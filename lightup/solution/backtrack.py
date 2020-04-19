import solution.validator
import solution.brute
import store.board as board


class BackTrackSolver(solution.brute.BruteForceSolver):

  def _populate_determined(self, store, validator, back_track):
    made_adjustment = True
    while made_adjustment:
      made_adjustment = False
      for y in range(store.dims[1]):
        for x in range(store.dims[0]):
          if self._break_soln:
            return
          
          rewind = None
          adj = False
          cell = store.get_cell(x, y)
          if cell.state is board.CellState.EMPTY and not cell.lit:
            rewind, adj = self._place_cross_on_illegal(cell, store, validator, back_track, x, y)
            if not rewind and not adj:
              rewind, adj = self._place_light_isolated_cell(store, cell, validator, back_track, x, y)
          elif cell.state is board.CellState.WALL and cell.count is not None:
            rewind, adj = self._place_lights_on_wall(store, cell, validator, back_track, x, y)
          elif cell.state is board.CellState.CROSS and not cell.lit:
            rewind, adj = self._place_only_viable_light(store, validator, back_track, x, y)
          
          if rewind:
            return rewind
          if not made_adjustment:
            made_adjustment = adj

  def _place_if_legal(self, cell, store, validator, back_track, x, y, state):
    validation_errors = validator.placement_legal(
      x, y,
      board.CellState(state, cell.lit, cell.count)
    )
    if self._count_illegal(validation_errors) == 0:
      back_track.set_cell_state(x, y, state, False)
      self._do_sleep()
      return
    
    return self._backtrack(store, validator, back_track)

  def _place_cross_on_illegal(self, cell, store, validator, back_track, x, y):
    validation_errors = validator.placement_legal(
      x, y,
      board.CellState(board.CellState.LIGHT, cell.lit, cell.count)
    )
    if self._count_illegal(validation_errors) == 0:
      return None, False

    return self._place_if_legal(cell, store, validator, back_track, x, y, board.CellState.CROSS), True

  def _place_light_isolated_cell(self, store, cell, validator, back_track, x, y):
    if len(self._get_empty_line_of_sight(store, x, y)) == 0:
      return self._place_if_legal(cell, store, validator, back_track, x, y, board.CellState.LIGHT), True
    else:
      return None, False

  def _place_lights_on_wall(self, store, cell, validator, back_track, x, y):
    adjacent_cells = solution.validator.IncidentLightUtil.get_adjacent(store, x, y)
    empty_cells = [cell for cell in adjacent_cells if cell[0].state is board.CellState.EMPTY and not cell[0].lit]
    light_cells = [cell for cell in adjacent_cells if cell[0].state is board.CellState.LIGHT]
    
    if len(empty_cells) > 0 and len(empty_cells) == cell.count - len(light_cells):
      for fill_cell, i, j in empty_cells:
        if self._break_soln:
          return None, False
        rewind = self._place_if_legal(fill_cell, store, validator, back_track, i, j, board.CellState.LIGHT)
        if rewind is not None:
          return rewind, True
      return None, True
    elif len(empty_cells) > 0 and len(light_cells) == cell.count:
      for fill_cell, i, j in empty_cells:
        if self._break_soln:
          return None, False
        rewind = self._place_if_legal(fill_cell, store, validator, back_track, i, j, board.CellState.CROSS)
        if rewind is not None:
          return rewind, True
      return None, True
    elif len(empty_cells) < cell.count - len(light_cells):
      return self._backtrack(store, validator, back_track), False
    
    return None, False

  def _get_empty_line_of_sight(self, store, x, y):
    return [
      cell for cell in store.line_of_sight(x, y) if cell[0].state is board.CellState.EMPTY and not cell[0].lit
    ]

  def _place_only_viable_light(self, store, validator, back_track, x, y):
    empty_cells = self._get_empty_line_of_sight(store, x, y)
    if len(empty_cells) == 1:
      cell, i, j = empty_cells[0]
      return self._place_if_legal(cell, store, validator, back_track, i, j, board.CellState.LIGHT), True
    elif len(empty_cells) == 0:
      return self._backtrack(store, validator, back_track), False
    else:
      return None, False
