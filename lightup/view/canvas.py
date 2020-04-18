import math
import tkinter as tk
import events
import store.board


class BoardCanvas(tk.Frame, events.EventListenerSync):

  _CELL_WIDTH = 30
  _CELL_HEIGHT = 30
  _BORDER_WIDTH = 1
  _CANVAS_BLEFT = 5
  _CANVAS_BTOP = 5
  _WALL_CELL_FILL = 'black'
  _WALL_TEXT_COLOUR = 'white'
  _WALL_TEXT_FONT = 'Times', 16
  _LIGHT_INNER_FILL = 'yellow'
  _LIGHT_PADDING = 10
  _LIGHT_RAY_R1 = 10
  _LIGHT_RAY_R2 = 13
  _CROSS_PADDING = 10
  _CROSS_COLOUR = 'red'
  _LIT_FILL = 'yellow'

  def __init__(self, master, board_store):
    super().__init__(master)
    self._canvas = None
    self._grid_dims = (0, 0)
    self._canvas_dims = (0, 0)
    self._focus_cell = None
    self._handles = []
    self._store = board_store

  def receive(self, event):
    if isinstance(event, store.board.BoardResetEvent):
      self._render_board(event)
    elif isinstance(event, store.board.CellStateUpdatedEvent):
      self._draw_cell(event)

  def _render_board(self, board_reset):
    # Create canvas
    if self._canvas is not None:
      self._canvas.destroy()
    self._grid_dims = (board_reset.x, board_reset.y)
    self._canvas_dims = (
      board_reset.x * (self._CELL_WIDTH + self._BORDER_WIDTH) + self._BORDER_WIDTH + self._CANVAS_BLEFT,
      board_reset.y * (self._CELL_HEIGHT + self._BORDER_WIDTH) + self._BORDER_WIDTH + self._CANVAS_BTOP
    )
    self._focus_cell = None
    self._handles = [
      [ [] for i in range(board_reset.y) ] for j in range(board_reset.x)
    ]
    self._canvas = tk.Canvas(
      self,
      width = self._canvas_dims[0],
      height = self._canvas_dims[1]
    )
    self._canvas.pack()
    self._canvas.bind('<Button-1>', self._handle_click)
    self._canvas.bind_all('<Key>', self._handle_keypress)

    # Draw vertical lines
    for i in range(board_reset.x + 1):
      x_pos = i * (self._CELL_WIDTH + self._BORDER_WIDTH) + self._CANVAS_BLEFT
      self._canvas.create_line(
        x_pos, self._CANVAS_BTOP,
        x_pos, self._canvas_dims[1] - self._BORDER_WIDTH,
        width = self._BORDER_WIDTH
      )

    # Draw horizontal lines
    for i in range(board_reset.y + 1):
      y_pos = i * (self._CELL_HEIGHT + self._BORDER_WIDTH) + self._CANVAS_BTOP
      self._canvas.create_line(
        self._CANVAS_BLEFT, y_pos,
        self._canvas_dims[0] - self._BORDER_WIDTH, y_pos,
        width = self._BORDER_WIDTH
      )

  def _handle_click(self, event):
    board_x = int((event.x - self._CANVAS_BLEFT) * self._grid_dims[0] / self._canvas_dims[0])
    board_y = int((event.y - self._CANVAS_BTOP) * self._grid_dims[1] / self._canvas_dims[1])
    self._focus_cell = board_x, board_y
    current_state = self._store.get_cell(board_x, board_y)
    next_state = self._next_state(current_state.state)
    
    if next_state is not None:
      self._store.set_cell_state(board_x, board_y, next_state)

  def _next_state(self, state):
    if self._store.game_mode is store.board.GameMode.CONSTRUCT:
      return self._next_state_construct(state)
    else:
      return self._next_state_solve(state)

  def _next_state_construct(self, state):
    if state is store.board.CellState.WALL:
      return store.board.CellState.EMPTY
    else:
      return store.board.CellState.WALL

  def _next_state_solve(self, state):
    if state is store.board.CellState.EMPTY:
      return store.board.CellState.LIGHT
    elif state is store.board.CellState.LIGHT:
      return store.board.CellState.CROSS
    elif state is store.board.CellState.CROSS:
      return store.board.CellState.EMPTY

  def _handle_keypress(self, event):
    if self._store.game_mode is not store.board.GameMode.CONSTRUCT or\
      self._store.get_cell(*self._focus_cell).state is not store.board.CellState.WALL:
      return

    if event.keysym == 'BackSpace':
      count = None
    else:
      try:
        count = int(event.keysym)
      except:
        return

    self._store.set_cell_count(self._focus_cell[0], self._focus_cell[1], count)

  def _draw_cell(self, cell):
    self._clear_cell(cell.x, cell.y)

    canvas_x = cell.x * (self._CELL_WIDTH + self._BORDER_WIDTH) + self._BORDER_WIDTH + self._CANVAS_BLEFT
    canvas_y = cell.y * (self._CELL_HEIGHT + self._BORDER_WIDTH) + self._BORDER_WIDTH + self._CANVAS_BTOP

    handles = []
    if cell.state.lit:
      handles.append(self._draw_lit_cell(canvas_x, canvas_y))

    if cell.state.state is store.board.CellState.EMPTY:
      handles.extend(self._draw_empty_cell(canvas_x, canvas_y, cell.state))
    elif cell.state.state is store.board.CellState.WALL:
      handles.extend(self._draw_wall_cell(canvas_x, canvas_y, cell.state))
    elif cell.state.state is store.board.CellState.LIGHT:
      handles.extend(self._draw_light_cell(canvas_x, canvas_y, cell.state))
    elif cell.state.state is store.board.CellState.CROSS:
      handles.extend(self._draw_cross_cell(canvas_x, canvas_y, cell.state))

    self._handles[cell.x][cell.y].extend(handles)

  def _clear_cell(self, x, y):
    for handle in self._handles[x][y]:
      self._canvas.delete(handle)
    self._handles[x][y] = []

  def _draw_empty_cell(self, x, y, cell):
    return []

  def _draw_wall_cell(self, x, y, cell):
    handles = [
      self._canvas.create_rectangle(
        x, y,
        x + self._CELL_HEIGHT, y + self._CELL_WIDTH,
        fill = self._WALL_CELL_FILL
      ) 
    ]

    if cell.count is not None:
      handles.append(
        self._canvas.create_text(
          x + self._CELL_WIDTH / 2, y + self._CELL_HEIGHT / 2,
          text = str(cell.count),
          fill = self._WALL_TEXT_COLOUR,
          font = self._WALL_TEXT_FONT
        )
      )

    return handles
  
  def _draw_light_cell(self, x, y, cell):
    origin_x = x + self._CELL_WIDTH / 2
    origin_y = y + self._CELL_HEIGHT / 2
    return [
      self._canvas.create_oval(
        x + self._LIGHT_PADDING, y + self._LIGHT_PADDING,
        x + self._CELL_HEIGHT - self._LIGHT_PADDING, y + self._CELL_WIDTH - self._LIGHT_PADDING,
        fill = self._LIGHT_INNER_FILL
      ),
      self._draw_light_ray(origin_x, origin_y, 0),
      self._draw_light_ray(origin_x, origin_y, 45),
      self._draw_light_ray(origin_x, origin_y, 90),
      self._draw_light_ray(origin_x, origin_y, 135),
      self._draw_light_ray(origin_x, origin_y, 180),
      self._draw_light_ray(origin_x, origin_y, -135),
      self._draw_light_ray(origin_x, origin_y, -90),
      self._draw_light_ray(origin_x, origin_y, -45)
    ]

  def _draw_light_ray(self, x, y, deg):
    cos = math.cos(math.radians(deg))
    sin = math.sin(math.radians(deg))
    return self._canvas.create_line(
      self._LIGHT_RAY_R1 * cos + x,
      self._LIGHT_RAY_R1 * sin + y,
      self._LIGHT_RAY_R2 * cos + x,
      self._LIGHT_RAY_R2 * sin + y
    )

  def _draw_cross_cell(self, x, y, cell):
    return [
      self._canvas.create_line(
        x + self._CROSS_PADDING, y + self._CROSS_PADDING,
        x + self._CELL_WIDTH - self._CROSS_PADDING, y + self._CELL_HEIGHT - self._CROSS_PADDING,
        fill = self._CROSS_COLOUR
      ),
      self._canvas.create_line(
        x + self._CROSS_PADDING, y + self._CELL_HEIGHT - self._CROSS_PADDING,
        x + self._CELL_WIDTH - self._CROSS_PADDING, y + self._CROSS_PADDING,
        fill = self._CROSS_COLOUR
      )
    ]

  def _draw_lit_cell(self, x, y):
    return self._canvas.create_rectangle(
      x, y,
      x + self._CELL_WIDTH, y + self._CELL_HEIGHT,
      fill = self._LIT_FILL,
      width = 0
    )
