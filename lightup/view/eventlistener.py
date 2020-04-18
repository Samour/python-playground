import events

EVENTS_LOG = False


class ApplicationEventListener(events.EventListenerAsync, events.ISubscribable):

  def __init__(self, application):
    super().__init__()
    self._application = application
    self._listeners = []

  def register_listener(self, listener):
    self._listeners.append(listener)

  def start(self, wait_timeout=0):
    self._log_msg('{} started', type(self).__name__)
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
    self._log_event(event)

    for listener in self._listeners:
      listener.receive(event)

  def _log_msg(self, msg, *args):
    if not EVENTS_LOG:
      return

    print(msg.format(*args))

  def _log_event(self, event):
    self._log_msg('{} received event {}', type(self).__name__, type(event).__name__)
    self._log_msg('\t{}', event)