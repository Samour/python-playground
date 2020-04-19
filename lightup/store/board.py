import events


class GameModeUpdatedEvent(events.IEvent):

  def __init__(self, mode):
    self.mode = mode

  def __str__(self):
    return '(mode = {})'.format(self.mode)


class BoardResetEvent(events.IEvent):

  def __init__(self, x, y):
    self.x = x
    self.y = y

  def __str__(self):
    return '(x = {}, y = {})'.format(self.x, self.y)


class GameResetEvent(events.IEvent):
  pass


class CellStateUpdatedEvent(events.IEvent):

  def __init__(self, x, y, state):
    self.x = x
    self.y = y
    self.state = state

  def __str__(self):
    return '(x = {}, y = {}, state = {})'.format(self.x, self.y, self.state)


class CellState:

  EMPTY = 'EMPTY'
  WALL = 'WALL'
  LIGHT = 'LIGHT'
  CROSS = 'CROSS'

  def __init__(self, state, lit, count):
    self.state = state
    self.lit = lit
    self.count = count

  def __str__(self):
    return '(state = {}, lit = {}, count = {})'.format(self.state, self.lit, self.count)


class GameMode:

  CONSTRUCT = 'CONSTRUCT'
  SOLVE = 'SOLVE'


class LineOfSightIterator:

  def __init__(self, store, x, y):
    self._store = store
    self._x = x
    self._y = y
    self._dir = 0
    self._i = 0

  def __next__(self):
    self._increment_ptr()
    return (self._get_cell(), *self._get_coords())

  def _increment_ptr(self):
    self._i += 1
    if self._ptr_is_valid() and self._get_cell().state is not CellState.WALL:
      return

    self._i = 0
    self._dir += 1
    self._increment_ptr()

  def _get_coords(self):
    if self._dir == 0:
      return self._x + self._i, self._y
    elif self._dir == 1:
      return self._x - self._i, self._y
    elif self._dir == 2:
      return self._x, self._y + self._i
    elif self._dir == 3:
      return self._x, self._y - self._i
    else:
      raise StopIteration()
  
  def _ptr_is_valid(self):
    x, y = self._get_coords()
    return x >= 0 and x < self._store.dims[0] and y >= 0 and y < self._store.dims[1]

  def _get_cell(self):
    x, y = self._get_coords()
    return self._store.get_cell(*self._get_coords())


class _LineOfSightIterable:

  def __init__(self, store, x, y):
    self._store = store
    self._x = x
    self._y = y

  def __iter__(self):
    return LineOfSightIterator(self._store, self._x, self._y)


class BoardStore:

  def __init__(self, event_bus):
    self._event_bus = event_bus
    self._dims = (0, 0)
    self._board = []
    self._lit_by_matrix = []
    self._game_mode = GameMode.SOLVE

  @property
  def game_mode(self):
    return self._game_mode

  @property
  def dims(self):
    return self._dims

  def change_mode(self, mode):
    self._game_mode = mode
    self._event_bus.emit(GameModeUpdatedEvent(mode))

  def reset_board(self, x, y):
    self._dims = (x, y)
    self._board = self._generate_matrix(x, y, lambda: CellState(CellState.EMPTY, False, None))
    self._lit_by_matrix = self._generate_matrix(x, y, set)
    self._event_bus.emit(BoardResetEvent(x, y))

  def _generate_matrix(self, x, y, provider):
    return [
      [ provider() for i in range(y) ] for j in range(x)
    ]

  def reset_game(self):
    self._lit_by_matrix = self._generate_matrix(self._dims[0], self._dims[1], set)
    for x in range(self._dims[0]):
      for y in range(self._dims[1]):
        cell = self.get_cell(x, y)
        if cell.state is CellState.WALL:
          continue
        if cell.state is CellState.EMPTY and not cell.lit:
          continue
        
        cell_state = CellState(CellState.EMPTY, False, None)
        self._board[x][y] = cell_state
        self._event_bus.emit(CellStateUpdatedEvent(x, y, cell_state))
    
    self._event_bus.emit(GameResetEvent())

  def get_cell(self, x, y):
    return self._board[x][y]

  def line_of_sight(self, x, y):
    return _LineOfSightIterable(self, x, y)

  def set_cell_state(self, x, y, state):
    current_state = self.get_cell(x, y)
    if state is current_state.state:
      return

    cell_state = CellState(state, state is CellState.LIGHT or len(self._lit_by_matrix[x][y]) > 0, current_state.count)
    self._board[x][y] = cell_state
    self._event_bus.emit(CellStateUpdatedEvent(x, y, cell_state))

    if state is CellState.LIGHT or current_state.state is CellState.LIGHT:
      self._update_lit_matrix(x, y, state is CellState.LIGHT)

  def _update_lit(self, x, y, lit):
    current_state = self.get_cell(x, y)
    if current_state.lit is lit:
      return
    
    cell_state = CellState(current_state.state, lit, current_state.count)
    self._board[x][y] = cell_state
    self._event_bus.emit(CellStateUpdatedEvent(x, y, cell_state))

  def _update_lit_matrix(self, x, y, lit):
    for cell, i, j in self.line_of_sight(x, y):
      lit_by = self._lit_by_matrix[i][j]
      if lit:
        lit_by.add((x, y))
      else:
        lit_by.remove((x, y))
      self._update_lit(i, j, len(lit_by) > 0 or cell.state is CellState.LIGHT)

  def set_cell_count(self, x, y, count):
    current_state = self.get_cell(x, y)
    if current_state.count == count:
      return

    cell_state = CellState(current_state.state, current_state.lit, count)
    self._board[x][y] = cell_state
    self._event_bus.emit(CellStateUpdatedEvent(x, y, cell_state))
