
class SudokuCell:

  def __init__(self):
    self.value = None
    self.fixed = False
    self.highlight = False
    self.highlight2 = False
    self.possible = set()

  def copy(self):
    cell = SudokuCell()
    cell.value = self.value
    cell.fixed = self.fixed
    cell.highlight = self.highlight
    cell.highlight2 = self.highlight2
    cell.possible = set(self.possible)
    
    return cell

  def __eq__(self, o):
    return self.value == o.value and self.fixed == o.fixed and self.highlight == o.highlight\
      and self.highlight2 == o.highlight2 and self.possible == o.possible

  def __str__(self):
    return '(value = {}, fixed = {}, highlight = {}, highlight2 = {}, possible = {})'.format(
      self.value,
      self.fixed,
      self.highlight,
      self.highlight2,
      self.possible
    )
