import subprocess
from pathlib import Path
from enum import StrEnum
import sys


class ColorMode(StrEnum):
    COLOR = "color"
    BW = "bw"


class Hierarchical(StrEnum):
    STACKED = "stacked"
    CUTOUT = "cutout"


class Mode(StrEnum):
    PIXEL = "pixel"
    POLYGON = "polygon"
    SPLINE = "spline"


class Preset(StrEnum):
    BW = "bw"
    POSTER = "poster"
    PHOTO = "photo"


def png_to_svg(
    png: Path,
    svg: Path,
    mode: Mode,
    color_mode: ColorMode,
    color_precision: int = 1,
    corner_threshold: int = 180,
    filter_speckle: int = 0,
    gradient_step: int = 1,
    hierarchical: Hierarchical = Hierarchical.STACKED,
    segment_length: int = 10,
    splice_threshold: int = 0,
):

    cmd = [Path(__file__).parent.parent / "deps/vtracer"]
    cmd += [
        "--colormode",
        color_mode,
        "-p",
        str(color_precision),
        "-c",
        str(corner_threshold),
        "-f",
        str(filter_speckle),
        "-g",
        str(gradient_step),
        "--hierarchical",
        hierarchical,
        "-l",
        str(segment_length),
        "-s",
        str(splice_threshold),
        "-m",
        mode,
        "-i",
        png,
        "-o",
        svg,
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=None,
    )

    for line in process.stdout:
        sys.stdout.write(line)


if __name__ == "__main__":
    png_to_svg(
        Path("/home/atisha/Downloads/AtestBW.png"),
        Path("test.svg"),
        Mode.PIXEL,
        ColorMode.BW,
    )
