import tkinter as tk
import sorting


class Configuration(tk.Toplevel):

  _ALGORITHM_INSERTION = 'Insertion sort'
  _ALGORITHM_SELECTION = 'Selection sort'
  _ALGORITHM_BUBBLE = 'Bubble sort'
  _ALGORITHM_COCKTAIL = 'Cocktail shaker sort'
  _ALGORITHM_MERGE = 'Merge sort'
  _ALGORITHM_QUICK = 'Quick sort'
  _ALGORITHM_HEAP = 'Heap sort'

  _ALGORITHMS = [
    _ALGORITHM_INSERTION,
    _ALGORITHM_SELECTION,
    _ALGORITHM_BUBBLE,
    _ALGORITHM_COCKTAIL,
    _ALGORITHM_MERGE,
    _ALGORITHM_QUICK,
    _ALGORITHM_HEAP
  ]

  _ALGORITHM_IMPL = {
    _ALGORITHM_INSERTION: sorting.InsertionSort,
    _ALGORITHM_SELECTION: sorting.SelectionSort,
    _ALGORITHM_BUBBLE: sorting.BubbleSort,
    _ALGORITHM_COCKTAIL: sorting.CocktailShakerSort,
    _ALGORITHM_MERGE: sorting.MergeSort,
    _ALGORITHM_QUICK: sorting.QuickSort,
    _ALGORITHM_HEAP: sorting.HeapSort
  }

  def __init__(self, master):
    super().__init__(master)
    self.master = master
    self.render_widgets()

  def render_widgets(self):
    self.list_size = self._render_val('List size', self.master.list_size)
    self.list_range = self._render_val('List range', self.master.list_range)
    self.step_count = self._render_val('Step count', self.master.step_count)
    self.step_pause = self._render_val('Step pause (ms)', self.master.step_pause)
    self.sort_alg = self._render_alg_select()
    base_frame = tk.Frame(self)
    base_frame.pack(pady = 5)
    close_btn = tk.Button(base_frame, text = 'Cancel', command = self.destroy)
    close_btn.pack(side = 'left', padx = 5)
    save_btn = tk.Button(base_frame, text = 'Save', command = self._save)
    save_btn.pack(side = 'right', padx = 5)

  def _render_val(self, text, value):
    frame = tk.Frame(self)
    frame.pack(pady = 5)
    label = tk.Label(frame, text = text)
    label.pack(side = 'left', padx = 5)
    val = tk.Entry(frame)
    val.insert(0, value)
    val.pack(side = 'right', padx = 5)

    return val

  def _render_alg_select(self):
    frame = tk.Frame(self)
    frame.pack(pady = 5)
    label = tk.Label(frame, text = 'Algorithm')
    label.pack(side = 'left', padx = 5)
    val = tk.StringVar(frame)
    for text in self._ALGORITHM_IMPL:
      if self._ALGORITHM_IMPL[text] is self.master.sort_alg:
        val.set(text)
        break
    opt = tk.OptionMenu(frame, val, *self._ALGORITHMS)
    opt.pack(side = 'right', padx = 5)

    return val

  def _save(self):
    try:
      list_size = int(self.list_size.get())
      list_range = int(self.list_range.get())
      step_count = int(self.step_count.get())
      step_pause = int(self.step_pause.get())
      sort_alg = self._ALGORITHM_IMPL[self.sort_alg.get()]

      self.master.list_size = list_size
      self.master.list_range = list_range
      self.master.step_count = step_count
      self.master.step_pause = step_pause
      self.master.sort_alg = sort_alg
      self.destroy()
    except:
      pass
