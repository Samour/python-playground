import random
import model
import serializer

def grid(x, y):
  puzzle = model.Puzzle(model.Puzzle.MODEL_GRID, (x, y))
  for i in range(x):
    for j in range(y):
      if i > 0:
        puzzle.lines.append(model.Line(model.Vertex(i - 1, j), model.Vertex(i, j)))
      if j > 0:
        puzzle.lines.append(model.Line(model.Vertex(i, j - 1), model.Vertex(i, j)))
      if i > 0 and j > 0:
        puzzle.line_counts.append(model.LineCount(model.Vertex(i - 0.5, j - 0.5), None))

  return puzzle


def triangular(x, y):
  puzzle = model.Puzzle
