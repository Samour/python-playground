import tkinter as tk
import events
import store.board


class Controls(tk.Frame, events.EventListenerSync):

  def __init__(self, master, board_store):
    super().__init__(master)
    self._store = board_store
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

    self._mode_btn = tk.Button(self, text = self._get_mode_btn_text(), command = self._change_mode())
    self._mode_btn.pack(side = tk.LEFT)
    self._reset_btn = tk.Button(self, text = 'Reset', command = self._reset_game)
    self._reset_btn.pack(side = tk.LEFT)
    self._clear_btn = tk.Button(self, text = 'Clear', command = self._clear_board)
    self._clear_btn.pack(side = tk.LEFT)

  def _get_mode_btn_text(self):
    if self._store.game_mode is store.board.GameMode.SOLVE:
      return 'Construct puzzle'
    else:
      return 'Solve puzzle'

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
