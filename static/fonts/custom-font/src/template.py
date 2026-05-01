from PIL import Image, ImageDraw


class Template:
    def __init__(self):
        self.characters = "abcdefghijklmnopqrstuvwxyz"
        self.character_size = (64, 64)
        self.padding = 10
        self.dimension = (6, 5)

    def draw_template(self):
        img_dim = (
            self.dimension[0] * (self.character_size[0] + self.padding) + self.padding,
            self.dimension[1] * (self.character_size[1] + self.padding) + self.padding,
        )
        img = Image.new("RGB", img_dim, color="white")

        draw = ImageDraw.Draw(img)

        char_index = 0
        cur_y = self.padding
        for y in range(self.dimension[1]):
            cur_x = self.padding
            for x in range(self.dimension[0]):
                if char_index >= len(self.characters):
                    break

                # Empty rectangle
                draw.rectangle(
                    [
                        cur_x,
                        cur_y,
                        cur_x + self.character_size[0],
                        cur_y + self.character_size[1],
                    ],
                    fill="white",
                    outline="black",
                    width=2,
                )
                # Character
                draw.text(
                    (cur_x - self.padding * 0.7, cur_y - self.padding),
                    self.characters[char_index],
                    fill="black"
                )
                char_index += 1

                cur_x += self.character_size[0] + self.padding

            cur_y += self.character_size[1] + self.padding

        img.save("test.png")


if __name__ == "__main__":
    template = Template()
    template.draw_template()
