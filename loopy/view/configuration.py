import tkinter as tk
import model


class Configuration(tk.Toplevel):

  def __init__(self, master, configuration):
    super().__init__()
    self.master = master
    self.configuration = configuration.clone()
    self.create_widgets()

  def create_widgets(self):
    self.root_frame = tk.Frame(self)
    self.root_frame.pack(padx = 5, pady = 5)
    self.width_inpt = self._render_input('Width', self.configuration.size[0])
    self.height_inpt = self._render_input('Height', self.configuration.size[1])
    self.puzzle_type_var = self._render_select('Model', self.configuration.model, [model.Puzzle.MODEL_GRID])
    self.step_pause_time_inpt = self._render_input('Step pause time', self.master.controls.step_pause_time)

    self.close_btn = tk.Button(self.root_frame, text = 'Close', command = self.destroy)
    self.close_btn.pack(side = 'left')
    self.save_btn = tk.Button(self.root_frame, text = 'Save', command = self.save)
    self.save_btn.pack(side = 'right', padx = 10)

  def _render_input(self, text, value):
    frame = tk.Frame(self.root_frame)
    frame.pack(pady = 5)
    label = tk.Label(frame, text = text)
    label.pack(side = 'left')
    input = tk.Entry(frame) # TODO try to make this not full
    input.insert(0, value)
    input.pack(side = 'right' )

    return input

  def _render_select(self, text, value, options):
    frame = tk.Frame(self.root_frame)
    frame.pack(pady = 5)
    label = tk.Label(frame, text = text)
    label.pack(side = 'left')
    var = tk.StringVar(self, value)
    select = tk.OptionMenu(frame, var, *options)
    select.pack(side = 'right')

    return var

  def destroy(self):
    super().destroy()
    self.master.configuration = None

  def save(self):
    configuration = model.Configuration()
    configuration.size = [
      int(self.width_inpt.get()),
      int(self.height_inpt.get())
    ]
    configuration.model = self.puzzle_type_var.get()
    
    self.master.manager.configuration = configuration
    self.master.controls.step_pause_time = int(self.step_pause_time_inpt.get())
    self.destroy()
