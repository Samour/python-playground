import schemabuf.schema.model as model


class StructBuilder:

  def __init__(self):
    self._fields = []

  def field(self, name, tag, f_type):
    if isinstance(f_type, type) and issubclass(f_type, model.FieldType):
      f_type = f_type()
    elif not isinstance(f_type, model.FieldType):
      raise TypeError()
    self._fields.append(model.Field(name, tag, f_type))

    return self

  def build(self):
    return model.Struct(self._fields)
