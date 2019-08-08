import math
import tkinter as tk
import model


class GridPxConverter:

  def __init__(self, grid_dims, canvas_dims, padding = (0, 0)):
    self.grid_dims = grid_dims
    self.canvas_dims = canvas_dims
    self.padding = padding

  def grid_to_px(self, x, y):
    return self._grid_to_px_val(x, 0), self._grid_to_px_val(y, 1)

  def _grid_to_px_val(self, v, d):
    return v * (self.canvas_dims[d] - self.padding[d] * 2) / self.grid_dims[d] + self.padding[d]

  def px_to_grid(self, x, y):
    return self._px_to_grid_val(x, 0), self._px_to_grid_val(y, 1)

  def _px_to_grid_val(self, v, d):
    return (v - self.padding[d]) * self.grid_dims[d] / (self.canvas_dims[d] - self.padding[d] * 2)


class GeometricLine:

  _BOUND_DISTANCE_THRESHOLD = 0.3 # Note that this is grid units, not px

  def __init__(self, line):
    self.line = line
    self.a = line.v2.y - line.v1.y
    self.b = line.v1.x - line.v2.x
    self.c = line.v2.x * line.v1.y - line.v2.y * line.v1.x
    self.discriminant = math.sqrt(self.a * self.a + self.b * self.b)
    self.x_lower = min(line.v1.x, line.v2.x)
    self.x_upper = max(line.v1.x, line.v2.x)
    if self.x_lower == self.x_upper:
      self.x_lower -= self._BOUND_DISTANCE_THRESHOLD
      self.x_upper += self._BOUND_DISTANCE_THRESHOLD
    self.y_lower = min(line.v1.y, line.v2.y)
    self.y_upper = max(line.v1.y, line.v2.y)
    if self.y_lower == self.y_upper:
      self.y_lower -= self._BOUND_DISTANCE_THRESHOLD
      self.y_upper += self._BOUND_DISTANCE_THRESHOLD

  def point_within_bound(self, x, y):
    return x > self.x_lower and x < self.x_upper and y > self.y_lower and y < self.y_upper

  def distance_from_point(self, x, y):
    return abs(self.a * x + self.b * y + self.c) / self.discriminant


class LineCount:

  def __init__(self, line_count, box):
    self.line_count = line_count
    self.box = box


class GameCanvas(tk.Frame):

  _COLOUR_LINE_PRESENT = '#000000'
  _COLOUR_LINE_ABSENT = '#dddddd'
  _COLOUR_LINE_UNKNOWN = '#ccd8cc'
  _COLOUR_COUNT_SELECTED_BG = '#8888ff'

  def __init__(self, master = None):
    super().__init__(master)
    self.master = master
    self.canvas = None
    self.puzzle = None
    self.grid_converter = None
    self.lines = []
    self.line_counts = []
    self._point_size = (7, 7)
    self._selected_line_count = None
    self._selected_line_count_box = None

  def draw_new_game(self, puzzle):
    self.puzzle = puzzle
    if self.puzzle is not None:
      self.lines = [GeometricLine(line) for line in puzzle.lines]
      self.line_counts = [LineCount(line_count, None) for line_count in puzzle.line_counts]
    self.redraw_game()

  def redraw_game(self):
    if self.canvas is not None:
      self.canvas.destroy()

    if self.puzzle is None:
      return

    self.canvas = tk.Canvas(self, width = 400, height = 400, highlightthickness = 0)
    self.canvas.bind('<Button-1>', self.handle_click)
    self.canvas.bind('<Key>', self.handle_key_press)
    self.canvas.pack()

    vertices = set()
    for line in self.puzzle.lines:
      for v in line.v1, line.v2:
        vertices.add((v.x, v.y))
    self.grid_converter = GridPxConverter(
      (max([v[0] for v in vertices]), max([v[1] for v in vertices])), 
      (int(self.canvas['width']), int(self.canvas['height'])),
      padding = (40, 40)
    )

    for line in self.puzzle.lines:
      self.draw_line(line)

    for x, y in vertices:
      self._draw_point(x, y)

    for line_count in self.line_counts:
      self._draw_number(line_count)

  def _draw_point(self, x, y, convert = True):
    px_x, px_y = self.grid_converter.grid_to_px(x, y) if convert else (x, y)
    self.canvas.create_oval(
      (px_x - self._point_size[0] / 2, px_y - self._point_size[1] / 2, 
        px_x + self._point_size[0] / 2, px_y + self._point_size[1] / 2),
      fill = 'black'
    )

  def draw_line(self, line, redraw_points = False):
    x0, y0 = self.grid_converter.grid_to_px(line.v1.x, line.v1.y)
    x1, y1 = self.grid_converter.grid_to_px(line.v2.x, line.v2.y)
    if line.state == model.Line.STATE_PRESENT:
      colour = self._COLOUR_LINE_PRESENT
    elif line.state == model.Line.STATE_ABSENT:
      colour = self._COLOUR_LINE_ABSENT
    else:
      colour = self._COLOUR_LINE_UNKNOWN
    self.canvas.create_line(x0, y0, x1, y1, width = 2, fill = colour)

    if redraw_points:
      self._draw_point(x0, y0, convert = False)
      self._draw_point(x1, y1, convert = False)

  def _draw_number(self, line_count, highlighted = False):
    x, y = self.grid_converter.grid_to_px(line_count.line_count.vertex.x, line_count.line_count.vertex.y)
    if highlighted:
      if self._selected_line_count_box is not None:
        self.canvas.delete(self._selected_line_count_box)
      self._selected_line_count_box = self.canvas.create_rectangle(
        x - 8,
        y - 10,
        x + 8,
        y + 10,
        outline = '',
        fill = self._COLOUR_COUNT_SELECTED_BG if highlighted else ''
      )
    if line_count.box is not None:
      self.canvas.delete(line_count.box)
    if line_count.line_count.value is not None:
      line_count.box = self.canvas.create_text(x, y, text = line_count.line_count.value)

  def handle_click(self, event):
    if self.master.edit_mode:
      self._handle_count_click(event)
    else:
      self._handle_line_click(event)

  def _handle_line_click(self, event):
    if self.master.lock_controls:
      return

    x, y = self.grid_converter.px_to_grid(event.x, event.y)
    line, distance = self._get_closest_line(x, y)
    if line is None:
      return

    if line.state == model.Line.STATE_UNKNOWN:
      line.state = model.Line.STATE_PRESENT
    elif line.state == model.Line.STATE_PRESENT:
      line.state = model.Line.STATE_ABSENT
    else:
      line.state = model.Line.STATE_UNKNOWN
    self._validate(line)

    self.draw_line(line, redraw_points=True)

  def _get_closest_line(self, x, y):
    closest_line = None
    closest_distance = None
    for line in self.lines:
      if line.point_within_bound(x, y):
        distance = line.distance_from_point(x, y)
        if closest_distance is None or distance < closest_distance:
          closest_distance = distance
          closest_line = line.line

    return closest_line, closest_distance

  def _highlight_line_count(self, line_count):
    self._draw_number(line_count, True)
    self._selected_line_count = line_count

  def _handle_count_click(self, event):
    self.canvas.focus_set()
    x, y = self.grid_converter.px_to_grid(event.x, event.y)
    closest_line_count = None
    closest_distance = None
    for line_count in self.line_counts:
      distance = math.sqrt((x - line_count.line_count.vertex.x) ** 2 + (y - line_count.line_count.vertex.y) ** 2)
      if closest_distance is None or distance < closest_distance:
        closest_distance = distance
        closest_line_count = line_count
    
    if closest_line_count is not None:
      self._highlight_line_count(closest_line_count)

  def _get_next_line_count(self, line_count):
    next_line_count = None
    for lc in self.line_counts:
      if lc is line_count:
        pass
      elif next_line_count is None:
        next_line_count = lc
      # next_line_count is lower than line_count
      elif next_line_count.line_count.vertex.y < line_count.line_count.vertex.y \
        or (next_line_count.line_count.vertex.y == line_count.line_count.vertex.y \
          and next_line_count.line_count.vertex.x < line_count.line_count.vertex.x):
        # lc is higher than line_count
        if lc.line_count.vertex.y > line_count.line_count.vertex.y \
          or (lc.line_count.vertex.y == line_count.line_count.vertex.y \
            and lc.line_count.vertex.x > line_count.line_count.vertex.x) \
          or lc.line_count.vertex.y < next_line_count.line_count.vertex.y \
          or (lc.line_count.vertex.y == next_line_count.line_count.vertex.y \
            and lc.line_count.vertex.x < next_line_count.line_count.vertex.x):
            next_line_count = lc
      # next_line_count is higher than line_count
      # lc is higher than line_count
      elif lc.line_count.vertex.y > line_count.line_count.vertex.y \
        or (lc.line_count.vertex.y == line_count.line_count.vertex.y \
          and lc.line_count.vertex.x > line_count.line_count.vertex.x):
        # lc is less than line_count
        if lc.line_count.vertex.y < next_line_count.line_count.vertex.y \
          or (lc.line_count.vertex.y == next_line_count.line_count.vertex.y \
            and lc.line_count.vertex.x < next_line_count.line_count.vertex.x):
          next_line_count = lc
    
    return next_line_count

  def handle_key_press(self, event):
    if not self.master.edit_mode or self._selected_line_count is None:
      return

    if event.keysym == 'Delete':
      val = None
    elif event.keysym == 'Tab':
      self.after(0, self.canvas.focus_set) # Otherwise focus moves away
      next_line_count = self._get_next_line_count(self._selected_line_count)
      if next_line_count is not None:
        self._highlight_line_count(next_line_count)
      return
    else:
      try:
        val = int(event.keysym)
      except:
        return

    self._selected_line_count.line_count.value = val
    self._draw_number(self._selected_line_count)

  def clean_edit(self):
    if self._selected_line_count_box is not None:
      self.canvas.delete(self._selected_line_count_box)
    self._selected_line_count = None

  def _validate(self, line):
    if self.master.manager.validator.is_complete():
      self.master.controls.validate_solution()
