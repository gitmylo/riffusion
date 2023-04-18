import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.ttk import Notebook

from PIL import Image
from gui.tab import Tab
from riffusion.cli import audio_to_image
import os
import shutil
from scripts.imagetoaudio import image_to_audio
from threading import Thread
from playsound import playsound
from PIL import ImageTk


def remake_dir(directory: str):
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


def play_audio_file():
    playsound("tmp/.wav", False)


class Previewer(Tab):
    def __init__(self):
        self.file_name: str = ""
        self.open_file: tk.Button = None
        self.preview_image: tk.Canvas = None
        self.play_file: tk.Button = None
        self.save_file_png: tk.Button = None
        self.save_file_wav: tk.Button = None
        self.file_type_both: tuple[str, str] = ("Images or audio files", "*.png;*.wav")
        self.file_type_png: tuple[str, str] = ("Images", "*.png")
        self.file_type_wav: tuple[str, str] = ("Audio files", "*.wav")
        self.file_types: tuple = (self.file_type_both, self.file_type_wav, self.file_type_png)

    def open_file_dialog(self):
        file_name = fd.askopenfilename(title="Open an image or Audio file", filetypes=self.file_types)
        if file_name == "":
            return
        Thread(target=self.perform_conversions_threaded, args=(file_name,)).start()

    def perform_conversions_threaded(self, file_name: str):
        self.open_file["state"] = tk.DISABLED
        self.play_file["state"] = tk.DISABLED
        self.save_file_wav["state"] = tk.DISABLED
        self.save_file_png["state"] = tk.DISABLED
        try:
            file_ext_name = os.path.splitext(file_name)[1].lower()
            remake_dir("tmp")
            shutil.copyfile(file_name, f"tmp/{file_ext_name}")
            match file_ext_name:
                case ".png":
                    image_to_audio(image="tmp/.png", audio="tmp/.wav")
                case ".wav":
                    audio_to_image(audio="tmp/.wav", image="tmp/.png")
                case _:  # This case should never match due to the file selector not allowing these files to be selected
                    print("Unable to load this file, not a supported type. Supported types: [\".png\", \".wav\"]")
            self.play_file["state"] = tk.NORMAL
            self.save_file_wav["state"] = tk.NORMAL
            self.save_file_png["state"] = tk.NORMAL
            el_width = self.preview_image.winfo_width()
            x_offset_base = el_width / 2
            image_open = Image.open("tmp/.png")
            new_img = ImageTk.PhotoImage(image_open)
            x_offset = image_open.width / 2
            self.preview_image.create_image(x_offset_base - x_offset, 0, image=new_img, anchor=tk.NW, tags="IMG")
            self.preview_image.image = new_img
        except Exception as e:
            print(e)
        self.open_file["state"] = tk.NORMAL

    def save_png(self):
        file_name = fd.asksaveasfilename(title="Save .png", filetypes=(self.file_type_png,))
        if file_name == "":
            return
        if not file_name.endswith(".png"):
            file_name += ".png"
        shutil.copyfile("tmp/.png", file_name)
        print(f"Saved {file_name}")

    def save_wav(self):
        file_name: str = fd.asksaveasfilename(title="Save .png", filetypes=(self.file_type_wav,))
        if file_name == "":
            return
        if not file_name.endswith(".wav"):
            file_name += ".wav"
        shutil.copyfile("tmp/.wav", file_name)
        print(f"Saved {file_name}")

    def create_element(self, root: Notebook):
        tab = ttk.Frame(root)
        top_label = tk.Label(tab, text="Preview and export files", anchor="w", font=("arial", 15))
        top_label.pack(fill="x")

        self.open_file = tk.Button(tab, text="Open file", command=self.open_file_dialog)
        self.open_file.pack(fill="x")

        self.play_file = tk.Button(tab, text="Play opened file audio (Requires you to have opened a file first)",
                                   state=tk.DISABLED, command=play_audio_file)
        self.play_file.pack(fill="x")

        save_frame = tk.Frame(tab)
        save_frame.pack(fill="x")
        self.save_file_png = tk.Button(save_frame, text="Save .png file (Requires you to have opened a file first)",
                                       state=tk.DISABLED, command=self.save_png)
        self.save_file_png.pack(side=tk.LEFT)
        self.save_file_wav = tk.Button(save_frame, text="Save .wav file (Requires you to have opened a file first)",
                                       state=tk.DISABLED, command=self.save_wav)
        self.save_file_wav.pack(side=tk.RIGHT)

        self.preview_image = tk.Canvas(tab, bd=0, highlightthickness=0)
        self.preview_image.pack()

        return tab
