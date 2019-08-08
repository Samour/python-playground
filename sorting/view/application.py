import random
import time
import threading
import tkinter as tk
import view.controls
import view.configuration
import view.canvas
import events
import sorting


class SolverThread(threading.Thread, events.IEventListener):

  def __init__(self, master, sorter):
    super().__init__()
    self.main_thread_event_queue = []
    self._running = False
    self._locked = False
    self._master = master
    self._sorter = sorter
    self._steps_since_pause = 0
    self._step_pending_queue = []

  @property
  def running(self):
    return self._running

  def run(self):
    self._running = True
    try:
      self._sorter.sort()
      self._step_pending_queue.append(view.canvas.ResetHighlightsEvent())
      self._step_pending_queue.append(view.controls.SortStopEvent())
      self._send_pending_events()
    except InterruptedError:
      pass
    self._running = False

  def stop(self):
    if self._running:
      self._running = False
      self.join()

  def acquire_lock(self):
    while self._locked:
      pass
    self._locked = True

  def release_lock(self):
    self._locked = False

  def receive(self, event):
    if isinstance(event, sorting.ComparisonEvent) or isinstance(event, sorting.SwitchEvent):
      if not self._running:
        raise InterruptedError()
      compare = isinstance(event, sorting.ComparisonEvent)
      self._step_pending_queue.append(view.canvas.ResetHighlightsEvent())
      self._step_pending_queue.append(view.canvas.DrawBarEvent(event.i, self._sorter.list_state.list[event.i], compare, not compare))
      self._step_pending_queue.append(view.canvas.DrawBarEvent(event.j, self._sorter.list_state.list[event.j], compare, not compare))

      if self._master.step_count > 0 and self._master.step_pause > 0:
        self._steps_since_pause += 1
        if self._steps_since_pause >= self._master.step_count:
          self._send_pending_events()
          time.sleep(self._master.step_pause / 1000)
          self._steps_since_pause = 0

  def _send_pending_events(self):
    pending_events = []
    for event in self._step_pending_queue:
      if isinstance(event, view.canvas.ResetHighlightsEvent):
        if len(pending_events) == 0 or not isinstance(pending_events[0], view.canvas.ResetHighlightsEvent):
          pending_events.insert(0, view.canvas.ResetHighlightsEvent())
        for e2 in pending_events:
          if isinstance(e2, view.canvas.DrawBarEvent):
            e2.compare = False
            e2.swap = False
      else:
        pending_events.append(event)

    self._step_pending_queue = []

    self.acquire_lock()
    self.main_thread_event_queue.extend(pending_events)
    self.release_lock()


class Application(tk.Frame, events.IEventListener):

  def __init__(self, master):
    super().__init__(master)
    self.list_size = 100
    self.list_range = 1000
    self.step_count = 1
    self.step_pause = 10
    self.sort_alg = sorting.InsertionSort
    self._list = None
    self._sort_thread = None
    self.pack()
    self.render_widgets()
    self._register_listeners()

  def render_widgets(self):
    self.controls = view.controls.Controls(self)
    self.controls.pack(pady = 5)
    self.counts = view.canvas.EventCount(self)
    self.counts.pack(pady = 5)
    self.canvas = view.canvas.ListCanvas(self)
    self.canvas.pack()

  def _register_listeners(self):
    self._event_bus = events.EventBus()
    self._event_bus.register(self.controls)
    self._event_bus.register(self.counts)
    self._event_bus.register(self.canvas)
    self._event_bus.register(self)

  @property
  def sorting(self):
    return self._sort_thread is not None and self._sort_thread.running

  def new_list(self):
    self.counts.reset_counts()
    if not self.sorting:
      self._list = []
      for i in range(self.list_size):
        self._list.append(random.randint(0, self.list_range))
      self.canvas.draw_list(self._list)

  def run_sort(self):
    if self._list is None or self.sorting:
      return

    if self._sort_thread is not None:
      self._sort_thread.stop()
    
    self._sort_thread = SolverThread(self, self.sort_alg(sorting.ListState(self._list, self._event_bus)))
    self._sort_thread.start()
    self._emit_events_from_thread()

  def _emit_events_from_thread(self):
    if self._sort_thread is not None:
      self._sort_thread.acquire_lock()
      events = self._sort_thread.main_thread_event_queue
      self._sort_thread.main_thread_event_queue = []
      running = self._sort_thread.running
      self._sort_thread.release_lock()

      for event in events:
        self._event_bus.emit(event)

      if len(events) > 0:
        self.counts.write_counts()

      if running:
        self.after(1, self._emit_events_from_thread)

  # Proxy the events instead of registering the Thread directly to avoid dangling references
  def receive(self, event):
    if self._sort_thread is not None:
      self._sort_thread.receive(event)

  def stop_sort(self):
    if self._sort_thread is not None:
      self._sort_thread.stop()
      self._event_bus.emit(view.controls.SortStopEvent())

  def open_configuration(self):
    if not self.sorting:
      view.configuration.Configuration(self)

  def destroy(self):
    if self._sort_thread is not None:
      self._sort_thread.stop()
    super().destroy()


def main():
  root = tk.Tk()
  app = Application(master = root)
  root.mainloop()
