from bs4 import BeautifulSoup
from jinja2 import Environment, FileSystemLoader
from marko import Parser, Renderer, convert
import os
import pathlib
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import re
import yaml

ROOT_PATH = pathlib.Path(__file__).parent.parent


def root(func):
    def wrapper():
        cwd = os.getcwd()
        os.chdir(ROOT_PATH)
        func()
        os.chdir(cwd)

    return wrapper


def get_header(rel_dir: str) -> BeautifulSoup:
    with open("templates/header.html", "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    for image in soup.find_all("img"):
        image["src"] = os.path.join(rel_dir, image["src"])

    for link in soup.find_all("a"):
        if "href" in link.attrs:
            link["href"] = os.path.join(rel_dir, link["href"])

    return soup


def get_relative_dir_offset(dir: str) -> str:
    if dir == ".":
        return "."
    nr_dirs = dir.count("/") + 1
    return "/".join([".."] * nr_dirs)


def anchor_headers(soup: BeautifulSoup) -> None:
    # Create id's for headers so they can be anchored
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for header in headers:
        text = header.get_text()
        text = text.lower()
        text = text.replace(" ", "-")
        header["id"] = text


def syntax_highlighting(soup: BeautifulSoup) -> None:
    # Apply code syntax highlighting
    code_blocks = soup.find_all("code")
    for block in code_blocks:
        parent = block.parent
        if parent.name != "pre":
            continue

        highlighted = highlight(block.get_text(), PythonLexer(), HtmlFormatter())
        parsed = BeautifulSoup(highlighted, "html.parser")
        block.string = ""

        # Extract code out of <pre>
        parent.insert_after(block.extract())
        if not parent.text.strip():
            # Delete empty <pre>
            parent.decompose()

        block.append(parsed)


def process_figures(soup: BeautifulSoup, dir: str) -> None:
    """Process images and videos"""

    img_counter = 1
    img_dict = {}

    for img in soup.find_all("img"):
        if img.get("id") == "site-logo":
            continue

        img_src = pathlib.Path("/", dir, img["src"])
        img["src"] = img_src
        img_title = img.get("title")
        img_id = img_src.stem.replace(" ", "-")
        img_dict[img_id] = f"Figure {img_counter}"

        if img_src.suffix == ".webm":
            class_prefix = "video-"
            img.name = "video controls"
            img.attrs = {}
            video = soup.new_tag(
                "source", attrs={"src": img_src, "type": f"video/{img_src.suffix[1:]}"}
            )
            img.append(video)
        else:
            class_prefix = "img-"

        # Wrap img in a div
        div = soup.new_tag("div", attrs={"class": f"{class_prefix}div"})
        img.parent.insert(img.parent.contents.index(img), div)
        div.append(img)

        # Change parent <p> to a <div>
        div.parent.name = "div"
        div.parent["class"] = f"{class_prefix}root"

        if img_title:
            title = f"<b>Figure {img_counter}:</b> {img_title}"
        else:
            title = f"<b>Figure {img_counter}</b>"

        title_soup = BeautifulSoup(title, "html.parser")
        title = soup.new_tag("p", attrs={"class": f"{class_prefix}title"})
        title.append(title_soup)
        img.insert_after(title)

        img_counter += 1

    # Replace image references
    img_link_regex = re.compile(r"\[\[(.*?)\]\]")
    for text_node in soup.find_all(string=True):
        if match := set(img_link_regex.findall(text_node)):
            new_text = text_node
            for m in match:
                if m not in img_dict:
                    continue

                to_replace = f"[[{m}]]"
                figure_ref = f"<i>{img_dict[m]}</i>"
                new_text = new_text.replace(to_replace, figure_ref)
            new_text = BeautifulSoup(new_text, "html.parser")
            text_node.replace_with(new_text)


def generate_post_html(name: str) -> None:
    post_dir = os.path.join("posts", name)
    markdown = os.path.join(post_dir, "text.md")
    with open(markdown, "r") as f:
        html = convert(f.read())

    html: BeatifulSoup = BeautifulSoup(html, "html.parser")

    anchor_headers(html)
    syntax_highlighting(html)
    process_figures(html, post_dir)

    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")

    rel_dir = get_relative_dir_offset(post_dir)
    css = os.path.join(rel_dir, "static", "main.css")
    post_rendered = base_template.render(
        contents=str(html), styles=[css], _class="centered-column", root_path=rel_dir
    )

    html_path = os.path.join(post_dir, "index.html")
    with open(html_path, "w") as f:
        f.write(post_rendered)


def generate_posts_html() -> None:
    posts = []
    with os.scandir("posts") as it:
        for entry in it:
            if not entry.is_dir():
                continue

            root = pathlib.Path(entry.path)
            info_file = root / "info.yml"
            text_file = root / "text.md"

            if not info_file.exists() or not text_file.exists():
                print(
                    f"Skipping post '{entry.name}' because it doesn't have info.yml or text.md"
                )

            with open(info_file, "r") as f:
                info = yaml.safe_load(f)

            info["name"] = root.name
            posts.append(info)

    posts = [x for x in posts if x["published"]]
    posts.sort(key=lambda post: post["date"])
    print(posts)

    for post in posts:
        generate_post_html(post["name"])

    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    posts_template = env.get_template("posts.html")

    posts_rendered = posts_template.render(posts=posts)
    page_rendered = base_template.render(
        contents=posts_rendered,
        styles=["static/main.css", "static/posts.css"],
        root_path=".",
    )

    with open("posts.html", "w") as f:
        f.write(page_rendered)


def generate_video_html(video: dict) -> None:
    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    video_template = env.get_template("video.html")

    videos_dir = "videos"
    rel_dir = get_relative_dir_offset(videos_dir)

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

    page_rendered = base_template.render(
        contents=str(html),
        styles=["static/main.css"],
        _class="centered-column",
        root_path=".",
    )

    with open(f"{destination}.html", "w") as f:
        f.write(page_rendered)


@root
def generate():
    generate_videos_html()
    generate_simple_html("home", "index")
    generate_simple_html("about", "about")
    generate_simple_html("posts", "posts")
    generate_posts_html()


if __name__ == "__main__":
    generate()
