import tkinter as tk
import events.bus as events
import events.tkinter as tkevents
import sudoku.store.board as board
import sudoku.store.solver as solver
import sudoku.view.controls as controls
import sudoku.view.canvas as canvas


LOG_EVENTS = False


class LoggingEventListener(events.EventListenerSync):

  def receive(self, event):
    print(event)


class Application(tk.Frame):

  def __init__(self, master):
    super().__init__(master)
    self._event_bus = None
    self._event_bridge = None
    self._store = None
    self._solver_store = None
    self._controls = None
    self._canvas = None

  def init(self):
    self._event_bus = events.EventBus()
    self._event_bridge = tkevents.ApplicationEventBridge(self)
    self._event_bridge.subscribe(self._event_bus)
    self._store = board.SudokuStore(self._event_bus)
    self._solver_store = solver.SolverStore(self._event_bus)
    if LOG_EVENTS:
      LoggingEventListener().subscribe(self._event_bus)

    self._controls = controls.Controls(self, self._store, self._solver_store)
    self._controls.subscribe(self._event_bridge)
    self._controls.pack()
    self._canvas = canvas.GameCanvas(self, self._store, self._solver_store)
    self._canvas.subscribe(self._event_bridge)
    self._canvas.pack()
    self.pack(pady = 10)

    self._event_bridge.start(wait_timeout = 1)
    self._controls.init()
    self._canvas.init(self._event_bridge)

  def destroy(self):
    self._event_bridge.stop()
    self._solver_store.stop_thread()
    super().destroy()


def main():
  root = tk.Tk()
  app = Application(master = root)
  app.init()
  root.mainloop()
