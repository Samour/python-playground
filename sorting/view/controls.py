import tkinter as tk
import events


class SortStopEvent:
  pass


class Controls(tk.Frame, events.IEventListener):

  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.render_widgets()

  def render_widgets(self):
    self.new_list_btn = tk.Button(self, text = 'New list', command = self.master.new_list)
    self.new_list_btn.pack(side = 'left', padx = 5)
    self.run_btn = tk.Button(self, text = 'Sort', command = self._run_btn_click)
    self.run_btn.pack(side = 'left', padx = 5)
    self.configure_btn = tk.Button(self, text = 'Configuration', command = self.master.open_configuration)
    self.configure_btn.pack(side = 'left', padx = 5)

  def _run_btn_click(self):
    if self.master.sorting:
      self.master.stop_sort()
    else:
      self.run_btn['text'] = 'Stop'
      self.master.run_sort()

  def receive(self, event):
    if isinstance(event, SortStopEvent):
      self.run_btn['text'] = 'Sort'
