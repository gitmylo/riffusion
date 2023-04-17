from tkinter import ttk
from gui.audiotoimagegui import create_element as ati_gui


def create_tabcontrol(root):
    tabs = ttk.Notebook(root)
    tabs.add(ati_gui(tabs), text="audio to image")
    return tabs
