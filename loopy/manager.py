import os
import random
import model
import serializer
import generator
import validator


class GameManager:

  def __init__(self):
    self.serializer = serializer.PuzzleStatementSerializer()
    self.game = None
    self.configuration = model.Configuration()
    self.validator = None
    self._threads = []

  def load_game(self, fname):
    with open(fname, 'r') as fh:
      self.game = self.serializer.deserialize(fh.read())
    
    self.validator = validator.PuzzleValidator(self.game)
      
    return self.game

  def reset_game(self):
    for line in self.game.lines:
      line.state = model.Line.STATE_UNKNOWN

  def new_game(self):
    if self.configuration.model == model.Puzzle.MODEL_GRID:
      self.game = generator.grid(*self.configuration.size)
      self.validator = validator.PuzzleValidator(self.game)
    else:
      raise Exception('Could not recognize puzzle type \'{}\''.format(self.configuration.model))
