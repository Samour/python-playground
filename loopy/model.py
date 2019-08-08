class Vertex:

  def __init__(self, x, y):
    self.x = x
    self.y = y


class Line:

  STATE_UNKNOWN = 'UNKNOWN'
  STATE_PRESENT = 'PRESENT'
  STATE_ABSENT = 'ABSENT'

  def __init__(self, v1, v2):
    self.v1 = v1
    self.v2 = v2
    self.state = self.STATE_UNKNOWN


class LineCount:

  def __init__(self, vertex, value):
    self.vertex = vertex
    self.value = value


class Puzzle:

  MODEL_GRID = 'GRID'

  def __init__(self, model = None, size = None):
    self.model = model
    self.size = size
    self.lines = []
    self.line_counts = []


class Configuration:

  def __init__(self):
    self.size = [6, 6]
    self.model = Puzzle.MODEL_GRID

  def clone(self):
    clone = Configuration()
    clone.size = type(self.size)(self.size)
    clone.model = self.model

    return clone
