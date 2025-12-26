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


def generate_snippets() -> None:
    """Generate code snippet pages"""
    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    snippet_template = env.get_template("snippet.html")

    with os.scandir("snippets") as it:
        for entry in it:
            if not entry.is_dir():
                continue

            snippet_dir = pathlib.Path(entry.path)

            with open(snippet_dir / "info.yml", "r") as f:
                snippet_info = yaml.safe_load(f)

            files = []
            for file_name in snippet_info["files"]:
                with open(snippet_dir / file_name, "r") as f:
                    snippet_content = f.read()

                highlighted = highlight(snippet_content, PythonLexer(), HtmlFormatter())
                files.append({"name": file_name, "content": highlighted})

            snippet_rendered = snippet_template.render(
                title=snippet_info["title"],
                # description=snippet_info.get("description"),
                files=files,
            )

            rel_dir = util.get_relative_dir_offset(str(snippet_dir))
            page_rendered = base_template.render(
                contents=snippet_rendered,
                styles=["static/main.css"],
                _class="centered-column",
                root_path=rel_dir,
            )

            with open(snippet_dir / "index.html", "w") as f:
                f.write(page_rendered)


@root
def generate():
    generate_simple_html("home", "index")
    generate_simple_html("about", "about")
    generate_videos_html()
    generate_posts_html([""])
    generate_snippets()


if __name__ == "__main__":
    generate()
