import store.board as board


_easy_7x7 = [
  (2, 1, 0),
  (4, 1, None),
  (1, 2, 2),
  (5, 2, None),
  (3, 3, 3),
  (1, 4, None),
  (5, 4, 2),
  (2, 5, 0),
  (4, 5, None)
]


_easy_10x10 = [
  (0, 0, None),
  (3, 0, None),
  (9, 0, None),
  (7, 1, 0),
  (1, 2, 0),
  (3, 2, 2),
  (3, 3, 1),
  (6, 3, None),
  (7, 3, 2),
  (9, 3, None),
  (0, 6, None),
  (2, 6, 1),
  (3, 6, None),
  (6, 6, None),
  (6, 7, 0),
  (8, 7, 1),
  (2, 8, 0),
  (0, 9, 1),
  (6, 9, None),
  (9, 9, 0)
]


class PuzzleLoader:

  EASY_7x7 = 7, 7, _easy_7x7
  EASY_10x10 = 10, 10, _easy_10x10

  @staticmethod
  def load_puzzle(store, puzzle):
    store.reset_board(puzzle[0], puzzle[1])
    for cell in puzzle[2]:
      store.set_cell_state(cell[0], cell[1], board.CellState.WALL)
      store.set_cell_count(cell[0], cell[1], cell[2])
