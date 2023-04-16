import os
import shutil
from riffusion.cli import audio_to_image
from PIL import Image


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
    audio_to_image(audio=path, image=f"{proc_file_name}.png")
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
    (width, height) = (img.width, img.height)
    diff = width % split_width
    caption_file = os.path.splitext(file)[0]
    print("first pass")
    for x in range(0, width - split_width, split_width):
        box = (x, 0, x + split_width, height)
        filepath = f"{out_dir}/{add_leading_zeroes(counter, 5)}"
        img.crop(box).save(f"{filepath}.png")
        shutil.copyfile(f"{proc_dir}/{caption_file}.txt", f"{filepath}.txt")
        counter += 1
    if diff != 0:
        print("second pass (backwards)")
        for x in range(0, width - split_width, split_width):
            box = (width - (x + split_width), 0, width - x, height)
            filepath = f"{out_dir}/{add_leading_zeroes(counter, 5)}"
            img.crop(box).save(f"{filepath}.png")
            shutil.copyfile(f"{proc_dir}/{caption_file}.txt", f"{filepath}.txt")
            counter += 1

print("completed")
