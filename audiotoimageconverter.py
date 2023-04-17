from sharedinfo import WrapMode


def run(backwards_if_not_fit=True, chunk_jump=512, wrap_mode=WrapMode.REPEAT.value, in_dir="!input", proc_dir="!processing", out_dir="!output"):
    import os
    import shutil

    from riffusion.cli import audio_to_image
    from PIL import Image

    def add_leading_zeroes(string, leading_zero):
        return f"{'0'*leading_zero}{string}"

    def remake_dir(directory):
        if os.path.isdir(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

    # preparation
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
                match wrap_mode.value:
                    case WrapMode.FILL.value:
                        edit_image.paste(image_object, (0, 0))
                    case WrapMode.REPEAT.value:
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
    print("Completed!")


if __name__ == '__main__':
    # settings
    s = {
        "backwards_if_not_fit": True,        # Second pass backwards if size is not a multiple of chunk_jump
                                             # Default: True

        "chunk_jump": 512,                   # Size of jumps
                                             # Default: 512

        "wrap_mode": WrapMode.REPEAT.value,  # What to do if a file is too small.
                                             # Default: WrapMode.REPEAT.value
                                             # SKIP: ignore the file,
                                             # FILL: fill with empty space,
                                             # REPEAT: repeat the clip to fill

        "in_dir": "!input",                  # The input directory.
                                             # Default: "!input"

        "proc_dir": "!processing",          # The processing directory.
                                             # Default: "!processing"

        "out_dir": "!output"                 # The output directory.
                                             # Default: "!output"
    }
    run(s["backwards_if_not_fit"], s["chunk_jump"], s["wrap_mode"], s["in_dir"], s["proc_dir"], s["out_dir"])
