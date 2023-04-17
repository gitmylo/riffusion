import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from gui.tab import Tab
from riffusion.cli import audio_to_image
import os
import shutil
from scripts.imagetoaudio import image_to_audio
from threading import Thread


def remake_dir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


class Previewer(Tab):
    def __init__(self):
        self.file_name: str = ""
        self.open_file: tk.Button = None
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

    def perform_conversions_threaded(self, file_name):
        self.open_file["state"] = tk.DISABLED
        file_ext_name = os.path.splitext(file_name)[1].lower()
        remake_dir("tmp")
        shutil.copyfile(file_name, f"tmp/{file_ext_name}")
        match file_ext_name:
            case ".png":
                image_to_audio(image="tmp/.png", audio="tmp/.wav")
            case ".wav":
                audio_to_image(audio="tmp/.wav", image="tmp/.png")
            case _:  # This case should never match due to the file selector not allowing these files to be selected.
                print("Unable to load this file, not a supported type. Supported types: [\".png\", \".wav\"]")
        self.open_file["state"] = tk.NORMAL

    def save_png(self):
        file_name = fd.asksaveasfilename(title="Save .png", filetypes=self.file_type_png)
        if file_name == "":
            return
        shutil.copyfile("tmp/.png", file_name)
        print(f"Saved {file_name}")

    def save_wav(self):
        file_name = fd.asksaveasfilename(title="Save .png", filetypes=self.file_type_wav)
        if file_name == "":
            return
        shutil.copyfile("tmp/.wav", file_name)
        print(f"Saved {file_name}")

    def create_element(self, root):
        tab = ttk.Frame(root)
        top_label = tk.Label(tab, text="Preview and export files", anchor="w", font=("arial", 15))
        top_label.pack(fill="x")

        self.open_file = tk.Button(tab, text="Open file", command=self.open_file_dialog)
        self.open_file.pack(fill="x")
        self.play_file = tk.Button(tab, text="Play opened file (Requires you to have opened a file first)",
                                   state=tk.DISABLED)
        self.play_file.pack(fill="x")

        save_frame = tk.Frame(tab)
        save_frame.pack(fill="x")
        self.save_file_png = tk.Button(save_frame, text="Save .png file (Requires you to have opened a file first)",
                                       state=tk.DISABLED)
        self.save_file_png.pack(side=tk.LEFT)
        self.save_file_wav = tk.Button(save_frame, text="Save .wav file (Requires you to have opened a file first)",
                                       state=tk.DISABLED)
        self.save_file_wav.pack(side=tk.RIGHT)
        return tab
