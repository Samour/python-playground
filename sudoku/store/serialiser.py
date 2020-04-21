import sudoku.store.model as model


class CellDeserialiserIterator:

  def __init__(self, elements):
    self._source = iter(elements)
    self._x = 0
    self._y = 0

  def __next__(self):
    el = next(self._source)
    value, fixed, possible = el.split(PuzzleSerialisationV1.FIELD_DELIM)
    cell = model.SudokuCell()
    try:
      cell.value = int(value)
    except:
      pass
    cell.fixed = fixed == '1'
    cell.possible = { int(i) for i in possible.split(PuzzleSerialisationV1.ARR_DELIM) if len(i) > 0 }

    x = self._x
    y = self._y

    self._y += 1
    if self._y == 9:
      self._y = 0
      self._x += 1

    return x, y, cell


class CellDeserialiserIterable:

  def __init__(self, source):
    self._source = source

  def __iter__(self):
    return CellDeserialiserIterator(self._source.split(PuzzleSerialisationV1.CELL_DELIM))


class PuzzleSerialisationV1:

  CELL_DELIM = ']'
  FIELD_DELIM = ';'
  ARR_DELIM = ','

  @staticmethod
  def serialise(store):
    elements = []
    for x in range(9):
      for y in range(9):
        elements.append(
          PuzzleSerialisationV1._serialise_cell(
            store.get_cell(x, y)
          )
        )

    return PuzzleSerialisationV1.CELL_DELIM.join(elements).encode('utf-8')

  @staticmethod
  def _serialise_cell(cell):
    return PuzzleSerialisationV1.FIELD_DELIM.join([
      str(cell.value) if cell.value is not None else '',
      '1' if cell.fixed else '0',
      PuzzleSerialisationV1.ARR_DELIM.join([ str(i) for i in cell.possible ])
    ])

  @staticmethod
  def deserialise(data):
    return CellDeserialiserIterable(data.decode('utf-8'))


class V2CellDataIterator:

  def __init__(self, source):
    self._source = iter(source)
    self._x = 0
    self._y = 0

  def __next__(self):
    high_byte = next(self._source)
    low_byte = next(self._source)
    cell = model.SudokuCell()
    cell.fixed = high_byte & PuzzleSerialisationV2.FIXED_MASK != 0x0
    cell.value = (high_byte & PuzzleSerialisationV2.VALUE_MASK) >> PuzzleSerialisationV2.VALUE_OFFSET
    if cell.value == 0:
      cell.value = None
    possible_bitmap = high_byte & PuzzleSerialisationV2.POSSIBLE_HIGH_MASK
    possible_bitmap <<= PuzzleSerialisationV2.BYTE_SIZE
    possible_bitmap |= low_byte
    for i in range(9):
      if possible_bitmap & 0x1 << i != 0:
        cell.possible.add(i + 1)
    
    x, y = self._x, self._y
    self._y += 1
    if self._y >= 9:
      self._x += 1
      self._y = 0

    return x, y, cell


class V2CellDataIterable:

  def __init__(self, source):
    self._source = source

  def __iter__(self):
    return V2CellDataIterator(self._source)


class PuzzleSerialisationV2:

  # Structure:
  # Each cell is represented by 2 bytes, comprised of the following parts:
  # 0FVVVVVN NNNNNNNN
  # F indicates whether the cell is fixed. 0 = False, 1 = True
  # V-block is the value of the cell, or 0 if not specified
  # N-block is a bitmap representing cell possible values, with 1 being the lowest bit moving to 9 being the heighest
  
  FILE_HEADER = b'\x01<!SAMOURSUDOKU\x1f\x02>\x1d'
  FILE_FOOTER = b'\x04'
  BYTE_SIZE = 0x08
  BYTE_MASK = 0xff
  FIXED_OFFSET = 0x06
  FIXED_MASK = 0x40
  VALUE_OFFSET = 0x01
  VALUE_MASK = 0x3e
  POSSIBLE_HIGH_MASK = 0x1

  def serialise(store):
    byte_arr = []
    byte_arr.extend(PuzzleSerialisationV2.FILE_HEADER)
    for x in range(9):
      for y in range(9):
        byte_arr.extend(PuzzleSerialisationV2._serialise_cell(store.get_cell(x, y)))
    byte_arr.extend(PuzzleSerialisationV2.FILE_FOOTER)

    return bytes(byte_arr)

  def _serialise_cell(cell):
    possible_bitmap = 0x00
    for i in cell.possible:
      possible_bitmap |= 0x1 << (i - 1)
    value = cell.value if cell.value is not None else 0x0

    high_bit = possible_bitmap >> PuzzleSerialisationV2.BYTE_SIZE
    high_bit |= value << PuzzleSerialisationV2.VALUE_OFFSET
    high_bit |= (1 if cell.fixed else 0) << PuzzleSerialisationV2.FIXED_OFFSET
    low_bit = possible_bitmap & PuzzleSerialisationV2.BYTE_MASK

    return [high_bit, low_bit]

  def format_matches(data):
    file_header_len = len(PuzzleSerialisationV2.FILE_HEADER)
    return len(data) > file_header_len and data[:file_header_len] == PuzzleSerialisationV2.FILE_HEADER

  def deserialise(data):
    return V2CellDataIterable(data[len(PuzzleSerialisationV2.FILE_HEADER):-len(PuzzleSerialisationV2.FILE_FOOTER)])


class PuzzleSerialisation:

  @staticmethod
  def serialise(store):
    return PuzzleSerialisationV2.serialise(store)

  @staticmethod
  def deserialise(data):
    if PuzzleSerialisationV2.format_matches(data):
      return PuzzleSerialisationV2.deserialise(data)
    else:
      return PuzzleSerialisationV1.deserialise(data)
