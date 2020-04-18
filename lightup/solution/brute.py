import time
import solution.solver
import solution.validator
import store.board as board


class CellBackTrack:

  def __init__(self, store):
    self._store = store
    self._cells = []
    self._guesses = []

  def set_cell_state(self, x, y, state, guess):
    self._cells.append((x, y))
    if guess:
      self._guesses.append((x, y))
    self._store.set_cell_state(x, y, state)

  def rewind_last_guess(self):
    if len(self._guesses) == 0:
      return None

    last_guess = self._guesses.pop()
    rewind = None
    while last_guess != rewind:
      rewind = self._cells.pop()
      self._store.set_cell_state(rewind[0], rewind[1], board.CellState.EMPTY)
    
    return last_guess


class BruteForceSolver(solution.solver.ISolverAsync):

  def __init__(self, step_timeout=0):
    self._step_timeout = step_timeout
    self._break_soln = False
  
  def solve(self, store):
    cell_validator = solution.validator.SolutionValidatorBuilder.solver_validator(store)
    solution_validator = solution.validator.SolutionValidatorBuilder.solution_validator(store)
    back_track = CellBackTrack(store)
    next_guess = 0, 0
    while True:
      if self._break_soln:
        self._break_soln = False
        return

      self._fill_stack(store, cell_validator, back_track, next_guess[0], next_guess[1])
      if len(solution_validator.validate()) == 0:
        return # Solution found

      last_guess = self._backtrack(store, cell_validator, back_track)
      if last_guess is None:
        return # No solution
      next_guess = last_guess[0] + 1, last_guess[1]

  def _fill_stack(self, store, validator, back_track, x, y):
    x, y = self._populate_determined(store, validator, back_track) or (x, y)
    next_cell = self._next_empty_cell(store, validator, x, y)
    while next_cell is not None:
      if self._break_soln:
        return

      back_track.set_cell_state(next_cell[0], next_cell[1], board.CellState.LIGHT, True)

      self._do_sleep()

      next_cell = self._populate_determined(store, validator, back_track) or next_cell
      next_cell = self._next_empty_cell(store, validator, next_cell[0] + 1, next_cell[1])
  
  def _backtrack(self, store, validator, back_track):
    last_guess = back_track.rewind_last_guess()
    if last_guess is None:
      return
    
    cell = store.get_cell(*last_guess)
    validation_errors = validator.placement_legal(
      last_guess[0], last_guess[1],
      board.CellState(board.CellState.CROSS, cell.lit, cell.count)
    )
    if self._count_illegal(validation_errors) > 0:
      return self._backtrack(store, validator, back_track)
    else:
      back_track.set_cell_state(last_guess[0], last_guess[1], board.CellState.CROSS, False)
      return last_guess

  def _do_sleep(self):
    if self._step_timeout > 0:
      time.sleep(self._step_timeout)

  def _populate_determined(self, store, validator, back_track):
    pass

  def _next_empty_cell(self, store, validator, x, y):
    for i in range(y, store.dims[1]):
      for j in range(x if i == y else 0, store.dims[1]):
        cell = store.get_cell(j, i)
        if cell.state is not board.CellState.EMPTY or cell.lit:
          continue
        validation_errors = validator.placement_legal(
          j, i,
          board.CellState(board.CellState.LIGHT, cell.lit, cell.count)
        )
        if self._count_illegal(validation_errors) == 0:
          return j, i
    
    return None
  
  def _count_illegal(self, validation):
    return len([
      e for e in validation if e.mode is solution.validator.RuleViolated.ILLEGAL
    ])

  def count_solutions(self, store):
    pass

  def stop(self):
    self._break_soln = True
