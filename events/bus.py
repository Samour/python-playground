import time


class ISubscribable:

  def register_subscriber(self, subscriber):
    pass


class IEventBus(ISubscribable):

  @property
  def events_head(self):
    pass

  def get_event(self, i):
    pass
  
  def emit(self, event):
    pass


class EventBus(IEventBus):

  def __init__(self):
    self._events = []
    self._subscribers = []

  @property
  def events_head(self):
    return len(self._events)

  def get_event(self, i):
    return self._events[i]

  def emit(self, event):
    self._events.append(event)
    for subscriber in self._subscribers:
      subscriber.receive(event)

  def register_subscriber(self, subscriber):
    self._subscribers.append(subscriber)


class IEvent:
  pass


class ISubscriber:

  def subscribe(self, subscribable):
    pass


class IEventListener(ISubscriber):

  def receive(self, event):
    pass


class IEventListenerAsync(IEventListener):

  def start(self, wait_timeout=0):
    pass
  
  def stop(self):
    pass


class EventListenerSync(IEventListener):

  def subscribe(self, subscribable):
    subscribable.register_subscriber(self)


class EventListenerAsync(IEventListener):

  def __init__(self):
    self._i = 0
    self._running = False
    self._event_bus = None

  def subscribe(self, event_bus):
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
