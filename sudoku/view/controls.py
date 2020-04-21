import tkinter as tk
import tkinter.filedialog as tkfiledialog
import events.bus as events
import sudoku.events.solver as solverevents


class Controls(tk.Frame, events.EventListenerSync):

  def __init__(self, master, store, solver_store):
    super().__init__(master)
    self._store = store
    self._solver_store = solver_store
    self._load_btn = None
    self._save_btn = None
    self._solve_btn = None

  def init(self):
    self._render_controls()

  def _render_controls(self):
    if self._load_btn is not None:
      self._load_btn.destroy()
    if self._save_btn is not None:
      self._save_btn.destroy()
    if self._solve_btn is not None:
      self._solve_btn.destroy()

    btn_state = tk.NORMAL if not self._solver_store.solution_in_progress else tk.DISABLED
    self._load_btn = tk.Button(self, text = 'Load puzzle', state = btn_state, command = self._load)
    self._load_btn.pack(side = tk.LEFT)
    self._save_btn = tk.Button(self, text = 'Save puzzle', state = btn_state, command = self._save)
    self._save_btn.pack(side = tk.LEFT)
    if not self._solver_store.solution_in_progress:
      self._solve_btn = tk.Button(self, text = 'Solve', command = self._solve)
    else:
      self._solve_btn = tk.Button(self, text = 'Stop', command = self._stop_solution)
    self._solve_btn.pack(side = tk.LEFT)

  def _load(self):
    fh = tkfiledialog.askopenfile()
    if fh is not None:
      with fh as fh_open:
        self._store.load(fh_open)

  def _save(self):
    fh = tkfiledialog.asksaveasfile()
    if fh is not None:
      with fh as fh_open:
        self._store.save(fh_open)

  def _solve(self):
    self._store.clear_all_highlights()
    self._store.clear_all_highlights2()
    self._solver_store.solve_in_thread(self._store)

  def _stop_solution(self):
    self._solver_store.stop_thread()

  def receive(self, event):
    if isinstance(event, solverevents.SolutionStartedEvent):
      self._render_controls()
    elif isinstance(event, solverevents.SolutionFinishedEvent):
      self._render_controls()
