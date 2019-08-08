import random
import time
import math
import events


MAX_RAND_VAL = 10000


class ForkIfAvailableThreadPool:

  def __init__(self, pool_size):
    self.pool_size = pool_size
    self.threads = []

  


def make_list(size):
  lst = []
  while len(lst) < size:
    lst.append(random.randint(0, MAX_RAND_VAL))
  
  return lst


class SortResult:

  def __init__(self, label, sort_time, is_sorted):
    self.label = label
    self.sort_time = sort_time
    self.is_sorted = is_sorted


class ISort:

  def __init__(self):
    self.comparison_count = 0
    self.assign_count = 0
    self.debug = False

  def sort(self, lst):
    pass

  def reset_counts(self):
    self.comparison_count = 0
    self.assign_count = 0


class SelectionSort(ISort):

  def sort(self, lst):
    sorted_list = list(lst)
    if self.debug:
      self.assign_count += len(sorted_list)
    for i in range(len(sorted_list)):
      min_idx = i
      for j in range(i + 1, len(sorted_list)):
        if self.debug:
          self.comparison_count += 1
        if sorted_list[j] < sorted_list[min_idx]:
          min_idx = j
      sorted_list[i], sorted_list[min_idx] = sorted_list[min_idx], sorted_list[i]
      if self.debug:
        self.assign_count += 2
    
    return sorted_list


class InsertionSort(ISort):

  def sort(self, lst):
    sorted_list = []
    for i in range(len(lst)):
      for j in range(len(sorted_list)):
        if self.debug:
          self.comparison_count += 1
        if lst[i] < sorted_list[j]:
          sorted_list = sorted_list[:j] + [lst[i]] + sorted_list[j:]
          if self.debug:
            self.assign_count += 1
          break
      if len(sorted_list) is i:
        sorted_list.append(lst[i])
        if self.debug:
          self.assign_count += 1

    return sorted_list


class BubbleSort(ISort):

  def sort(self, lst):
    sorted_list = list(lst)
    if self.debug:
      self.assign_count += len(sorted_list)
    last_swap = len(sorted_list)
    while last_swap > 0:
      generator = range(last_swap - 1)
      last_swap = 0
      for i in generator:
        if self.debug:
          self.comparison_count += 1
        if sorted_list[i] > sorted_list[i + 1]:
          sorted_list[i], sorted_list[i + 1] = sorted_list[i + 1], sorted_list[i]
          last_swap = i + 1
          if self.debug:
            self.assign_count += 2
    
    return sorted_list


class MergeSort(ISort):

  def __init__(self, thread_pool):
    super().__init__()
    self._thread_pool = thread_pool

  def sort(self, lst):
    if len(lst) < 2:
      return lst

    h = math.floor(len(lst) / 2)
    if self.debug:
      self.assign_count += len(lst)
    left_fut = self._dispatch_sort_task(lst[:h])
    right_fut = self._dispatch_sort_task(lst[h:])
    left = left_fut
    right = right_fut
    l = 0
    r = 0
    sorted_list = []
    while l < len(left) and r < len(right):
      if self.debug:
        self.comparison_count += 1
      if right[r] < left[l]:
        sorted_list.append(right[r])
        if self.debug:
          self.assign_count += 1
        r += 1
      else:
        sorted_list.append(left[l])
        if self.debug:
          self.assign_count += 1
        l += 1
    sorted_list += left[l:]
    sorted_list += right[r:]
    if self.debug:
      self.assign_count += l + r

    return sorted_list

  def _dispatch_sort_task(self, lst):
    if len(lst) < 50000 or self.debug:
      return self.sort(lst)
    else:
      return self._thread_pool.dispatch(self.sort(lst))


class IPartition:

  def start_partition(self, lst):
    pass

  @property
  def is_thread_safe(self):
    pass


class IPartitionSupplier:

  def get_partition(self, lst):
    pass


class QuickSort(ISort):

  def __init__(self, partition, thread_pool):
    super().__init__()
    self.partition = partition
    self._thread_pool = thread_pool

  def sort(self, lst):
    return self._sort(lst, self.partition.start_partition(lst))

  def _sort(self, lst, partition_supplier):
    part_value = partition_supplier.get_partition(lst)
    all_are_same = True
    initial_value = None
    lower = []
    parts = []
    upper = []
    for x in lst:
      if initial_value is None:
        initial_value = x
      elif x != initial_value:
        all_are_same = False

      if x < part_value:
        if self.debug:
          self.comparison_count += 1
        lower.append(x)
      else:
        if self.debug:
          self.comparison_count += 2
        if x is part_value:
          parts.append(x)
        else:
          upper.append(x)
      
    if self.debug:
      self.assign_count += 2 * (len(lower) + len(parts) + len(upper))
    if all_are_same:
      return lower + parts + upper
    else:
      return self._sort(lower, partition_supplier) + parts + self._sort(upper, partition_supplier)


class PartitionOnFirstElementSupplier(IPartitionSupplier):

  def get_partition(self, lst):
    return 0 if len(lst) is 0 else lst[0]


class PartitionOnFirstElement(IPartition):

  def start_partition(self, lst):
    return PartitionOnFirstElementSupplier()

  @property
  def is_thread_safe(self):
    return True


class MidValueTreeNode:

  def __init__(self, parent_node, lower, upper = None):
    if upper is not None:
      self.lower = lower
      self.upper = upper
      self.parent_node = parent_node
    else:
      self.lower = parent_node
      self.upper = lower
      self.parent_node = None
    self._left_child = None
    self._right_child = None
    self.avg = (self.lower + self.upper) / 2
    self.walk_length = 0
    self.debug = False

  def walk_to_node(self, val):
    if self.debug:
      self.walk_length += 1
    if val > self.upper:
      return self.parent_node.walk_to_node(val)

    if self._left_child is None:
      self._left_child = MidValueTreeNode(self, self.lower, self.avg)
      self._right_child = MidValueTreeNode(self, self.avg, self.upper)
      return self
    elif val <= self.avg:
      return self._left_child.walk_to_node(val)
    else:
      return self._right_child.walk_to_node(val)

  @property
  def total_walk_length(self):
    walk_length = self.walk_length
    if self._left_child is not None:
      walk_length += self._left_child.total_walk_length
    if self._right_child is not None:
      walk_length += self._right_child.total_walk_length
    
    return walk_length


class PartitionOnMidValSupplier(IPartitionSupplier):

  def __init__(self, lst):
    rMin = None
    rMax = None
    for x in lst:
      if rMin is None or x < rMin:
        rMin = x
      if rMax is None or x > rMax:
        rMax = x
    self._avg_tree = MidValueTreeNode(rMin, rMax)
    self._tree_walk_pos = self._avg_tree

  def get_partition(self, lst):
    if len(lst) is 0:
      return 0
    else:
      self._tree_walk_pos = self._tree_walk_pos.walk_to_node(lst[0])
      return self._tree_walk_pos.avg


class PartitionOnMidVal(IPartition):

  def start_partition(self, lst):
    return PartitionOnMidValSupplier(lst)

  @property
  def is_thread_safe(self):
    return False


class HeapSort(ISort):

  def __init__(self):
    super().__init__()
    self._heap = []
    self._heap_top = 0

  def sort(self, lst):
    self._heap = [None for i in lst]
    self._heap_top = 0
    for v in lst:
      self._insert_value(v)
    sorted_list = []
    while self._heap_top > 0:
      sorted_list.append(self._pop_value())
      if self.debug:
        self.assign_count += 1

    return sorted_list

  def _insert_value(self, v):
    self._heap[self._heap_top] = v
    if self.debug:
      self.assign_count += 1
    i = self._heap_top
    self._heap_top += 1
    while i > 0:
      ih = math.floor((i + 1) / 2) - 1
      if self.debug:
        self.comparison_count += 1
      if self._heap[i] < self._heap[ih]:
        self._heap[i], self._heap[ih] = self._heap[ih], self._heap[i]
        if self.debug:
          self.assign_count += 2
        i = ih
      else:
        return

  def _pop_value(self):
    val = self._heap[0]
    self._heap_top -= 1
    self._heap[0], self._heap[self._heap_top] = self._heap[self._heap_top], None
    if self.debug:
      self.assign_count += 2
    i = 0
    while True:
      ival = self._get_heap_pos(i)
      l = i * 2 + 1
      lval = self._get_heap_pos(l)
      r = i * 2 + 2
      rval = self._get_heap_pos(r)
      if self._gt_either(ival, lval, rval):
        if rval is None or lval < rval:
          self._heap[i], self._heap[l] = lval, ival
          if self.debug:
            self.assign_count += 2
          i = l
        else:
          self._heap[i], self._heap[r] = rval, ival
          if self.debug:
            self.assign_count += 2
          i = r
      else:
        return val

  def _gt_either(self, top, left, right):
    if left is not None and top > left:
      if self.debug:
        self.comparison_count += 1
      return True
    elif right is not None and top > right:
      if self.debug:
        self.comparison_count += 2
      return True
    else:
      if self.debug:
        self.comparison_count += 2
      return False

  def _get_heap_pos(self, i):
    return self._heap[i] if i < len(self._heap) else None


def is_sorted(lst):
  last = None
  for x in lst:
    if last is not None and x < last:
      return False
    last = x

  return True


def do_and_time_sort(lst, strategy):
  start = time.time()
  sorted_list = strategy.sort(lst)
  end = time.time()

  return end - start, is_sorted(sorted_list)


class ListSortedEvent:

  def __init__(self, sorter, sort_result):
    self.sorter = sorter
    self.sort_result = sort_result


def run_algorithms(lst, algs, event_emitter):
  result = []
  for spec in algs:
    spec[1].reset_counts()
    start = time.time()
    sorted_list = spec[1].sort(lst)
    end = time.time()
    
    result_line = SortResult(spec[0], end - start, is_sorted(sorted_list))
    event_emitter.emit(ListSortedEvent(spec[1], result_line))
    result.append(result_line)

  return result


class ListSortedEventListener(events.IEventListener):

  def receive(self, event, emitter):
    if isinstance(event, ListSortedEvent):
      base_tmpl = '{}: {:6f}s ({})'
      if event.sorter.debug:
        print((base_tmpl + ' - {:,} comparisons, {:,} assignments').format(
          event.sort_result.label,
          event.sort_result.sort_time,
          'sorted' if event.sort_result.is_sorted else 'not sorted',
          event.sorter.comparison_count,
          event.sorter.assign_count
        ))
      else:
        print(base_tmpl.format(
          event.sort_result.label,
          event.sort_result.sort_time,
          'sorted' if event.sort_result.is_sorted else 'not sorted'
        ))
    

LIST_LENGTH = 50000


def main():
  event_bus = events.EventBus()
  event_bus.register(ListSortedEventListener())
  sort_event_emitter = events.DefaultEventEmitter(event_bus)

  lst = make_list(LIST_LENGTH)
  strategies = [
    # ('Selection sort', SelectionSort()),
    # ('Insertion sort', InsertionSort()),
    # ('Bubble sort', BubbleSort()),
    ('Merge sort (single-threaded)', MergeSort()),
    ('Merge sort (multi-threaded)', MergeSort()),
    # ('Quick sort (first element)', QuickSort(PartitionOnFirstElement(), thread_pool)),
    # ('Quick sort (mid value)', QuickSort(PartitionOnMidVal(), thread_pool)),
    # ('Heap sort', HeapSort())
  ]

  result = loop.run_until_complete(run_algorithms(lst, strategies, sort_event_emitter))

if __name__ == '__main__':
  main()