import tkinter as tk
import events
import store.board
import store.solver
import solution.validator as validator


class BoardControls(tk.Frame, events.EventListenerSync):

  def __init__(self, master, board_store, solver_store):
    super().__init__(master)
    self._store = board_store
    self._solver_store = solver_store
    self._mode_btn = None
    self._reset_btn = None
    self._clear_btn = None

  def init(self):
    self._render_controls()

  def _render_controls(self):
    if self._mode_btn is not None:
      self._mode_btn.destroy()
    if self._reset_btn is not None:
      self._reset_btn.destroy()
    if self._clear_btn is not None:
      self._clear_btn.destroy()

    btn_state = tk.DISABLED if self._solver_store.solution_in_progress else tk.NORMAL
    self._mode_btn = tk.Button(self, text = self._get_mode_btn_text(), state = btn_state, command = self._change_mode())
    self._mode_btn.pack(side = tk.LEFT)
    self._reset_btn = tk.Button(self, text = 'Reset', state = btn_state, command = self._reset_game)
    self._reset_btn.pack(side = tk.LEFT)
    self._clear_btn = tk.Button(self, text = 'Clear', state = btn_state, command = self._clear_board)
    self._clear_btn.pack(side = tk.LEFT)

  def _get_mode_btn_text(self):
    if self._store.game_mode is store.board.GameMode.SOLVE:
      return 'Construct mode'
    else:
      return 'Solve mode'

  def _change_mode(self):
    game_mode = self._store.game_mode
    def command():
      if game_mode is store.board.GameMode.SOLVE:
        self._store.change_mode(store.board.GameMode.CONSTRUCT)
      else:
        self._store.change_mode(store.board.GameMode.SOLVE)

    return command

  def _reset_game(self):
    self._store.reset_game()

  def _clear_board(self):
    self._store.reset_board(*self._store.dims)

  def receive(self, event):
    if isinstance(event, store.board.GameModeUpdatedEvent):
      self._render_controls()
    elif isinstance(event, store.solver.SolverStartedEvent):
      self._render_controls()
    elif isinstance(event, store.solver.SolverFinishedEvent):
      self._render_controls()


class ValidationControl(tk.Frame, events.EventListenerSync):

  _SOLVED_COLOUR = 'green'
  _WARNING_COLOUR = 'orange'
  _ERROR_COLOUR = 'red'

  def __init__(self, master, solution_validator, board_store, solver_store):
    super().__init__(master)
    self._solution_validator = solution_validator
    self._board_store = board_store
    self._solver_store = solver_store
    self._btn_frame = None
    self._validate_btn = None
    self._solve_btn = None
    self._validation_msg = None

  def init(self):
    self._render_controls()

  def _render_controls(self):
    if self._btn_frame is not None:
      self._btn_frame.destroy()
    if self._validation_msg is not None:
      self._validation_msg.destroy()

    btn_state = tk.DISABLED if self._solver_store.solution_in_progress else tk.NORMAL
    self._btn_frame = tk.Frame(self)
    self._btn_frame.pack()
    self._validate_btn = tk.Button(self._btn_frame, text = 'Validate', state = btn_state, command = self._validate)
    self._validate_btn.pack(side = tk.LEFT)
    self._solve_btn = tk.Button(self._btn_frame, text = 'Solve', state = btn_state, command = self._solve)
    self._solve_btn.pack(side = tk.LEFT)
  
  def _validate(self):
    self._clear_validation_msg()

    validation_errors = self._solution_validator.validate()
    cell_not_lit_errors = [
      e for e in validation_errors if isinstance(e.rule, validator.CellNotLitRule)
    ]
    validation_illegal = [
      e for e in validation_errors if e.mode is validator.RuleViolated.ILLEGAL
    ]
    if len(validation_errors) == 0:
      self._validation_msg = tk.Label(self, text = 'Solved!', fg = self._SOLVED_COLOUR)
    elif len(cell_not_lit_errors) > 0 and len(validation_illegal) == 0:
      self._validation_msg = tk.Label(self, text = 'Some cells are still unlit', fg = self._WARNING_COLOUR)
    else:
      self._validation_msg = tk.Label(self, text = 'There are errors in the solution', fg = self._ERROR_COLOUR)
    self._validation_msg.pack()

  def _solve(self):
    self._solver_store.solve_in_thread(self._board_store)

  def receive(self, event):
    if isinstance(event, store.board.BoardResetEvent) or isinstance(event, store.board.GameResetEvent):
      self._clear_validation_msg()
    elif isinstance(event, store.solver.SolverStartedEvent):
      self._render_controls()
    elif isinstance(event, store.solver.SolverFinishedEvent):
      self._receive_solver_finished()
  
  def _clear_validation_msg(self):
    if self._validation_msg is not None:
      self._validation_msg.destroy()
  
  def _receive_solver_finished(self):
    self._solver_store.thread_join()
    self._render_controls()


class Controls(tk.Frame, events.ISubscriber):

  def __init__(self, master, board_store, solver_store, solution_validator):
    super().__init__(master)
    self._event_bus = None
    self._board_store = board_store
    self._solver_store = solver_store
    self._solution_validator = solution_validator
    self._board_controls = None
    self._validation_control = None

  def init(self):
    self._render_controls()
  
  def _render_controls(self):
    if self._board_controls is not None:
      self._board_controls.destroy()
    if self._validation_control is not None:
      self._validation_control.destroy()

    self._board_controls = BoardControls(self, self._board_store, self._solver_store)
    self._board_controls.pack()
    self._validation_control = ValidationControl(self, self._solution_validator, self._board_store, self._solver_store)
    self._validation_control.pack()
    if self._event_bus is not None:
      self._board_controls.register_bus(self._event_bus)
      self._validation_control.register_bus(self._event_bus)
    self._board_controls.init()
    self._validation_control.init()

  def register_bus(self, event_bus):
    self._event_bus = event_bus
    if self._board_controls is not None:
      self._board_controls.register_bus(event_bus)
    if self._validation_control is not None:
      self._validation_control.register_bus(event_bus)
