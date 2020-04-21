import time
import threading
import sudoku.events.solver as events
import sudoku.solution.solver as solver


class SolverStore:

  def __init__(self, event_bus):
    self._event_bus = event_bus
    self._solver = None
    self._solution_in_progress = False
    self._thread = None

  @property
  def solution_in_progress(self):
    return self._solution_in_progress

  def solve(self, store):
    self._solver = solver.SudokuSolverFactory.build(store, step_timeout=0.1)
    self._solution_in_progress = True
    self._event_bus.emit(events.SolutionStartedEvent())

    try:
      self._solver.solve()
    except solver.AlgorithmStoppedException:
      pass
    
    self._solution_in_progress = False
    store.clear_all_highlights()
    store.clear_all_highlights2()
    self._event_bus.emit(events.SolutionFinishedEvent())

  def solve_in_thread(self, store):
    if self._thread is not None:
      self.stop_thread()
    self._thread = threading.Thread(target = lambda: self.solve(store))
    self._thread.start()

  def stop_thread(self):
    if self._solver is not None:
      self._solver.stop()
    if self._thread is not None:
      self._thread.join()
      self._thread = None
