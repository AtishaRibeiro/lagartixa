from pathlib import Path

from PIL import Image, ImageDraw

import generate_font
from vtracer import png_to_svg, Mode, ColorMode


class Template:
    def __init__(self):
        self.characters = "abcdefghijklmnopqrstuvwxyz"
        self.character_size = (64, 64)
        self.padding = 10
        self.dimension = (6, 5)

    def iter(self):
        chars = iter(self.characters)
        cur_y = self.padding
        for y in range(self.dimension[1]):
            cur_x = self.padding
            for x in range(self.dimension[0]):
                try:
                    yield next(chars), (
                        cur_x,
                        cur_y,
                        cur_x + self.character_size[0],
                        cur_y + self.character_size[1],
                    )
                    cur_x += self.character_size[0] + self.padding
                except StopIteration:
                    break

            cur_y += self.character_size[1] + self.padding


def draw_template(template: Template, out_file: str):
    t = template
    img_dim = (
        t.dimension[0] * (t.character_size[0] + t.padding) + t.padding,
        t.dimension[1] * (t.character_size[1] + t.padding) + t.padding,
    )
    img = Image.new("RGB", img_dim, color="white")

    draw = ImageDraw.Draw(img)

    for char, rect in template.iter():
        print(char)
        # Empty rectangle
        draw.rectangle(
            rect,
            fill="white",
            outline="black",
            width=2,
        )
        # Character
        draw.text(
            (rect[0] - t.padding * 0.7, rect[1] - t.padding),
            char,
            fill="black",
        )
       

    img.save(out_file)


def read_template(in_file: str):
    work_folder = Path("tmp")
    work_folder.mkdir(exist_ok=True)
    

    img = Image.open(in_file)
    t = Template()

    svgs = {}
    for char, rect in t.iter():
        png_file = f"{work_folder / char}.png"
        svg_file = f"{work_folder / char}.svg"

        # Small TEMPORARY hack to remove the border 
        letter = img.crop((rect[0] + 2, rect[1] + 2, rect[2] - 1, rect[3] - 1))
        letter.save(png_file)

        png_to_svg(
            Path(png_file),
            Path(svg_file),
            Mode.PIXEL,
            ColorMode.BW,
        )

        svgs.setdefault(svg_file, []).append(char)

    return svgs
       

if __name__ == "__main__":
    # template = Template()
    # draw_template(template, "test.png")

    svgs = read_template("filled.png")
    print(svgs)
    generate_font.execute(svgs, "TestFont", "TestFamily")
