import tkinter as tk
import events
import store.board
import store.puzzles
import store.solver
import solution.validator as validator
import view.eventlistener
import view.controls
import view.canvas


LOG_EVENTS = False


class LoggingEventListener(events.EventListenerSync):

  def receive(self, event):
    print('{} received event {}'.format(type(self).__name__, type(event).__name__))
    print('\t{}'.format(event))


class Application(tk.Frame):

  _EVENT_LOOP_TIMEOUT = 1

  _APPLICATION_PAD = 10

  def __init__(self, master):
    super().__init__(master)
    self._event_bus = None
    self._event_listener = None
    self._board_store = None
    self._solver_store = None
    self._validator = None
    self._controls = None
    self._board_canvas = None

    self.pack(padx = self._APPLICATION_PAD, pady = self._APPLICATION_PAD)
    self.post_construct()

  def post_construct(self):
    self._event_bus = events.EventBus()
    if LOG_EVENTS:
      LoggingEventListener().register_bus(self._event_bus)
    self._event_listener = view.eventlistener.ApplicationEventListener(self)
    self._event_listener.register_bus(self._event_bus)
    self._board_store = store.board.BoardStore(self._event_bus)
    self._solver_store = store.solver.SolverStore(self._event_bus)
    
    self._event_listener.start(self._EVENT_LOOP_TIMEOUT)
    
    self._validator = validator.SolutionValidatorBuilder.solution_validator(self._board_store)
    self._render_widgets()
    # self._board_store.reset_board(7, 7)
    store.puzzles.PuzzleLoader.load_puzzle(self._board_store, store.puzzles.PuzzleLoader.EASY_10x10)

  def _render_widgets(self):
    self._controls = view.controls.Controls(self, self._board_store, self._solver_store, self._validator)
    self._controls.pack()
    self._controls.register_bus(self._event_listener)
    self._controls.init()

    self._board_canvas = view.canvas.BoardCanvas(self, self._board_store, self._solver_store)
    self._board_canvas.pack()
    self._board_canvas.register_bus(self._event_listener)

  def destroy(self):
    self._solver_store.stop_thread()
    self._event_listener.stop()
    super().destroy()


def main():
  root = tk.Tk()
  app = Application(master = root)
  root.mainloop()
