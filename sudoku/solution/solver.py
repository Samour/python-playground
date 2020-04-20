import time
import sudoku.solution.analyser as analyser


class AlgorithmStoppedException(Exception):
  pass


class SudokuSolver:

  def __init__(self, store, analyser, **kwargs):
    self._store = store
    self._analyser = analyser
    self._step_timeout = kwargs.get('step_timeout', 0)
    self._break_soln = False
    self._current_highlight = None

  def stop(self):
    self._break_soln = True

  def solve(self):
    self._break_soln = False

    # Clear any cells that are currently highlighted
    for y in range(9):
      for x in range(9):
        if self._store.get_cell(x, y).highlight:
          self._store.set_cell_highlight(x, y, False)

    # Populate initial state
    for y in range(9):
      for x in range(9):
        cell = self._store.get_cell(x, y)
        if cell.value is not None:
          continue

        adjacent_values = {
          v for v in (self._store.get_cell(*i).value for i in self._analyser.adjacent_cells(x, y)) if v is not None
        }
        for i in self._cell_all_values().difference(adjacent_values):
          self._add_cell_possible(x, y, i)
        self._set_if_only_remaining(x, y)

    self._set_determinable()

  def _set_determinable(self):
    made_change = True
    while made_change:
      made_change = False

      for cell_group in self._analyser.get_cell_sets():
        count = { i + 1: [] for i in range(9) }
        for x, y in cell_group:
          cell = self._store.get_cell(x, y)
          if cell.value is not None:
            continue
          # print(cell.possible)
          for value in cell.possible:
            count[value].append((x, y))

        for value in count:
          print(len(count[value]))
          if len(count[value]) != 1:
            continue
          self._set_cell_value(*count[value][0], value)
          made_change = True
        
  def _cell_all_values(self):
    return { i + 1 for i in range(9) }

  def _add_cell_possible(self, x, y, i):
    self._store.add_cell_possible(x, y, i)
    self._highlight_cell(x, y)
    self._do_sleep()

  def _remove_cell_possible(self, x, y, i):
    self._store.remove_cell_possible(x, y, i)
    self._highlight_cell(x, y)
    self._do_sleep()

  def _set_if_only_remaining(self, x, y):
    cell = self._store.get_cell(x, y)
    if len(cell.possible) == 1:
      self._set_cell_value(x, y, list(cell.possible)[0])

  def _set_cell_value(self, x, y, value):
    self._store.set_cell_value(x, y, value)
    self._highlight_cell(x, y)
    self._do_sleep()
    self._clear_adjacent_possible(x, y, value)

  def _clear_adjacent_possible(self, x, y, value):
    for i, j in self._analyser.adjacent_cells(x, y):
      cell = self._store.get_cell(i, j)
      if cell.value is not None or value not in cell.possible:
        continue

      self._remove_cell_possible(i, j, value)
      self._set_if_only_remaining(i, j)

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
