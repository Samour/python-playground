class IReversableStore:

  def apply_update(self, update):
    pass

  def reverse_update(self, update):
    pass


class BackTrack:

  def __init__(self, state_manager):
    self._state_manager = state_manager
    self._mutations = []
    self._guesses = []

  def update(self, mutation, guess):
    self._mutations.append(mutation)
    if guess:
      self._guesses.append(mutation)
    self._state_manager.apply_update(mutation)

  def rollback_guess(self):
    last_guess = self._guesses.pop()
    last_mutation = None
    while last_mutation != last_guess:
      last_mutation = self._mutations.pop()
      self._state_manager.reverse_update(last_mutation)
    
    return last_guess
