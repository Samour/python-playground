import time


class ISubscribable:

  def register_listener(self, listener):
    pass


class EventBus(ISubscribable):

  def __init__(self):
    self._events = []
    self._listeners = []

  @property
  def events_head(self):
    return len(self._events)

  def get_event(self, i):
    return self._events[i]

  def emit(self, event):
    self._events.append(event)
    for listener in self._listeners:
      listener.receive(event)

  def register_listener(self, listener):
    self._listeners.append(listener)


class IEvent:
  pass


class IEventListener:

  def receive(self, event):
    pass

  def register_bus(self, event_bus):
    pass


class EventListenerSync(IEventListener):

  def register_bus(self, event_bus):
    event_bus.register_listener(self)


class EventListenerAsync(IEventListener):

  def __init__(self):
    self._i = 0
    self._running = False
    self._event_bus = None

  def register_bus(self, event_bus):
    self._event_bus = event_bus

  def start(self, wait_timeout=0):
    self._running = True
    while self._running:
      while self._i < self._event_bus.events_head:
        self.receive(self._event_bus.get_event(self._i))
        self._i += 1
      
      if wait_timeout > 0:
        time.sleep(wait_timeout)
  
  def stop(self):
    self._running = False
