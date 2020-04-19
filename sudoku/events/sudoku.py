import events.bus as events


class SudokuCellUpdatedEvent(events.IEvent):

  def __init__(self, x, y, cell):
    self.x = x
    self.y = y
    self.cell = cell

  def __str__(self):
    return '{}(x = {}, y = {}, cell = {})'.format(type(self).__name__, self.x, self.y, self.cell)


class ModeChangedEvent(events.IEvent):

  def __init__(self, mode):
    self.mode = mode

  def __str__(self):
    return '{}(mode = {})'.format(type(self).__name__, self.mode)
