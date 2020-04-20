class ICellAnalyser:

  def adjacent_cells(self, x, y):
    pass

  def get_cell_sets(self):
    pass


class HorizontalCellAnalyser(ICellAnalyser):

  def adjacent_cells(self, x, y, include_own=False):
    return {
      (x, i) for i in range(9) if include_own or i != y
    }
  
  def get_cell_sets(self):
    return [
      self.adjacent_cells(i, 0, True) for i in range(9)
    ]


class VerticalCellAnalyser(ICellAnalyser):

  def adjacent_cells(self, x, y, include_own=False):
    return {
      (i, y) for i in range(9) if include_own or i != x
    }

  def get_cell_sets(self):
    return [
      self.adjacent_cells(i, 0, True) for i in range(9)
    ]


class SquareCellAnalyser(ICellAnalyser):

  def adjacent_cells(self, x, y, include_own=False):
    r_set = set()
    for i in self._get_range(x):
      for j in self._get_range(y):
        if include_own or (i != x and j != y):
          r_set.add((i, j))
    
    return r_set

  def _get_range(self, z):
    r_start = z - z % 3
    return range(r_start, r_start + 3)

  def get_cell_sets(self):
    r_list = []
    for x in range(3):
      for y in range(3):
        r_list.append(self.adjacent_cells(x, y, True))

    return r_list


class UnionCellAnalyser(ICellAnalyser):
  
  def __init__(self, sources):
    self._sources = sources

  def adjacent_cells(self, x, y):
    r_set = set()
    for source in self._sources:
      r_set.update(source.adjacent_cells(x, y))

    return r_set

  def get_cell_sets(self):
    r_list = []
    for source in self._sources:
      r_list.extend(source.get_cell_sets())

    return r_list
