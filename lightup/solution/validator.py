import store.board


LOG_VIOLATIONS = False


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
    if cell.state is not store.board.CellState.WALL or cell.count is None:
      return None

    adjacent_lights = self._count_adjacent_lights(x, y)

    violation_mode = self._validate_count(
      self._count_adjacent_lights(x, y),
      cell.count
    )
    if violation_mode is not None:
      return RuleViolated(x, y, violation_mode, self)

  def _count_adjacent_lights(self, x, y):
    adjacent_lights = 0
    for adj_cell in map(lambda i: self._store.get_cell(*i), self._incident_cells(x, y)):
      if adj_cell.state is store.board.CellState.LIGHT:
        adjacent_lights += 1

    return adjacent_lights

  def _validate_count(self, adjacent_count, cell_count):
    if adjacent_count > cell_count:
      return RuleViolated.ILLEGAL
    elif adjacent_count < cell_count:
      return RuleViolated.INSUFFICIENT

  def _incident_cells(self, x, y):
    incident_cells = []
    if x - 1 >= 0:
      incident_cells.append((x - 1, y))
    if x + 1 < self._store.dims[0]:
      incident_cells.append((x + 1, y))
    if y - 1 >= 0:
      incident_cells.append((x, y - 1))
    if y + 1 < self._store.dims[1]:
      incident_cells.append((x, y + 1))
    
    return incident_cells


class IncidentLightCountRule(WallIncidentLightCountRule):

  def validate(self, x, y, cell):
    if cell.state is not store.board.CellState.LIGHT:
      return None

    violations = []
    
    for i, j in self._incident_cells(x, y):
      wall_cell = self._store.get_cell(i, j)
      if wall_cell.state is not store.board.CellState.WALL or wall_cell.count is None:
        continue

      violation_mode = self._validate_count(
        self._count_adjacent_lights(i, j) + 1,
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
    if cell.state is not store.board.CellState.LIGHT:
      return None

    for cell_los, i, j in self._store.line_of_sight(x, y):
      if cell_los.state is store.board.CellState.LIGHT:
        return RuleViolated(x, y, RuleViolated.ILLEGAL, self)


class CellNotLitRule(ICellRule):

  def __init__(self, store):
    self._store = store

  def validate(self, x, y, cell):
    if not cell.lit and cell.state is not store.board.CellState.WALL:
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
