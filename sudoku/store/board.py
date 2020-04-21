import sudoku.store.model as model
import sudoku.store.serialiser as serialiser
import sudoku.events.sudoku as events


class SudokuStore:

  MODE_VALUE = 'VALUE'
  MODE_NOTE = 'NOTE'

  def __init__(self, event_bus):
    self._event_bus = event_bus
    self._mode = SudokuStore.MODE_VALUE
    self._board = [
      [ model.SudokuCell() for i in range(9) ] for j in range(9)
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

  def clear_all_highlights(self):
    for x in range(9):
      for y in range(9):
        self.set_cell_highlight(x, y, False)

  def set_cell_highlight2(self, x, y, highlight2):
    cell = self._board[x][y].copy()
    cell.highlight2 = highlight2
    self._update_cell(x, y, cell, False)

  def clear_all_highlights2(self):
    for x in range(9):
      for y in range(9):
        self.set_cell_highlight2(x, y, False)

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
    update = model.SudokuCell()
    update.highlight = cell.highlight
    self._update_cell(x, y, update, False)
  
  def save(self, fh):
    fh.write(serialiser.PuzzleSerialisation.serialise(self))

  def load(self, fh):
    for x, y, cell in serialiser.PuzzleSerialisation.deserialise(fh.read()):
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
