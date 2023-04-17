from tkinter import *
from tkinter import ttk
from sharedinfo import WrapMode
from audiotoimageconverter import run
from threading import Thread


def get_textbox_value(textbox):
    return textbox.get("1.0", "end").replace("\n", "")


def create_element(root):
    tab = ttk.Frame(root)
    top_label = Label(tab, text="Process audio files to trainable data.", anchor="w", font=("arial", 15))
    top_label.pack(fill="x")

    # start section directories
    dir_separator = ttk.Separator(tab, orient="horizontal")
    dir_separator.pack(fill="x")

    dir_label = Label(tab, text="Directories.", anchor="w", font=("arial", 15))
    dir_label.pack(fill="x")

    # input directory
    in_dir_l = Label(tab, text="Input directory", anchor="w")
    in_dir_l.pack(fill="x")
    in_dir = Text(tab, height=1)
    in_dir.insert(END, "!input")
    in_dir.pack(fill="x")

    # processing directory
    proc_dir_l = Label(tab, text="Processing directory (no need to change)", anchor="w")
    proc_dir_l.pack(fill="x")
    proc_dir = Text(tab, height=1)
    proc_dir.insert(END, "!processing")
    proc_dir.pack(fill="x")

    # output directory
    out_dir_l = Label(tab, text="Output directory", anchor="w")
    out_dir_l.pack(fill="x")
    out_dir = Text(tab, height=1)
    out_dir.insert(END, "!output")
    out_dir.pack(fill="x")

    # start section settings
    set_separator = ttk.Separator(tab, orient="horizontal")
    set_separator.pack(fill="x")

    set_label = Label(tab, text="Settings.", anchor="w", font=("arial", 15))
    set_label.pack(fill="x")

    # backwards_if_not_fit
    backwards_if_not_fit = IntVar(tab)
    backwards_if_not_fit.set(1)
    backwards = Checkbutton(tab, text="Rerun backwards if not a multiple of the chunk jump setting (overlap for better training)",
                            anchor="w", variable=backwards_if_not_fit)
    backwards.select()
    backwards.pack(fill="x")

    # chunk_jump
    chunk_jump_l = Label(tab, text="Chunk jump (amount to jump, use lower than 512 for overlap. "
                                   "higher than 512 not recommended.)", anchor="w")
    chunk_jump_l.pack(fill="x")
    chunk_jump = Text(tab, height=1)
    chunk_jump.insert(END, "512")
    chunk_jump.pack(fill="x")

    # wrap_mode
    wrap_mode_l = Label(tab, text="Wrap mode (SKIP=\"Skip files under 512px.\", "
                                  "FILL=\"Fill empty space with silence.\", REPEAT=\"Repeat the clip to fill.\").",
                        anchor="w")
    wrap_mode_l.pack(fill="x")
    wrap_mode_options = [option.value for option in WrapMode]
    wrap_mode_val = StringVar(tab)
    wrap_mode_val.set(WrapMode.REPEAT.value)
    wrap_mode = OptionMenu(tab, wrap_mode_val, *wrap_mode_options)
    wrap_mode.pack(fill="x")

    # start section run
    run_separator = ttk.Separator(tab, orient="horizontal")
    run_separator.pack(fill="x")

    # run button
    run_button = Button(tab, text="Run script (Check console for progress)",
                        command=lambda: Thread(target=run, args=(backwards_if_not_fit.get() == 1,
                                                                 int(get_textbox_value(chunk_jump)),
                                                                 wrap_mode_val.get(),
                                                                 get_textbox_value(in_dir),
                                                                 get_textbox_value(proc_dir),
                                                                 get_textbox_value(out_dir)))
                        .start())
    run_button.pack(fill="x")
    return tab
