from tkinter import ttk, Tk
from gui.audiotoimagegui import AudioToImageGui
from gui.previewer import Previewer


def create_tabcontrol(root: Tk):
    tabs = ttk.Notebook(root)
    tabs.add(Previewer().create_element(tabs), text="Preview and save")
    tabs.add(AudioToImageGui().create_element(tabs), text="Audio to image")
    return tabs
