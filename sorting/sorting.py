import math
import events


class ComparisonEvent:

  def __init__(self, i, j):
    self.i = i
    self.j = j


class SwitchEvent:

  def __init__(self, i, j):
    self.i = i
    self.j = j


class ListState:

  def __init__(self, lst, event_bus):
    self.list = lst
    self._event_bus = event_bus

  def compare(self, i, j):
    self._event_bus.emit(ComparisonEvent(i, j))
    if self.list[i] < self.list[j]:
      return -1
    elif self.list[i] == self.list[j]:
      return 0
    else:
      return 1

  def swap(self, i, j):
    self.list[i], self.list[j] = self.list[j], self.list[i]
    self._event_bus.emit(SwitchEvent(i, j))


class BaseSorter:

  def __init__(self, list_state):
    self.list_state = list_state

  def sort(self):
    pass


class InsertionSort(BaseSorter):

  def sort(self):
    list_s = len(self.list_state.list)
    sorted = list_s
    while sorted > 0:
      for i in range(sorted - 1, list_s - 1):
        if self.list_state.compare(i, i + 1) > 0:
          self.list_state.swap(i, i + 1)
        else:
          break
      sorted -= 1


class SelectionSort(BaseSorter):

  def sort(self):
    list_s = len(self.list_state.list)
    for i in range(list_s):
      l = i
      for j in range(i + 1, list_s):
        if self.list_state.compare(j, l) < 0:
          l = j
      if l != i:
        self.list_state.swap(i, l)


class BubbleSort(BaseSorter):

  def sort(self):
    sorted = len(self.list_state.list)
    while sorted > 0:
      ran = range(sorted - 1)
      sorted = 0
      for i in ran:
        if self.list_state.compare(i, i + 1) > 0:
          self.list_state.swap(i, i + 1)
          sorted = i + 1


class CocktailShakerSort(BaseSorter):

  def sort(self):
    sorted_upper = len(self.list_state.list)
    sorted_lower = 0
    direction = 1
    while sorted_lower < sorted_upper:
      if direction == 1:
        ran = range(sorted_lower, sorted_upper - 1)
        sorted_upper = sorted_lower
      else:
        ran = range(sorted_upper - 1, sorted_lower - 1, -1)
        sorted_lower = sorted_upper
      for i in ran:
        if self.list_state.compare(i, i + 1) > 0:
          self.list_state.swap(i, i + 1)
          if direction == 1:
            sorted_upper = i + 1
          else:
            sorted_lower = i
      direction *= -1


class MergeSort(BaseSorter):

  def sort(self):
    self._sort_range(0, len(self.list_state.list))

  def _sort_range(self, i, j):
    if j - i < 2:
      return

    split = math.floor((j + i) / 2)
    self._sort_range(i, split)
    self._sort_range(split, j)

    i_i = i
    j_i = split
    result = []
    while i_i < split and j_i < j:
      if self.list_state.compare(i_i, j_i) > 0:
        result.append(j_i - i)
        j_i += 1
      else:
        result.append(i_i - i)
        i_i += 1
    while i_i < split:
      result.append(i_i - i)
      i_i += 1
    while j_i < j:
      result.append(j_i - i)
      j_i += 1
    
    # Breaks O(ln(N)) performance, but will look good for render
    for k in range(len(result)):
      swap = result[k]
      if k != swap:
        self.list_state.swap(k + i, swap + i)
        result[k] = k
        for n in range(len(result)):
          if result[n] == k:
            result[n] = swap


class QuickSort(BaseSorter):

  def sort(self):
    self._sort_range(0, len(self.list_state.list))

  def _sort_range(self, i, j):
    if j - i < 2:
      return

    pivot = i
    i_i = i + 1
    j_i = j - 1
    cache_i_gt = False # Just to reduce some redundant compare calls
    while i_i < j_i:
      if not cache_i_gt and self.list_state.compare(i_i, pivot) <= 0:
        i_i += 1
      elif self.list_state.compare(j_i, pivot) > 0:
        j_i -= 1
        cache_i_gt = True
      else:
        self.list_state.swap(i_i, j_i)
        cache_i_gt = False

    if self.list_state.compare(i_i, pivot) <= 0:
      if i_i != pivot:
        self.list_state.swap(i_i, pivot)
        pivot = i_i
    else:
      if i_i - 1 != pivot:
        self.list_state.swap(i_i - 1, pivot)
        pivot = i_i - 1

    self._sort_range(i, pivot)
    self._sort_range(pivot + 1, j)


class HeapSort(BaseSorter):

  def sort(self):
    list_s = len(self.list_state.list)
    heap_size = 1
    while heap_size < list_s:
      heap_size += 1
      self._bubble_val(heap_size)

    while heap_size > 1:
      self.list_state.swap(0, heap_size - 1)
      heap_size -= 1
      self._sink_value(1, heap_size)

  def _bubble_val(self, i):
    h = math.floor(i / 2)
    if i > 1 and self.list_state.compare(i - 1, h - 1) > 0:
      self.list_state.swap(i - 1, h - 1)
      self._bubble_val(h)

  def _sink_value(self, i, heap_size):
    l = i * 2
    r = l + 1
    l_l = l <= heap_size and self.list_state.compare(i - 1, l - 1) < 0
    r_l = r <= heap_size and self.list_state.compare(i - 1, r - 1) < 0
    if l_l or r_l:
      if not r_l or self.list_state.compare(l - 1, r - 1) >= 0:
        self.list_state.swap(i - 1, l - 1)
        self._sink_value(l, heap_size)
      else:
        self.list_state.swap(i - 1, r - 1)
        self._sink_value(r, heap_size)
