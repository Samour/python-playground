import sudoku.events.sudoku as events


class CellDeserialiserIterator:

  def __init__(self, elements):
    self._source = iter(elements)
    self._x = 0
    self._y = 0

  def __next__(self):
    el = next(self._source)
    value, fixed, possible = el.split(PuzzleSerialisation.FIELD_DELIM)
    cell = SudokuCell()
    try:
      cell.value = int(value)
    except:
      pass
    cell.fixed = fixed == '1'
    cell.possible = { int(i) for i in possible.split(PuzzleSerialisation.ARR_DELIM) if len(i) > 0 }

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
    return CellDeserialiserIterator(self._source.split(PuzzleSerialisation.CELL_DELIM))


class PuzzleSerialisation:

  CELL_DELIM = ']'
  FIELD_DELIM = ';'
  ARR_DELIM = ','

  @staticmethod
  def serialise(store):
    elements = []
    for x in range(9):
      for y in range(9):
        elements.append(
          PuzzleSerialisation._serialise_cell(
            store.get_cell(x, y)
          )
        )

    return PuzzleSerialisation.CELL_DELIM.join(elements)

  @staticmethod
  def _serialise_cell(cell):
    return PuzzleSerialisation.FIELD_DELIM.join([
      str(cell.value) if cell.value is not None else '',
      '1' if cell.fixed else '0',
      PuzzleSerialisation.ARR_DELIM.join([ str(i) for i in cell.possible ])
    ])

  @staticmethod
  def deserialise(string):
    return CellDeserialiserIterable(string)


class SudokuCell:

  def __init__(self):
    self.value = None
    self.fixed = False
    self.highlight = False
    self.possible = set()

  def copy(self):
    cell = SudokuCell()
    cell.value = self.value
    cell.fixed = self.fixed
    cell.highlight = self.highlight
    cell.possible = set(self.possible)
    
    return cell

  def __eq__(self, o):
    return self.value == o.value and self.fixed == o.fixed and self.highlight == o.highlight\
      and self.possible == o.possible

  def __str__(self):
    return '(value = {}, fixed = {}, highlight = {}, possible = {})'.format(
      self.value,
      self.fixed,
      self.highlight,
      self.possible
    )

class SudokuStore:

  MODE_VALUE = 'VALUE'
  MODE_NOTE = 'NOTE'

  def __init__(self, event_bus):
    self._event_bus = event_bus
    self._mode = SudokuStore.MODE_VALUE
    self._board = [
      [ SudokuCell() for i in range(9) ] for j in range(9)
    ]
    self._update_history = []
    self._undo_head = None

  @property
  def mode(self):
    return self._mode
  
  def set_mode(self, mode):
    self._mode = mode
    self._event_bus.emit(events.ModeChangedEvent(mode))

  def get_cell(self, x, y):
    return self._board[x][y].copy()

  def set_cell_value(self, x, y, value):
    cell = self._board[x][y].copy()
    cell.value = value
    self._update_cell(x, y, cell, True)

  def set_cell_fixed(self, x, y, fixed):
    cell = self._board[x][y].copy()
    cell.fixed = fixed
    self._update_cell(x, y, cell, True)

  def set_cell_highlight(self, x, y, highlight):
    cell = self._board[x][y].copy()
    cell.highlight = highlight
    self._update_cell(x, y, cell, False)

  def add_cell_possible(self, x, y, value):
    cell = self._board[x][y].copy()
    cell.possible.add(value)
    self._update_cell(x, y, cell, True)

  def remove_cell_possible(self, x, y, value):
    cell = self._board[x][y].copy()
    cell.possible.remove(value)
    self._update_cell(x, y, cell, True)

  def _update_cell(self, x, y, update, undoable):
    cell = self._board[x][y]
    if cell == update:
      return
    
    if undoable:
      if self._undo_head is not None:
        self._update_history = self._update_history[:self._undo_head]
        self._undo_head = None
      self._update_history.append((x, y, cell.copy(), update.copy()))
    self._board[x][y] = update
    self._event_bus.emit(events.SudokuCellUpdatedEvent(x, y, update.copy()))

  def clear_all(self):
    for x in range(9):
      for y in range(9):
        self._clear_cell(x, y)
    self._clear_history()

  def reset_solution(self):
    for x in range(9):
      for y in range(9):
        if not self._board[x][y].fixed:
          self._clear_cell(x, y)
    self._clear_history()

  def _clear_cell(self, x, y):
    cell = self._board[x][y]
    update = SudokuCell()
    update.highlight = cell.highlight
    self._update_cell(x, y, update, False)
  
  def save(self, fh):
    fh.write(PuzzleSerialisation.serialise(self))

  def load(self, fh):
    for x, y, cell in PuzzleSerialisation.deserialise(fh.read()):
      self._update_cell(x, y, cell, False)
    self._clear_history()

  def _clear_history(self):
    self._update_history = []
    self._undo_head = None

  def undo(self):
    if self._undo_head is None:
      self._undo_head = len(self._update_history)
    self._undo_head -= 1
    x, y, before, after = self._update_history[self._undo_head]
    self._apply_past_state(x, y, before)

  def redo(self):
    if self._undo_head is None or self._undo_head >= len(self._update_history):
      return
    
    x, y, before, after = self._update_history[self._undo_head]
    self._undo_head += 1
    self._apply_past_state(x, y, after)

  def _apply_past_state(self, x, y, state):
    cell = self._board[x][y].copy()
    cell.value = state.value
    cell.fixed = state.fixed
    cell.possible = set(state.possible)
    self._update_cell(x, y, cell, False)
