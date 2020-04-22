class SerialisationFilter:

  def pre_serialise(self, data):
    return data

  def post_serialise(self, data):
    return data

  def pre_deserialise(self, data):
    return data

  def post_deserialise(self, data):
    return data


class Serialiser:

  def __init__(self, filters):
    self._filters = filters

  def serialise(self, s_type, data):
    for f in self._filters:
      data = f.pre_serialise(data)
    data = s_type.serialise(data)
    for f in self._filters:
      data = f.post_serialise(data)
    
    return data

  def deserialise(self, s_type, data):
    for f in self._filters[::-1]:
      data = f.pre_deserialise(data)
    data = s_type.deserialise(data)
    for f in self._filters[::-1]:
      data = f.post_deserialise(data)

    return data


class CompressionSerialisationFilter(SerialisationFilter):

  def __init__(self, compress_bytes, decompress_bytes):
    self.compress_bytes = compress_bytes
    self.decompress_bytes = decompress_bytes

  def post_serialise(self, data):
    return self.compress_bytes(data)

  def pre_deserialise(self, data):
    return self.decompress_bytes(data)
