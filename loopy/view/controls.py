import time
import threading
import tkinter as tk
import tkinter.filedialog
import solver


class GameControls(tk.Frame):

  def __init__(self, master = None):
    super().__init__(master)
    self.master = master
    self.step_pause_time = 0
    self._solve_thread = None
    self._stop_solve_thread = False
    self._solve_in_steps = False
    self._proceed_step = False
    self.create_widgets()

  def create_widgets(self):
    # First row
    self.frame_upper = tk.Frame(self)
    self.frame_upper.pack(pady = 5)
    self.load_game_btn = tk.Button(self.frame_upper, text = 'Load', command = self.load_game)
    self.load_game_btn.pack(side = 'left', padx = 10)
    self.save_game_btn = tk.Button(self.frame_upper, text = 'Save', command = self.save_game)
    self.save_game_btn.pack(side = 'left', padx = 10)
    self.reset_btn = tk.Button(self.frame_upper, text = 'Reset', command = self.reset_game)
    self.reset_btn.pack(side = 'left', padx = 10)
    self.configure_btn = tk.Button(self.frame_upper, text = 'Configure', command = self.master.open_configuration)
    self.configure_btn.pack(side = 'left', padx = 10)

    # Second row
    self.frame_lower = tk.Frame(self)
    self.frame_lower.pack(pady = 5)
    self.new_game_btn = tk.Button(self.frame_lower, text = 'New game', command = self.new_game)
    self.new_game_btn.pack(side = 'left', padx = 5)
    self.edit_btn = tk.Button(self.frame_lower, text = 'Edit', command = self.edit)
    self.edit_btn.pack(side = 'left', padx = 5)
    self.solve_btn = tk.Button(self.frame_lower, text = 'Solve', command = self.solve)
    self.solve_btn.pack(side = 'left', padx = 5)
    if self._solve_in_steps:
      self.step_btn = tk.Button(self.frame_lower, text = 'Step', command = self.step)
      self.step_btn.pack(side = 'left', padx = 5)
    self.validate_btn = tk.Button(self.frame_lower, text = 'Validate', command = self.validate_solution)
    self.validate_btn.pack(side = 'right')
    self.validate_lbl = tk.Label(self.frame_lower)
    self.validate_lbl.pack(side = 'right', padx = 20)

  def load_game(self):
    filename = tk.filedialog.askopenfilename()
    game = self.master.manager.load_game(filename)
    self.master.canvas.draw_new_game(game)

  def save_game(self):
    filename = tk.filedialog.asksaveasfilename()
    with open(filename, 'w') as fh:
      fh.write(self.master.manager.serializer.serialize(self.master.manager.game))

  def reset_game(self):
    if not self.master.lock_controls:
      self.master.manager.reset_game()
      self.master.canvas.redraw_game()

  def new_game(self):
    self.master.manager.new_game()
    self.master.canvas.draw_new_game(self.master.manager.game)

  def edit(self):
    if self.master.edit_mode:
      self.master.edit_mode = False
      self.master.canvas.clean_edit()
      self.edit_btn['text'] = 'Edit'
    else:
      self.master.edit_mode = True
      self.edit_btn['text'] = 'Play'

  def solve(self):
    if self.master.edit_mode:
      self.edit()
    if not self.master.lock_controls:
      if self._solve_thread is None:
        self.validate_lbl['text'] = 'Solving'
        self.solve_btn['text'] = 'Stop'
        self.master.lock_controls = True
        self._solve_thread = threading.Thread(target = self._solve_thread_ep)
        self._solve_thread.start()
    else:
      self.stop_alg()

  def step(self):
    self._proceed_step = True

  def stop_alg(self):
    self.solve_btn['text'] = 'Solve'
    self.validate_lbl['text'] = ''
    self._stop_solve_thread = True
    if self._solve_thread is not None:
      self._solve_thread.join()

  def _alg_step_cb(self, lines):
    while self._solve_in_steps and not self._proceed_step:
      if self._stop_solve_thread:
        raise InterruptedError()
    self._proceed_step = False
    if self._stop_solve_thread:
      raise InterruptedError()
    if self.step_pause_time > 0:
      for line in lines:
        self.master.canvas.draw_line(line, True)
      time.sleep(self.step_pause_time)

  def _solve_thread_ep(self):
    self._stop_solve_thread = False
    puzzle_solver = solver.PuzzleSolver(self.master.manager.game, step_callback = self._alg_step_cb)
    try:
      print(puzzle_solver.solve(True))
    except InterruptedError:
      pass
    self.master.canvas.redraw_game()
    self.master.lock_controls = False
    self._solve_thread = None

  def validate_solution(self):
    if self.master.lock_controls:
      return
    if not self.master.manager.validator.is_valid():
      self.validate_lbl['text'] = 'Puzzle has errors'
    elif not self.master.manager.validator.is_complete():
      self.validate_lbl['text'] = 'Puzzle is incomplete'
    else:
      self.validate_lbl['text'] = 'Puzzle has been solved'
