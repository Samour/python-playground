import threading
import asyncio


class ThreadPoolMember(threading.Thread):

  def __init__(self):
    super().__init__()
    self._loop = None

  def dispatch_task(self, method):
    return asyncio.wrap_future(asyncio.run_coroutine_threadsafe(method, self._loop))

  def run(self):
    self._loop = asyncio.new_event_loop()
    try:
      self._loop.run_forever()
    finally:
      self._loop.close()

  def kill(self):
    self.dispatch_task(self._stop_loop())
    
  async def _stop_loop(self):
    self._loop.stop()


class IThreadPool:

  def start_threads(self, count = None):
    pass

  def dispatch(self, method):
    pass
  
  def close_pool(self):
    pass


class RoundRobinThreadPool(IThreadPool):

  def __init__(self, threadpool_size):
    self.threadpool_size = threadpool_size
    self._threads = []
    self._next_thread = 0
    self._running = True
    self._lock = False

  def _acquire_lock(self):
    while self._lock:
      pass
    self._lock = True

  def _release_lock(self):
    self._lock = False

  def start_threads(self, count = None):
    self._acquire_lock()
    while len(self._threads) < self.threadpool_size and (count is None or len(self._threads) < count):
      self._start_new_thread()
    self._release_lock()

  def dispatch(self, method):
    self._acquire_lock()
    thread = self._get_available_thread()
    self._release_lock()

    return thread.dispatch_task(method)

  def _start_new_thread(self):
    thread = ThreadPoolMember()
    thread.start()
    self._threads.append(thread)
    
    return thread

  def _get_available_thread(self):
    if len(self._threads) == self._next_thread:
      self._start_new_thread()

    thread = self._threads[self._next_thread]
    self._next_thread += 1
    if self._next_thread == self.threadpool_size:
      self._next_thread = 0

    return thread

  def close_pool(self):
    for thread in self._threads:
      thread.kill()
    for thread in self._threads:
      thread.join()


class MockThreadPool(IThreadPool):

  def start_threads(self, count = None):
    pass

  async def dispatch(self, method):
    return await method

  def close_pool(self):
    pass