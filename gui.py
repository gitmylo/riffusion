from tkinter import *
from gui.tabcontrol import create_tabcontrol
from torch import cuda

print(f"Cuda available: {cuda.is_available()}")

root = Tk()

root.title("Riffusion-scripts gui")

root.geometry("700x400")
root.resizable(False, False)


tabcontrol = create_tabcontrol(root)
tabcontrol.pack(side="top", fill="both", expand=True)

root.mainloop()
