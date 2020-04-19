import tkinter as tk
import tkinter.filedialog as tkfiledialog


class Controls(tk.Frame):

  def __init__(self, master, store):
    super().__init__(master)
    self._store = store
    self._load_btn = None
    self._save_btn = None

  def init(self):
    self._load_btn = tk.Button(self, text = 'Load puzzle', command = self._load)
    self._load_btn.pack(side = tk.LEFT)
    self._save_btn = tk.Button(self, text = 'Save puzzle', command = self._save)
    self._save_btn.pack(side = tk.LEFT)

  def _load(self):
    with tkfiledialog.askopenfile() as fh:
      self._store.load(fh)

  def _save(self):
    with tkfiledialog.asksaveasfile() as fh:
      self._store.save(fh)
