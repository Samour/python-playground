class IEventEmitter:

  def emit(self, event):
    pass


class DefaultEventEmitter(IEventEmitter):

  def __init__(self, bus):
    self.bus = bus

  def emit(self, event):
    self.bus.emit(event, self)


class IEventListener:

  def receive(self, event, emitter):
    pass


class EventBus:

  def __init__(self):
    self._listeners = []

  def register(self, listener):
    self._listeners.append(listener)

  def emit(self, event, emitter):
    for listener in self._listeners:
      listener.receive(event, emitter)
