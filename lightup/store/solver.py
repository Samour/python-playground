import time
import threading
import events
import solution.brute


class SolverStartedEvent(events.IEvent):
  pass


class SolverFinishedEvent(events.IEvent):
  pass


class SolverStore:

  def __init__(self, event_bus):
    self._event_bus = event_bus
    self._solver = solution.brute.BruteForceSolver(0.001)
    self._solver_thread = None
    self._solution_in_progress = False

  @property
  def solution_in_progress(self):
    return self._solution_in_progress

  def solve(self, store):
    if self._solution_in_progress:
      return

    self._solution_in_progress = True
    self._event_bus.emit(SolverStartedEvent())
    self._solver.solve(store)
    self._solution_in_progress = False
    self._event_bus.emit(SolverFinishedEvent())

  def solve_in_thread(self, store):
    if self._solver_thread is not None:
      raise Exception('A solver thread already exists')
    
    self._solver_thread = threading.Thread(target = lambda: self.solve(store))
    self._solver_thread.start()
  
  def thread_join(self):
    if self._solver_thread is None:
      return

    self._solver_thread.join()
    self._solver_thread = None

  def stop_thread(self):
    if self._solution_in_progress:
      self._solver.stop()
      self.thread_join()
