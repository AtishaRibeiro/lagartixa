import os
import json


JSON = "fontforge-comm.json"

def execute(svgs: dict, font_name: str, font_family: str):
    data = {
        "svgs": svgs,
        "font_name": font_name,
        "font_family": font_family,
    }
    with open(JSON, "w") as f:
        json.dump(data, f, indent=2)

    os.system(f"fontforge -lang=py -script {__file__}")

def generate_font(svgs: dict, font_name: str, font_family: str):    
    import fontforge, psMat

    f = fontforge.font()
    f.fontname = font_name
    f.familyname = font_family
    f.fullname = font_name
    f.encoding = "UnicodeFull"

    for svg_path, chars in svgs.items():
        for char in chars:
            g = f.createChar(ord(char), char)
            g.importOutlines(svg_path)
            if not g.changed:
                # Something went wrong reading the svg
                g.importOutlines("tmp/a.svg")
                bb = g.boundingBox()
                print(f"{char}: {bb}")

            bb = g.boundingBox()

            target_height = 700
            scale = target_height / (bb[3] - bb[1])
            g.transform(psMat.scale(scale))

            # Then move it to sit on the baseline
            bb2 = g.boundingBox()
            g.transform(psMat.translate(-bb2[0], -bb2[1]))

            g.correctDirection()
            # Set advance width to match the glyph's bounding box width
            g.width = int(g.boundingBox()[2] - g.boundingBox()[0]) + 20  # +20 for some padding

    # Set font metrics based on the 'a' glyph
    f["a"].autoHint()
    f.ascent = 800
    f.descent = 200

    ttf_file = font_name + ".ttf"
    f.generate(ttf_file)
    # Convert to woff2 (requires woff2 tools installed)
    os.system(f"woff2_compress {ttf_file}")

   
if __name__ == "__main__":
    with open(JSON, "r") as f:
        data = json.load(f)
    generate_font(data["svgs"], data["font_name"], data["font_family"])
