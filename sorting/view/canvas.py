import tkinter as tk
import events
import sorting


class DrawBarEvent:

  def __init__(self, i, v, compare, swap):
    self.i = i
    self.v = v
    self.compare = compare
    self.swap = swap


class ResetHighlightsEvent:
  pass


class EventCount(tk.Frame, events.IEventListener):

  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.comparison_count = 0
    self.switch_count = 0
    self.render_widgets()

  def render_widgets(self):
    self._comparison_var = tk.StringVar()
    comparison_lbl = tk.Label(self, textvariable = self._comparison_var)
    comparison_lbl.pack(side = 'left', padx = 5)
    self._switch_var = tk.StringVar()
    switch_lbl = tk.Label(self, textvariable = self._switch_var)
    switch_lbl.pack(side = 'left', padx = 5)
    self.write_counts()

  def _write_comp_count(self):
    self._comparison_var.set('Comparisons: {}'.format(self.comparison_count))

  def _write_switch_count(self):
    self._switch_var.set('Switches: {}'.format(self.switch_count))

  def receive(self, event):
    if isinstance(event, sorting.ComparisonEvent):
      self.comparison_count += 1
    elif isinstance(event, sorting.SwitchEvent):
      self.switch_count += 1

  def write_counts(self):
      self._write_comp_count()
      self._write_switch_count()

  def reset_counts(self):
    self.comparison_count = 0
    self.switch_count = 0
    self.write_counts()


class ListCanvas(tk.Frame, events.IEventListener):

  _WIDTH = 1200
  _HEIGHT = 600
  _BUFFER = 0.5
  _BAR_FILL = 'gray'
  _BAR_COMPARE = 'blue'
  _BAR_SWAP = 'red'

  def __init__(self, master):
    super().__init__(master)
    self._bars = []
    self._line_width = 0
    self._offset_c = 0
    self._height_c = 0
    self._highlighted = []
    self.render_widgets()

  def render_widgets(self):
    self.canvas = tk.Canvas(self, width = self._WIDTH, height = self._HEIGHT)
    self.canvas.pack()

  def draw_list(self, lst):
    self.canvas.delete(tk.ALL)
    self._bars = [None for v in lst]
    max_v = max(lst)
    count_v = len(lst)
    self._line_width = self._WIDTH / ((1 + self._BUFFER) * count_v - self._BUFFER)
    self._offset_c = (1 + self._BUFFER) * self._line_width
    self._height_c = self._HEIGHT / max_v
    for i in range(count_v):
      self._draw_bar(i, lst[i])

  def _draw_bar(self, i, v, highlight = None):
    if self._bars[i] is not None:
      self.canvas.delete(self._bars[i])
    offset = i * self._offset_c
    self._bars[i] = self.canvas.create_rectangle(
      offset, self._HEIGHT, offset + self._line_width,
      self._HEIGHT - v * self._height_c,
      width = 0,
      fill = self._BAR_FILL if highlight is None else highlight
    )
    if highlight is not None:
      self._highlighted.append((i, v))

  def receive(self, event):
    if isinstance(event, DrawBarEvent):
      if event.compare:
        self._draw_bar(event.i, event.v, self._BAR_COMPARE)
      elif event.swap:
        self._draw_bar(event.i, event.v, self._BAR_SWAP)
      else:
        self._draw_bar(event.i, event.v)
    elif isinstance(event, ResetHighlightsEvent):
      while len(self._highlighted) > 0:
        self._draw_bar(*self._highlighted.pop())
