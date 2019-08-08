import tkinter as tk
import view.controls as controls
import view.canvas as canvas
import view.configuration as configuration
import manager
import solver


class Application(tk.Frame):

  def __init__(self, master = None):
    super().__init__(master)
    self.manager = manager.GameManager()
    self.master = master
    self.configuration = None
    self.lock_controls = False
    self.edit_mode = False
    self.pack()
    self.create_widgets()

  def create_widgets(self):
    self.controls = controls.GameControls(self)
    self.controls.pack()
    self.canvas = canvas.GameCanvas(self)
    self.canvas.pack()

    self.canvas.draw_new_game(self.manager.game)

  def open_configuration(self):
    if self.configuration is None:
      self.configuration = configuration.Configuration(self, self.manager.configuration)

  def destroy(self):
    self.controls.stop_alg()
    super().destroy()


def main():
  root = tk.Tk()
  app = Application(master = root)
  app.mainloop()
