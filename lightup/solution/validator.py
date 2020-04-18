import store.board as board


LOG_VIOLATIONS = False


class IncidentLightUtil:

  @staticmethod
  def incident_cells(x, y, dims):
    incident_cells = []
    if x - 1 >= 0:
      incident_cells.append((x - 1, y))
    if x + 1 < dims[0]:
      incident_cells.append((x + 1, y))
    if y - 1 >= 0:
      incident_cells.append((x, y - 1))
    if y + 1 < dims[1]:
      incident_cells.append((x, y + 1))
    
    return incident_cells

  @staticmethod
  def get_adjacent(store, x, y):
    return [
      (store.get_cell(*i), i[0], i[1]) for i in IncidentLightUtil.incident_cells(x, y, store.dims)
    ]

  @staticmethod
  def count_adjacent(store, x, y):
    return len([
      cell for cell in IncidentLightUtil.get_adjacent(store, x, y) if cell[0].state is not board.CellState.WALL
    ])

  @staticmethod
  def count_adjacent_lights(store, x, y):
    return len([
      cell for cell in IncidentLightUtil.get_adjacent(store, x, y) if cell[0].state is board.CellState.LIGHT
    ])

  @staticmethod
  def count_adjacent_cross(store, x, y):
    return len([
      cell for cell in IncidentLightUtil.get_adjacent(store, x, y)
        if cell[0].state is board.CellState.CROSS or (cell[0].lit and cell[0].state is not board.CellState.LIGHT)
    ])


class RuleViolated:

  ILLEGAL = 'ILLEGAL'
  INSUFFICIENT = 'INSUFFICIENT'

  def __init__(self, x, y, validation_mode, rule):
    self.x = x
    self.y = y
    self.mode = validation_mode
    self.rule = rule

  def __str__(self):
    return '(x = {}, y = {}, mode = {}, rule = {})'.format(self.x, self.y, self.mode, type(self.rule).__name__)


class ICellRule:

  def valid(self, x, y, cell):
    pass


class WallIncidentLightCountRule(ICellRule):
  
  def __init__(self, store):
    self._store = store

  def validate(self, x, y, cell):
    if cell.state is not board.CellState.WALL or cell.count is None:
      return None

    violation_mode = self._validate_count(
      IncidentLightUtil.count_adjacent(self._store, x, y),
      IncidentLightUtil.count_adjacent_lights(self._store, x, y),
      IncidentLightUtil.count_adjacent_cross(self._store, x, y),
      cell.count
    )
    if violation_mode is not None:
      return RuleViolated(x, y, violation_mode, self)

  def _validate_count(self, adjacent_all, adjacent_lights, adjacent_cross, cell_count):
    if adjacent_lights > cell_count or adjacent_cross > adjacent_all - cell_count:
      return RuleViolated.ILLEGAL
    elif adjacent_lights < cell_count:
      return RuleViolated.INSUFFICIENT


class IncidentLightCountRule(WallIncidentLightCountRule):

  def validate(self, x, y, cell):
    if cell.state not in (board.CellState.LIGHT, board.CellState.CROSS):
      return None

    violations = []
    
    for i, j in IncidentLightUtil.incident_cells(x, y, self._store.dims):
      wall_cell = self._store.get_cell(i, j)
      if wall_cell.state is not board.CellState.WALL or wall_cell.count is None:
        continue

      adj_lights = IncidentLightUtil.count_adjacent_lights(self._store, i, j)
      adj_cross = IncidentLightUtil.count_adjacent_cross(self._store, i, j)
      if cell.state is board.CellState.LIGHT:
        adj_lights += 1
      elif cell.state is board.CellState.CROSS:
        adj_cross += 1
      violation_mode = self._validate_count(
        IncidentLightUtil.count_adjacent(self._store, i, j),
        adj_lights,
        adj_cross,
        wall_cell.count
      )
      if violation_mode is not None:
        violations.append(RuleViolated(x, y, violation_mode, self))

    if len(violations) == 0:
      return None
    illegal_violations = [v for v in violations if v.mode is RuleViolated.ILLEGAL]
    if len(illegal_violations) > 0:
      return illegal_violations[0]
    else:
      return violations[0]


class LightCollisionRule(ICellRule):

  def __init__(self, store):
    self._store = store

  def validate(self, x, y, cell):
    if cell.state is not board.CellState.LIGHT:
      return None

    for cell_los, i, j in self._store.line_of_sight(x, y):
      if cell_los.state is board.CellState.LIGHT:
        return RuleViolated(x, y, RuleViolated.ILLEGAL, self)


class CellNotLitRule(ICellRule):

  def __init__(self, store):
    self._store = store

  def validate(self, x, y, cell):
    if not cell.lit and cell.state is not board.CellState.WALL:
      return RuleViolated(x, y, RuleViolated.INSUFFICIENT, self)


class SolutionValidator:

  def __init__(self, store, rules):
    self._store = store
    self._rules = rules
  
  def placement_legal(self, x, y, cell):
    rules_violated = []
    for rule in self._rules:
      validation = rule.validate(x, y, cell)
      if validation is None:
        continue
      if LOG_VIOLATIONS:
        print(validation)
      rules_violated.append(validation)
    
    return rules_violated

  def validate(self):
    rules_violated = []
    for x in range(self._store.dims[0]):
      for y in range(self._store.dims[1]):
        rules_violated.extend(self.placement_legal(x, y, self._store.get_cell(x, y)))

    return rules_violated


class SolutionValidatorBuilder:

  @staticmethod
  def solution_validator(store):
    return SolutionValidator(store, [
      WallIncidentLightCountRule(store),
      LightCollisionRule(store),
      CellNotLitRule(store)
    ])
  
  @staticmethod
  def solver_validator(store):
    return SolutionValidator(store, [
      IncidentLightCountRule(store),
      LightCollisionRule(store),
      CellNotLitRule(store)
    ])
