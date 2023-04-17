import os
import shutil
from enum import Enum

from riffusion.cli import audio_to_image
from PIL import Image


class WrapMode(Enum):
    SKIP = 0  # Ignore files smaller than split_width (around 5 seconds)
    FILL = 1  # Fill the empty space with white (nothing)
    REPEAT = 2  # Repeat the clip to the correct pixel count


# settings
backwards_if_not_fit = True  # default: true, set this to true to take all audio from the end, useful if you have an overlap of 512
chunk_jump = 512  # default: 512, set this lower for more output files, with more overlap
wrap_mode = WrapMode.REPEAT  # default: WrapMode.REPEAT, what to do when a file is smaller than the split_width


def add_leading_zeroes(s, leading_zero):
    return f"{'0'*leading_zero}{s}"


def remake_dir(directory):
    if os.path.isdir(directory):
        shutil.rmtree(directory)
    os.mkdir(directory)


# preparation
in_dir = "!input"
proc_dir = "!processing"
out_dir = "!output"
counter = 0
split_width = 512

if not os.path.isdir(in_dir):
    os.mkdir(in_dir)
    print("created input dir, exiting")
    exit(0)
remake_dir(proc_dir)
remake_dir(out_dir)

for file in os.listdir(in_dir):
    path = f"{in_dir}/{file}"
    if not path.lower().endswith(".wav"):
        continue
    print(f"processing {path}")
    base_file_name = os.path.splitext(file)[0]
    proc_file_name = f"{proc_dir}/{base_file_name}"
    base_caption_path = f"{in_dir}/{base_file_name}.txt"
    save_image_path = f"{proc_file_name}.png"
    audio_to_image(audio=path, image=save_image_path)
    if wrap_mode != WrapMode.SKIP:
        image_object = Image.open(save_image_path)
        (width, height) = image_object.size
        if width < split_width:
            # too small, needs wrap_mode
            edit_image = Image.new(image_object.mode, (split_width, height), (255, 255, 255, 255))
            match wrap_mode:
                case WrapMode.FILL:
                    edit_image.paste(image_object, (0, 0))
                case WrapMode.REPEAT:
                    for x in range(0, split_width, width):
                        edit_image.paste(image_object, (x, 0))
                case _:
                    pass
            edit_image.save(save_image_path)
            image_object.close()
    if os.path.isfile(base_caption_path):
        shutil.copyfile(base_caption_path, f"{proc_file_name}.txt")
    else:
        caption_file = open(f"{proc_file_name}.txt", "w")
        caption_file.write(base_file_name)
        caption_file.close()


print("splitting files into chunks of 512px")
# splitting

for file in os.listdir(proc_dir):
    path = f"{proc_dir}/{file}"
    if not path.lower().endswith(".png"):
        continue
    print(f"processing {path}")
    img = Image.open(path)
    (width, height) = img.size
    diff = width % split_width
    caption_file = os.path.splitext(file)[0]
    print("first pass")
    for x in range(0, width - split_width + 1, chunk_jump):
        print(f"at {x}")
        box = (x, 0, x + split_width, height)
        filepath = f"{out_dir}/{add_leading_zeroes(counter, 5)}"
        img.crop(box).save(f"{filepath}.png")
        shutil.copyfile(f"{proc_dir}/{caption_file}.txt", f"{filepath}.txt")
        counter += 1
    if diff != 0 and width > split_width and backwards_if_not_fit:
        print("second pass (backwards)")
        for x in range(0, width - split_width + 1, chunk_jump):
            box = (width - (x + split_width), 0, width - x, height)
            filepath = f"{out_dir}/{add_leading_zeroes(counter, 5)}"
            img.crop(box).save(f"{filepath}.png")
            shutil.copyfile(f"{proc_dir}/{caption_file}.txt", f"{filepath}.txt")
            counter += 1
    img.close()

print("completed")
