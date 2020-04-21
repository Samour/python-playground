import time
import algorithm.backtrack as backtrack
import sudoku.solution.analyser as analyser


class AlgorithmStoppedException(Exception):
  pass


class IllegalBoardStateException(Exception):
  pass


class CellMutation:

  TYPE_VALUE = 'VALUE'
  TYPE_POSSIBLE = 'POSSIBLE'

  def __init__(self, x, y, value, m_type, prior_solved_cells=None):
    self.x = x
    self.y = y
    self.value = value
    self.prior_solved_cells = prior_solved_cells
    self.type = m_type

def __eq__(self, o):
  return self.x == o.x and self.y == o.y and self.value == o.value and self.type == o.type\
    and self.prior_solved_cells == o.prior_solved_cells


class BackTrackMutationManager(backtrack.IReversableStore):

  def __init__(self, store):
    self._store = store

  def apply_update(self, update):
    if update.type is CellMutation.TYPE_VALUE:
      self._store.set_cell_value(update.x, update.y, update.value)
    else:
      self._store.remove_cell_possible(update.x, update.y, update.value)

  def reverse_update(self, update):
    if update.type is CellMutation.TYPE_VALUE:
      self._store.set_cell_value(update.x, update.y, None)
    else:
      self._store.add_cell_possible(update.x, update.y, update.value)


class SudokuSolver:

  def __init__(self, store, analyser, **kwargs):
    self._store = store
    self._analyser = analyser
    self._step_timeout = kwargs.get('step_timeout', 0)
    self._back_track = backtrack.BackTrack(BackTrackMutationManager(store))
    self._break_soln = False
    self._current_highlight = None
    self._cells_solved = 0

  def stop(self):
    self._break_soln = True

  def solve(self):
    self._break_soln = False
    self._cells_solved = 0

    # Populate initial state
    for y in range(9):
      for x in range(9):
        cell = self._store.get_cell(x, y)
        if cell.value is not None:
          self._cells_solved += 1
          continue

        adjacent_values = {
          v for v in (self._store.get_cell(*i).value for i in self._analyser.adjacent_cells(x, y)) if v is not None
        }
        for i in self._cell_all_values().difference(adjacent_values):
          self._add_cell_possible(x, y, i)
        self._set_if_only_remaining(x, y)

    self._set_determinable()
    last_bad_guess = None
    while self._cells_solved < 81:
      try:
        if last_bad_guess is not None:
          self._remove_cell_possible(last_bad_guess.x, last_bad_guess.y, last_bad_guess.value)
          self._cells_solved = last_bad_guess.prior_solved_cells
          self._store.set_cell_highlight2(last_bad_guess.x, last_bad_guess.y, False)
          last_bad_guess = None
          self._do_sleep()
        else:
          self._make_guess()
        self._set_determinable()
      except IllegalBoardStateException:
        last_bad_guess = self._back_track.rollback_guess()

  def _set_determinable(self):
    made_change = True
    while made_change:
      made_change = False

      for y in range(9):
        for x in range(9):
          cell = self._store.get_cell(x, y)
          if cell.value is not None or len(cell.possible) > 1:
            continue
          self._set_cell_value(x, y, list(cell.possible)[0], False)
          made_change = True

      if made_change:
        continue

      for cell_group in self._analyser.get_cell_sets():
        count = { i + 1: [] for i in range(9) }
        for x, y in cell_group:
          cell = self._store.get_cell(x, y)
          if cell.value is not None:
            continue
          for value in cell.possible:
            count[value].append((x, y))

        for value in count:
          if len(count[value]) != 1:
            continue
          self._set_cell_value(*count[value][0], value, False)
          made_change = True

  def _make_guess(self):
    guess_cell = None
    for y in range(9):
      for x in range(9):
        cell = self._store.get_cell(x, y)
        if cell.value is not None:
          continue
        if guess_cell is None or len(guess_cell[2]) > len(cell.possible):
          guess_cell = x, y, cell.possible
    
    x, y, possible = guess_cell
    self._store.set_cell_highlight2(x, y, True)
    self._set_cell_value(x, y, list(possible)[0], True)
        
  def _cell_all_values(self):
    return { i + 1 for i in range(9) }

  def _add_cell_possible(self, x, y, i):
    self._store.add_cell_possible(x, y, i)
    self._highlight_cell(x, y)
    self._do_sleep()

  def _remove_cell_possible(self, x, y, i):
    self._back_track.update(CellMutation(x, y, i, CellMutation.TYPE_POSSIBLE), False)
    self._highlight_cell(x, y)
    self._do_sleep()
    if len(self._store.get_cell(x, y).possible) == 0:
      raise IllegalBoardStateException()

  def _set_if_only_remaining(self, x, y):
    cell = self._store.get_cell(x, y)
    if len(cell.possible) == 1:
      self._set_cell_value(x, y, list(cell.possible)[0], False)

  def _set_cell_value(self, x, y, value, guess):
    self._back_track.update(CellMutation(x, y, value, CellMutation.TYPE_VALUE, self._cells_solved), guess)
    self._cells_solved += 1
    self._highlight_cell(x, y)
    self._do_sleep()
    self._clear_adjacent_possible(x, y, value)

  def _clear_adjacent_possible(self, x, y, value):
    for i, j in self._analyser.adjacent_cells(x, y):
      cell = self._store.get_cell(i, j)
      if cell.value is not None or value not in cell.possible:
        continue

      self._remove_cell_possible(i, j, value)

  def _highlight_cell(self, x, y):
    if self._current_highlight is not None:
      self._store.set_cell_highlight(*self._current_highlight, False)
    self._current_highlight = x, y
    self._store.set_cell_highlight(x, y, True)
  
  def _do_sleep(self):
    if self._step_timeout > 0:
      time.sleep(self._step_timeout)
    if self._break_soln:
      raise AlgorithmStoppedException()


class SudokuSolverFactory:

  @staticmethod
  def build(store, **kwargs):
    return SudokuSolver(
      store,
      analyser.UnionCellAnalyser([
        analyser.HorizontalCellAnalyser(),
        analyser.VerticalCellAnalyser(),
        analyser.SquareCellAnalyser()
      ]),
      **kwargs
    )
