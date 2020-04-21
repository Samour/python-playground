import tkinter as tk
import events.bus as events
import sudoku.events.sudoku as sudokuevents
import sudoku.events.solver as solverevents
import sudoku.store.board as board


class GameControls(tk.Frame, events.EventListenerSync):

  def __init__(self, master, store, solver_store):
    super().__init__(master)
    self._store = store
    self._solver_store = solver_store
    self._row_numbers = None
    self._cell_btn = None
    self._note_btn = None
    self._undo_btn = None
    self._redo_btn = None
    self._row_board = None
    self._lock_btn = None
    self._clear_btn = None
    self._reset_btn = None

  def init(self):
    self._row_numbers = tk.Frame(self)
    self._row_numbers.pack()
    self._render_row_numbers()

    self._row_board = tk.Frame(self)
    self._row_board.pack()
    self._render_row_board()

  def _render_row_numbers(self):
    if self._cell_btn is not None:
      self._cell_btn.destroy()
    if self._note_btn is not None:
      self._note_btn.destroy()
    if self._undo_btn is not None:
      self._undo_btn.destroy()
    if self._redo_btn is not None:
      self._redo_btn.destroy()
    
    mode = self._store.mode
    self._cell_btn = tk.Button(
      self._row_numbers,
      text = 'Cell',
      state = tk.DISABLED\
        if self._solver_store.solution_in_progress or mode is board.SudokuStore.MODE_VALUE\
        else tk.NORMAL,
      command = self._set_mode(board.SudokuStore.MODE_VALUE)
    )
    self._cell_btn.pack(side = tk.LEFT)
    self._note_btn = tk.Button(
      self._row_numbers,
      text = 'Note',
      state = tk.NORMAL\
        if not self._solver_store.solution_in_progress and mode is board.SudokuStore.MODE_VALUE\
        else tk.DISABLED,
      command = self._set_mode(board.SudokuStore.MODE_NOTE)
    )

    btn_state = tk.DISABLED if self._solver_store.solution_in_progress else tk.NORMAL
    self._note_btn.pack(side = tk.LEFT)
    self._undo_btn = tk.Button(self._row_numbers, state = btn_state, text = 'Undo', command = self._undo)
    self._undo_btn.pack(side = tk.LEFT)
    self._redo_btn = tk.Button(self._row_numbers, state = btn_state, text = 'Redo', command = self._redo)
    self._redo_btn.pack(side = tk.LEFT)

  def _render_row_board(self):
    if self._lock_btn is not None:
      self._lock_btn.destroy()
    if self._clear_btn is not None:
      self._clear_btn.destroy()
    if self._reset_btn is not None:
      self._reset_btn.destroy()

    btn_state = tk.DISABLED if self._solver_store.solution_in_progress else tk.NORMAL
    self._lock_btn = tk.Button(
      self._row_board,
      state = btn_state,
      text = 'Lock values',
      command = self._lock_values
    )
    self._lock_btn.pack(side = tk.LEFT)
    self._clear_btn = tk.Button(
      self._row_board,
      state = btn_state,
      text = 'Clear all values',
      command = self._clear_board
    )
    self._clear_btn.pack(side = tk.LEFT)
    self._reset_btn = tk.Button(
      self._row_board,
      state = btn_state,
      text = 'Reset solution',
      command = self._reset_game
    )
    self._reset_btn.pack(side = tk.LEFT)

  def _lock_values(self):
    for x in range(9):
      for y in range(9):
        self._store.set_cell_fixed(x, y, self._store.get_cell(x, y).value is not None)

  def _clear_board(self):
    self._store.clear_all()

  def _reset_game(self):
    self._store.reset_solution()

  def _set_mode(self, mode):
    def cb():
      self._store.set_mode(mode)
    return cb

  def _undo(self):
    self._store.undo()

  def _redo(self):
    self._store.redo()

  def receive(self, event):
    if isinstance(event, sudokuevents.ModeChangedEvent):
      self._render_row_numbers()
    elif isinstance(event, solverevents.SolutionStartedEvent):
      self._render_controls()
    elif isinstance(event, solverevents.SolutionFinishedEvent):
      self._render_controls()

  def _render_controls(self):
    self._render_row_numbers()
    self._render_row_board()


class GameCanvas(tk.Frame, events.EventListenerSync):

  _BOARD_SIZE = 400
  _BOARD_BUFFER = 10
  _CELL_FONT_MAIN = 'Times', 20
  _CELL_FONT_NOTE = 'Times', 10
  _CELL_FIXED_BACKGROUND = '#ffffdd'
  _CELL_HIGHLIGHT_BACKGROUND = '#ddddff'
  _CELL_HIGHLIGHT2_BACKGROUND = '#ff8888'

  def __init__(self, master, store, solver_store):
    super().__init__(master)
    self._store = store
    self._solver_store = solver_store
    self._canvas = None
    self._game_controls = None
    self._cells = [
      [ [] for i in range(9) ] for j in range(9)
    ]
    self._focus_cell = None

  def init(self, event_bus):
    if self._canvas is not None:
      self._canvas.destroy()
    
    canvas_size = self._BOARD_SIZE + self._BOARD_BUFFER * 2
    self._canvas = tk.Canvas(self, height = canvas_size, width = canvas_size)
    self._canvas.pack()
    self._canvas.bind('<Button-1>', self._handle_click)
    self._canvas.bind_all('<Key>', self._handle_keypress)
    self._game_controls = GameControls(self, self._store, self._solver_store)
    self._game_controls.pack()
    
    self._game_controls.subscribe(event_bus)
    self._game_controls.init()
    self._draw_grid()

  def _cell_to_grid(self, i):
    return i * self._BOARD_SIZE / 9 + self._BOARD_BUFFER

  def _draw_grid(self):
    for i in range(10):
      xy = self._cell_to_grid(i)
      width = 2 if i % 3 == 0 else 1
      self._canvas.create_line(
        xy, self._BOARD_BUFFER,
        xy, self._BOARD_SIZE + self._BOARD_BUFFER,
        width = width
      )
      self._canvas.create_line(
        self._BOARD_BUFFER, xy,
        self._BOARD_SIZE + self._BOARD_BUFFER, xy,
        width = width
      )

  def _handle_click(self, event):
    if self._solver_store.solution_in_progress:
      return

    x = int((event.x - self._BOARD_BUFFER) * 9 / self._BOARD_SIZE)
    y = int((event.y - self._BOARD_BUFFER) * 9 / self._BOARD_SIZE)
    if x >= 9 or x < 0 or y >= 9 or y < 0:
      return

    if self._focus_cell is not None:
      self._store.set_cell_highlight(self._focus_cell[0], self._focus_cell[1], False)
    self._focus_cell = x, y
    self._store.set_cell_highlight(x, y, True)

  def _handle_keypress(self, event):
    if self._solver_store.solution_in_progress or self._focus_cell is None:
      return
    
    x, y = self._focus_cell
    if event.keysym == 'space':
      self._store.set_cell_fixed(x, y, not self._store.get_cell(x, y).fixed)
    elif not self._store.get_cell(x, y).fixed:
      val = self._read_cell_value(event.keysym)
      if val == -1:
        return

      if self._store._mode is board.SudokuStore.MODE_VALUE:
        self._store.set_cell_value(x, y, val)
      elif val is not None:
        if val in self._store.get_cell(x, y).possible:
          self._store.remove_cell_possible(x, y, val)
        else:
          self._store.add_cell_possible(x, y, val)

  def _read_cell_value(self, sym):
    try:
      if sym == 'BackSpace' or sym == '0':
        return None
      else:
        return int(sym)
    except:
      return -1

  def receive(self, event):
    if isinstance(event, sudokuevents.SudokuCellUpdatedEvent):
      self._render_cell(event)

  def _render_cell(self, event):
    for handle in self._cells[event.x][event.y]:
      self._canvas.delete(handle)

    handles = []

    if event.cell.fixed:
      handles.append(self._draw_cell_highlight(event.x, event.y, self._CELL_FIXED_BACKGROUND))
    elif event.cell.highlight:
      handles.append(self._draw_cell_highlight(event.x, event.y, self._CELL_HIGHLIGHT_BACKGROUND))
    elif event.cell.highlight2:
      handles.append(self._draw_cell_highlight(event.x, event.y, self._CELL_HIGHLIGHT2_BACKGROUND))

    if event.cell.value is not None:
      x = self._cell_to_grid(event.x + 0.5)
      y = self._cell_to_grid(event.y + 0.5)
      handles.append(self._canvas.create_text(
        x, y,
        text = str(event.cell.value),
        font = self._CELL_FONT_MAIN
      ))
    else:
      for value in event.cell.possible:
        x = self._cell_to_grid(event.x + 1 / 6 + ((value - 1) % 3) * 1 / 3)
        y = self._cell_to_grid(event.y + 1 / 6 + int((value - 1) / 3) * 1 / 3)
        handles.append(self._canvas.create_text(
          x, y,
          text = str(value),
          font = self._CELL_FONT_NOTE
        ))

    self._cells[event.x][event.y] = handles

  def _draw_cell_highlight(self, x, y, colour):
    return self._canvas.create_rectangle(
      self._cell_to_grid(x) + 1, self._cell_to_grid(y) + 1,
      self._cell_to_grid(x + 1) - 1, self._cell_to_grid(y + 1) - 1,
      fill = colour,
      width = 0
    )
