import events.bus as events


class ApplicationEventBridge(events.ISubscribable, events.IEventListenerAsync):

  def __init__(self, application):
    super().__init__()
    self._application = application
    self._subscribers = []
    self._event_bus = None
    self._i = 0

  def subscribe(self, event_bus):
    self._event_bus = event_bus

  def register_subscriber(self, subscriber):
    self._subscribers.append(subscriber)

  def start(self, wait_timeout=0):
    self._running = True
    self._event_listener_loop(wait_timeout)()

  def _event_listener_loop(self, wait_timeout):
    def cb():
      if not self._running:
        return
      
      while self._i < self._event_bus.events_head:
        self.receive(self._event_bus.get_event(self._i))
        self._i += 1
      
      if wait_timeout > 0:
        self._application.after(wait_timeout, self._event_listener_loop(wait_timeout))
    
    return cb

  def receive(self, event):
    for subscriber in self._subscribers:
      subscriber.receive(event)
