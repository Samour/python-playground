import model
import validator


class PuzzleSolver(validator.PuzzleValidator):

  def __init__(self, puzzle, **options):
    super().__init__(puzzle)
    self.moves = []
    self._guesses = []
    self._step_callback = options['step_callback'] if 'step_callback' in options else None

  def _emit_lines(self, lines):
    if self._step_callback is not None:
      self._step_callback(lines)

  def _update_state(self, line, state):
    line.state = state
    self.moves.append(line)
    if self._step_callback is not None:
      self._step_callback([line])

    return self.valid_for_line(line)

  def _place_lines_for_counts(self):
    change = False
    for line_count in self.line_counts:
      counts = self._count_states(line_count.lines)
      if counts[model.Line.STATE_UNKNOWN] == 0:
        continue
      elif counts[model.Line.STATE_PRESENT] + counts[model.Line.STATE_UNKNOWN] == line_count.line_count.value:
        for line in line_count.lines:
          if line.state == model.Line.STATE_UNKNOWN:
            change = True
            if not self._update_state(line, model.Line.STATE_PRESENT):
              return change, False
      elif counts[model.Line.STATE_PRESENT] == line_count.line_count.value:
        for line in line_count.lines:
          if line.state == model.Line.STATE_UNKNOWN:
            change = True
            if not self._update_state(line, model.Line.STATE_ABSENT):
              return change, False
    
    return change, True

  def _remove_deadend_lines(self):
    change = False
    for x in self.vertex_lines:
      for y in self.vertex_lines[x]:
        counts = self._count_states(self.vertex_lines[x][y])
        if counts[model.Line.STATE_UNKNOWN] == 0:
          continue
        elif counts[model.Line.STATE_UNKNOWN] == 1 and counts[model.Line.STATE_PRESENT] == 1:
          for line in self.vertex_lines[x][y]:
            if line.state == model.Line.STATE_UNKNOWN:
              change = True
              if not self._update_state(line, model.Line.STATE_PRESENT):
                return change, False
        elif counts[model.Line.STATE_PRESENT] > 1 or counts[model.Line.STATE_UNKNOWN] == 1:
          for line in self.vertex_lines[x][y]:
            if line.state == model.Line.STATE_UNKNOWN:
              change = True
              if not self._update_state(line, model.Line.STATE_ABSENT):
                return change, False

    return change, True

  def _apply_edges(self):
    if len(self.moves) > 0 and not self.valid_for_line(self.moves[-1]):
      return False
    
    change = True
    while change:
      change = False
      fn_change, valid = self._place_lines_for_counts()
      if not valid:
        return False
      change = fn_change or change
      fn_change, valid = self._remove_deadend_lines()
      if not valid:
        return False
      change = fn_change or change

    return True
  
  def solve(self, count_solutions = False):
    soln_c = 0
    self.moves = []
    self._guesses = []
    while True:
      if not self._apply_edges():
        reverse_lines = []
        guess = self._guesses.pop()
        line = None
        while line != guess:
          line = self.moves.pop()
          line.state = model.Line.STATE_UNKNOWN
          reverse_lines.append(line)
        self._emit_lines(reverse_lines)
        self._update_state(guess, model.Line.STATE_ABSENT)
      else:
        if self.is_complete():
          soln_c += 1
          if count_solutions:
            return soln_c
        guess = None
        for line in self.puzzle.lines:
          if line.state == model.Line.STATE_UNKNOWN:
            guess = line
            break
        if guess is None:
          return soln_c
        self._guesses.append(guess)
        self._update_state(guess, model.Line.STATE_PRESENT)

      
