class EventBus:

  def __init__(self):
    self._listeners = []

  def register(self, listener):
    self._listeners.append(listener)

  def deregister(self, listener):
    self._listeners = list(filter(
      lambda l: not l is listener,
      self._listeners
    ))

  def emit(self, event):
    for listener in self._listeners:
      listener.receive(event)


class IEventListener:

  def receive(self, event):
    pass
