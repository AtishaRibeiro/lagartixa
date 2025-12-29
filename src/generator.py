from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from marko import Parser, Renderer, convert
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import os
import pathlib
import re
import yaml

import util
from generator_posts import generate_posts_html

ROOT_PATH = pathlib.Path(__file__).parent.parent


def root(func):
    def wrapper():
        cwd = os.getcwd()
        os.chdir(ROOT_PATH)
        func()
        os.chdir(cwd)

    return wrapper


def generate_video_html(video: dict) -> None:
    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    video_template = env.get_template("video.html")

    videos_dir = "videos"
    rel_dir = util.get_relative_dir_offset(videos_dir)

    video["description"] = util.fill_links(video["description"])
    video_rendered = video_template.render(video=video)
    post_rendered = base_template.render(
        contents=video_rendered,
        styles=["static/main.css", "static/video.css"],
        _class="centered-column",
        root_path=rel_dir,
    )

    html_path = os.path.join(videos_dir, f"{video["name_link"]}.html")
    with open(html_path, "w") as f:
        f.write(post_rendered)


def generate_videos_html() -> None:
    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    videos_template = env.get_template("videos.html")

    with open("videos/videos.yml", "r") as f:
        videos = yaml.safe_load(f)

    for video in videos:
        video["url"] = (
            f"https://youtube.com/embed/{video["url"].split("/")[-1]}?vq=hd720p"
        )

        keys = list(video)
        for key in keys:
            # Jinja doesn't like dashes
            video[key.replace("-", "_")] = video.pop(key)

        generate_video_html(video)

    videos_rendered = videos_template.render(videos=videos)

    page_rendered = base_template.render(
        contents=videos_rendered,
        styles=["static/main.css", "static/videos.css"],
        root_path=".",
    )

    with open("videos.html", "w") as f:
        f.write(page_rendered)


def generate_simple_html(template: str, destination: str) -> None:
    """For simple pages with content that fit in base.html without
    any extra processing"""
    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")

    with open(f"templates/{template}.html", "r") as f:
        html = f.read()

    styles = ["static/main.css"]
    specific_css = f"static/{template}.css"
    if pathlib.Path(specific_css).exists():
        styles.append(specific_css)

    page_rendered = base_template.render(
        contents=str(html),
        styles=styles,
        _class="centered-column",
        root_path=".",
    )

    with open(f"{destination}.html", "w") as f:
        f.write(page_rendered)
        base_template = env.get_template("base.html")


def generate_file_viewer(dir: pathlib.Path, root: bool) -> None:
    """Recursively generate file pages"""

    print(f"generating dir '{dir}'")

    if not dir.is_dir():
        return

    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    snippet_template = env.get_template("snippet.html")

    dirs = []
    files = []
    info = {}

    with os.scandir(dir) as it:
        for entry in it:
            entry_path = pathlib.Path(entry.path)
            is_dir = entry.is_dir()
            if is_dir:
                generate_file_viewer(entry_path, False)
                dirs.append({"name": entry_path.name + "/", "url": entry_path})
            else:
                # index.html is what we generate here
                if entry_path.name == "index.html":
                    continue

                with open(entry_path, "r") as f:
                    if entry_path.name == "info.yml":
                        info = yaml.safe_load(f)
                    else:
                        snippet_content = f.read()
                        highlighted = highlight(
                            snippet_content, PythonLexer(), HtmlFormatter()
                        )
                        files.append(
                            {
                                "name": entry_path.name,
                                "content": highlighted,
                                "url": str(pathlib.Path(*entry_path.parts[1:])),
                            }
                        )

    if len(dirs) == 0 and len(files) == 0:
        title = "Empty Folder"
    else:
        title = info.get("title", dir.name.title())

    # Add a way to get back up
    # if not root:
    #     dirs = [{"name": "../", "url": "/" + str(dir.parent)}] + dirs

    snippet_rendered = snippet_template.render(
        title=title,
        dirs=dirs,
        files=files,
    )

    rel_dir = util.get_relative_dir_offset(str(dir))
    page_rendered = base_template.render(
        contents=snippet_rendered,
        styles=["static/main.css"],
        _class="centered-column",
        root_path=rel_dir,
    )

    with open(dir / "index.html", "w") as f:
        f.write(page_rendered)


@root
def generate():
    generate_simple_html("home", "index")
    generate_simple_html("about", "about")
    generate_videos_html()
    generate_posts_html([""])
    generate_file_viewer(pathlib.Path("files"), True)


if __name__ == "__main__":
    generate()
