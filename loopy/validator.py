import math
import model


class LineCount:

  def __init__(self, line_count):
    self.line_count = line_count
    self.lines = set()


class PuzzleValidator:

  def __init__(self, puzzle):
    self.puzzle = puzzle
    self.vertex_lines = {}
    self.line_counts = []
    self._derive_graph()

  def _derive_graph(self):
    self.vertex_lines = {}
    line_gradients = set()
    for line in self.puzzle.lines:
      if line.v2.y - line.v1.y == 0:
        line_gradients.add(None)
      else:
        line_gradients.add((line.v1.x - line.v1.x) / (line.v2.y - line.v1.y)) # Perpendicular gradient to detect intersections
      for vertex in line.v1, line.v2:
        if vertex.x not in self.vertex_lines:
          self.vertex_lines[vertex.x] = {}
        if vertex.y not in self.vertex_lines[vertex.x]:
          self.vertex_lines[vertex.x][vertex.y] = []
        self.vertex_lines[vertex.x][vertex.y].append(line)

    self.line_counts = []
    for line_count in self.puzzle.line_counts:
      count_r = LineCount(line_count)
      self.line_counts.append(count_r)
      for grad in line_gradients:
        line_lower = None
        line_lower_d = None
        line_upper = None
        line_upper_d = None
        if grad is None:
          rel = line_count.vertex.y
          ray_c = line_count.vertex.x
        else:
          rel = line_count.vertex.x
          ray_c = line_count.vertex.y - grad * line_count.vertex.x
        for line in self.puzzle.lines:
          inter = self._lines_intersection(grad, ray_c, line)
          if inter is None:
            continue
          if inter > rel:
            if line_upper_d is None or line_upper_d > inter - rel:
              line_upper_d = inter - rel
              line_upper = line
          else:
            if line_lower_d is None or line_lower_d > rel - inter:
              line_lower_d = rel - inter
              line_lower = line
        if line_lower is not None:
          count_r.lines.add(line_lower)
        if line_upper is not None:
          count_r.lines.add(line_upper)

  def _lines_intersection(self, grad, ray_c, line):
    if line.v2.x == line.v1.x: # Line is vertical case; don't need to calculate x value at intersection
      if grad is None: # Parallel vertical lines
        return None
      inter_y = grad * line.v2.x + ray_c
      # Check the intersection is on the line segment
      if inter_y >= min(line.v1.y, line.v2.y) and inter_y <= max(line.v1.y, line.v2.y):
        return line.v2.x
      else:
        return None

      return line.v2.x

    line_m = (line.v2.y - line.v1.y) / (line.v2.x - line.v1.x)
    line_c = line.v1.y - line_m * line.v1.x
    if grad is None: # ray is vertical line case
      inter_y = line_m * ray_c + line_c
      # Check the intersection is on the line segment
      if ray_c >= min(line.v1.x, line.v2.x) and ray_c <= max(line.v1.x, line.v2.x):
        return inter_y
      else:
        return None
    elif line_m == grad: # Lines are parallel case - no intersection
      return None
    else: # All other cases - calculate intersection of lines
      inter_x = (line_c - ray_c) / (grad - line_m)
      # Check the intersection is on the line segment
      if inter_x >= min(line.v1.x, line.v2.x) and inter_x <= max(line.v1.x, line.v2.x):
        return inter_x
      else:
        return None

  def _line_as_tup(self, line):
    return ((line.v1.x, line.v1.y), (line.v2.x, line.v2.y))

  def _count_states(self, lines):
    counts = {
      model.Line.STATE_PRESENT: 0,
      model.Line.STATE_ABSENT: 0,
      model.Line.STATE_UNKNOWN: 0
    }

    for line in lines:
      counts[line.state] += 1

    return counts

  def _validate_vertex(self, x, y):
    # No dead-end or intersecting lines
    counts = self._count_states(self.vertex_lines[x][y])

    if counts[model.Line.STATE_UNKNOWN] == 0:
      return counts[model.Line.STATE_PRESENT] in (0, 2)
    else:
      return counts[model.Line.STATE_PRESENT] <= 2

  def _validate_line_count(self, line_count):
    if line_count.line_count.value is None:
      return True
      
    # Not more or less than lines than specified by line count
    counts = self._count_states(line_count.lines)

    return counts[model.Line.STATE_PRESENT] <= line_count.line_count.value and \
      counts[model.Line.STATE_PRESENT] + counts[model.Line.STATE_UNKNOWN] >= line_count.line_count.value

  def _line_not_part_of_sub_loop(self, line, encountered):
    line_tup = self._line_as_tup(line)
    # No sub-loops
    if line.state != model.Line.STATE_PRESENT:
      return True

    encountered.add(line_tup)
    next1 = [l for l in self.vertex_lines[line.v1.x][line.v1.y] if l.state == model.Line.STATE_PRESENT]
    next2 = [l for l in self.vertex_lines[line.v2.x][line.v2.y] if l.state == model.Line.STATE_PRESENT]
    valid = False
    for next_cand in next1, next2:
      if len(next_cand) > 1:
        for next_line in next_cand:
          if not self._line_as_tup(next_line) in encountered:
            return self._line_not_part_of_sub_loop(next_line, encountered)
      else:
        valid = True

    if valid:
      return True

    expected = {
      ((line.v1.x, line.v1.y), (line.v2.x, line.v2.y)) 
      for line in self.puzzle.lines if line.state == model.Line.STATE_PRESENT
    }
    
    return expected == encountered

  def valid_for_line(self, line):
    for v in line.v1, line.v2:
      if not self._validate_vertex(v.x, v.y):
        return False

    for line_count in self.line_counts:
      if line in line_count.lines and not self._validate_line_count(line_count):
        return False

    return self._line_not_part_of_sub_loop(line, set())

  def is_valid(self):
    for x in self.vertex_lines:
      for y in self.vertex_lines:
        if not self._validate_vertex(x, y):
          return False

    for line_count in self.line_counts:
      if not self._validate_line_count(line_count):
        return False

    lines_to_check = set(filter(lambda l: l.state == model.Line.STATE_PRESENT, self.puzzle.lines))
    while len(lines_to_check) > 0:
      checked = set()
      if not self._line_not_part_of_sub_loop(lines_to_check.pop(), checked):
        return False
      lines_to_remove = set()
      for line in lines_to_check:
        if self._line_as_tup(line) in checked:
          lines_to_remove.add(line)
      for line in lines_to_remove:
        lines_to_check.remove(line)

    return True

  def is_complete(self):
    for line in self.puzzle.lines:
      if line.state == model.Line.STATE_UNKNOWN:
        return False

    return True
