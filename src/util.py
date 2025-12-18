import re


def fill_links(text: str):
    return re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

def get_relative_dir_offset(dir: str) -> str:
    if dir == ".":
        return "."
    nr_dirs = dir.count("/") + 1
    return "/".join([".."] * nr_dirs)
