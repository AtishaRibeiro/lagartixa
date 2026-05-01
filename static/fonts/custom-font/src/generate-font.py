import fontforge
import os

SVG_PATH = "a.svg"
OUTPUT_TTF = "test.ttf"
OUTPUT_WOFF2 = "test.woff2"

f = fontforge.font()
f.fontname = "TestFont"
f.familyname = "TestFont"
f.fullname = "TestFont"
f.encoding = "UnicodeFull"

# Characters to map to the 'a' glyph
chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

for ch in chars:
    g = f.createChar(ord(ch), ch)
    g.importOutlines(SVG_PATH)
    g.correctDirection()
    # Set advance width to match the glyph's bounding box width
    g.width = int(g.boundingBox()[2] - g.boundingBox()[0]) + 20  # +20 for some padding

# Set font metrics based on the 'a' glyph
f["a"].autoHint()
f.ascent = 800
f.descent = 200

f.generate(OUTPUT_TTF)
print(f"Generated {OUTPUT_TTF}")

# Convert to woff2 (requires woff2 tools installed)
os.system(f"woff2_compress {OUTPUT_TTF}")
print(f"Generated {OUTPUT_WOFF2}")
