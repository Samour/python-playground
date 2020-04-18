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

  def valid(self, x, y):
    pass


class IncidentLightCountRule(ICellRule):
  
  def __init__(self, store):
    self._store = store

  def validate(self, x, y):
    cell = self._store.get_cell(x, y)
    if cell.state is not store.board.CellState.WALL or cell.count is None:
      return None

    adjacent_lights = 0
    for adj_cell in self._incident_cells(x, y):
      if adj_cell.state is store.board.CellState.LIGHT:
        adjacent_lights += 1

    if adjacent_lights > cell.count:
      return RuleViolated(x, y, RuleViolated.ILLEGAL, self)
    elif adjacent_lights < cell.count:
      return RuleViolated(x, y, RuleViolated.INSUFFICIENT, self)

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
    
    return map(lambda i: self._store.get_cell(*i), incident_cells)


class LightCollisionRule(ICellRule):

  def __init__(self, store):
    self._store = store

  def validate(self, x, y):
    if self._store.get_cell(x, y).state is not store.board.CellState.LIGHT:
      return None

    for cell, i, j in self._store.line_of_sight(x, y):
      if cell.state is store.board.CellState.LIGHT:
        return RuleViolated(x, y, RuleViolated.ILLEGAL, self)


class CellNotLitRule(ICellRule):

  def __init__(self, store):
    self._store = store

  def validate(self, x, y):
    cell = self._store.get_cell(x, y)
    if not cell.lit and cell.state is not store.board.CellState.WALL:
      return RuleViolated(x, y, RuleViolated.INSUFFICIENT, self)


class SolutionValidator:

  def __init__(self, store):
    self._store = store
    self._rules = [
      IncidentLightCountRule(store),
      LightCollisionRule(store),
      CellNotLitRule(store)
    ]

  def validate(self):
    rules_violated = []
    for x in range(self._store.dims[0]):
      for y in range(self._store.dims[1]):
        for rule in self._rules:
          validation = rule.validate(x, y)
          if validation is not None:
            if LOG_VIOLATIONS:
              print(validation)
            rules_violated.append(validation)

    return rules_violated
