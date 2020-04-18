import events


class ISolver:

  def solve(self, store):
    pass
  
  def count_solutions(self, store):
    pass


class ISolverAsync(ISolver):

  def stop(self):
    pass
