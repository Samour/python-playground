import struct


MAX_FIELDS = 255
SHORT_SIZE = 0x02
INT32_SIZE = 0x04
INT64_SIZE = 0x08
FLOAT_SIZE = 0x04
DOUBLE_SIZE = 0x08
PACK_SHORT = '!h'
PACK_INT32 = '!i'
PACK_INT64 = '!l'
PACK_FLOAT = '!f'
PACK_DOBULE = '!d'
MAX_CONDENSED_TAG = 15
UNCONDENSED_MASK = 0x88
STR_ENCODING = 'utf-8'
CODE_NULL = 0x00


def n_next(b_iter, c):
  b = []
  for i in range(c):
    b.append(next(b_iter))
  return bytes(b)


class FieldType:

  def default(self):
    pass

  def valid(self, data):
    pass

  def print_value(self, data, pad_in=0, pad_size=2):
    pass

  def serialise_value(self, data):
    pass

  def deserialise_value(self, data):
    pass


class String(FieldType):

  def default(self):
    return ''

  def valid(self, data):
    return isinstance(data, str)

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    esc_str = []
    for c in data:
      if c == '"':
        esc_str.append('\\')
      esc_str.append(c)
    
    return '"{}"'.format(''.join(esc_str))

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return list(data.encode(STR_ENCODING)) + [CODE_NULL]

  def deserialise_value(self, b_iter):
    chars = []
    c = next(b_iter)
    while c != CODE_NULL:
      chars.append(c)
      c = next(b_iter)
    return bytes(chars).decode(STR_ENCODING)


class Boolean(FieldType):
  
  def default(self):
    return False

  def valid(self, data):
    return isinstance(data, bool)
  
  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    return str(data)

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return [0x01] if data else [0x00]

  def deserialise_value(self, b_iter):
    return next(b_iter) == 0x01


class Int32(FieldType):

  def default(self):
    return 0

  def valid(self, data):
    return isinstance(data, int) and data <= MAX_INT32 and data >= MIN_INT32

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    return 'Int32( {} )'.format(data)

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return list(struct.pack(PACK_INT32, data))

  def deserialise_value(self, b_iter):
    return struct.unpack(PACK_INT32, n_next(b_iter, INT32_SIZE))[0]


class Int64(FieldType):

  def default(self):
    return 0

  def valid(self, data):
    return isinstance(data, int) and data <= MAX_INT64 and data >= MIN_INT64

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    return 'Int64( {} )'.format(data)

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return list(struct.pack(PACK_INT64, data))

  def deserialise_value(self, b_iter):
    return struct.unpack(PACK_INT64, n_next(b_iter, INT64_SIZE))[0]


class Float(FieldType):

  def default(self):
    return 0.0

  def valid(self, data):
    return isinstance(data, float)

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    return 'Float( {} )'.format(data)
  
  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return list(struct.pack(PACK_FLOAT, data))

  def deserialise_value(self, b_iter):
    return struct.unpack(PACK_FLOAT, n_next(b_iter, FLOAT_SIZE))[0]


class Double(FieldType):

  def default(self):
    return 0.0

  def valid(self, data):
    return isinstance(data, float)

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    return 'Double( {} )'.format(data)
  
  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    return list(struct.pack(PACK_DOBULE, data))

  def deserialise_value(self, b_iter):
    return struct.unpack(PACK_DOBULE, n_next(b_iter, DOUBLE_SIZE))[0]


class List(FieldType):

  def __init__(self, element_type):
    self.element_type = element_type

  def default(self):
    return []

  def valid(self, data):
    if not isinstance(data, list):
      return False
    for e in data:
      if not self.element_type.valid(e):
        return False
    return True

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    elements = []
    for e in data:
      elements.append(self.element_type.print_value(e, pad_in=pad_in+pad_size, pad_size=pad_size))
    if len(elements) == 0:
      return '[]'
    elif len(elements) == 1:
      return '[ {} ]'.format(''.join(elements))
    else:
      pad_str = ' ' * (pad_in + pad_size)
      return '[\n{}{}\n{}]'.format(pad_str, ',\n{}'.format(pad_str).join(elements), ' ' * pad_in)

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    arr = list(struct.pack(PACK_SHORT, len(data)))
    for i in data:
      arr.extend(self.element_type.serialise_value(i))
    return arr

  def deserialise_value(self, b_iter):
    arr_len = struct.unpack(PACK_SHORT, n_next(b_iter, SHORT_SIZE))[0]
    arr = []
    for i in range(arr_len):
      arr.append(self.element_type.deserialise_value(b_iter))
    
    return arr


class Field:

  def __init__(self, name, tag, f_type):
    self.name = name
    self.tag = tag
    self.type = f_type


class StructObject:

  def __init__(self, struct):
    self._struct = struct
    for field in struct.fields:
      setattr(self, field.name, field.type.default())

  def __setattr__(self, name, value):
    if hasattr(self, '_struct'):
      field = [ f for f in self._struct.fields if f.name == name ]
      if len(field) > 0 and not field[0].type.valid(value):
        raise TypeError('{} {} cannot be represented with {}'.format(
          type(value).__name__,
          value,
          type(field[0].type).__name__
        ))

    super().__setattr__(name, value)

  def __str__(self):
    return self._struct.print_value(self)


class Struct(FieldType):

  def __init__(self, fields):
    self.fields = fields

  def default(self):
    return None

  def valid(self, data):
    if len(self.fields) > MAX_FIELDS:
      return False
    if data is None:
      return True
    if not isinstance(data, StructObject) or data._struct != self:
      return False
    for field in self.fields:
      if not hasattr(data, field.name) or not field.type.valid(getattr(data, field.name)):
        return False
    return True

  def print_value(self, data, pad_in=0, pad_size=2):
    if not self.valid(data):
      raise TypeError()
    if data is None:
      return 'None'
    elements = []
    for field in self.fields:
      elements.append('{}: {}'.format(
        field.name,
        field.type.print_value(getattr(data, field.name), pad_in=pad_in+pad_size, pad_size=pad_size)
      ))
    if len(elements) == 0:
      return '{}'
    else:
      pad_str = ' ' * (pad_in + pad_size)
      return '{}\n{}{}\n{}{}'.format('{', pad_str, ',\n{}'.format(pad_str).join(elements), ' ' * pad_in, '}')

  def serialise_value(self, data):
    if not self.valid(data):
      raise TypeError()
    if data is None:
      return b''
    b = []
    # Append tags
    fields = [ f for f in self.fields if getattr(data, f.name) is not f.type.default() ]
    fields.sort(key=lambda f: f.tag)
    b.append(len(fields))
    make_tag = []
    for f in fields:
      b.append(f.tag - 1)
    # Append values
    for f in fields:
      b.extend(f.type.serialise_value(getattr(data, f.name)))
    
    return b

  def serialise(self, data):
    return bytes(self.serialise_value(data))

  def deserialise_value(self, b_iter):
    data = self.create()
    field_map = { f.tag: f for f in self.fields }
    field_count = int(next(b_iter))
    field_tags = list(n_next(b_iter, field_count))
    
    for tag in field_tags:
      field = field_map[tag + 1]
      setattr(data, field.name, field.type.deserialise_value(b_iter))

    return data

  def deserialise(self, data):
    return self.deserialise_value(iter(data))

  def create(self):
    return StructObject(self)
