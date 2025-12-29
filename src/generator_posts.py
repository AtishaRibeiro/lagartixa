import os
import pathlib
import yaml
import re
import copy
from dataclasses import dataclass
from typing import Optional

from bs4 import BeautifulSoup
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight
from jinja2 import Environment, FileSystemLoader
from marko import Parser, Renderer, convert

import util


@dataclass
class Post:
    root_dir: pathlib.Path
    title: str = "No title"
    date: str = "1997-12-22"
    edited: Optional[str] = None
    language: str = "en"
    published: bool = False
    # Whether this language is the main version of the post
    main: bool = False

    def get_info_file_path(self) -> pathlib.Path:
        return (self.root_dir / self.language).with_suffix(".yml")

    def get_html_path(self) -> pathlib.Path:
        return (self.root_dir / self.language).with_suffix(".html")

    def get_md_path(self) -> pathlib.Path:
        return (self.root_dir / self.language).with_suffix(".md")

    def overwrite_with_dict(self, d: dict):
        if v := d.get("title"):
            self.title = v
        if v := d.get("date"):
            self.date = v
        if v := d.get("edited"):
            self.edited = v
        if v := d.get("published"):
            self.published = v


def anchor_headers(soup: BeautifulSoup) -> None:
    # Create id's for headers so they can be anchored
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for header in headers:
        text = header.get_text()
        text = text.lower()
        text = text.replace(" ", "-")


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


def add_footer(
    soup: BeautifulSoup, date_published: str, date_edited: str | None
) -> None:
    def get_date_p(text: str, date: str) -> BeautifulSoup:
        soup = f'<p class="footer">{text}: {date}</p>'
        return BeautifulSoup(soup, "html.parser")

    soup.append(get_date_p("Published", date_published))
    if date_edited is not None:
        soup.append(get_date_p("Edited", date_edited))


def process_figures(soup: BeautifulSoup, dir: pathlib.Path) -> None:
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

        if img_title is None:
            continue

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


def generate_post_html(post: Post) -> None:
    post_dir = post.root_dir
    markdown = post.get_md_path()

    if not markdown.exists():
        print(f"Can't find {markdown}, skipping")
        return

    with open(markdown, "r") as f:
        html = convert(f.read())

    html: BeatifulSoup = BeautifulSoup(html, "html.parser")

    anchor_headers(html)
    syntax_highlighting(html)
    process_figures(html, post_dir)
    add_footer(html, post.date, post.edited)

    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")

    rel_dir = util.get_relative_dir_offset(str(post_dir))
    css = os.path.join(rel_dir, "static", "main.css")
    post_rendered = base_template.render(
        contents=str(html), styles=[css], _class="centered-column", root_path=rel_dir
    )

    with open(post.get_html_path(), "w") as f:
        f.write(post_rendered)


def get_all_post_info() -> list[Post]:
    posts = []
    with os.scandir("posts") as it:
        for entry in it:
            if not entry.is_dir():
                continue

            root = pathlib.Path(entry.path)
            info_file = root / "info.yml"

            if not info_file.exists():
                print(
                    f"Skipping post '{entry.name}' because it doesn't have an info.yml"
                )
                continue

            base_post = Post(root_dir=root)

            with open(info_file, "r") as f:
                info = yaml.safe_load(f)
            base_post.overwrite_with_dict(info)
            languages = info.get("languages", [])

            for i, language in enumerate(languages):
                post = copy.deepcopy(base_post)
                post.language = language
                post.main = i == 0
                lang_file = post.get_info_file_path()
                if not lang_file.exists():
                    print(f"Skipping post for language '{language}', no yml file found")
                    continue

                with open(lang_file, "r") as f:
                    info = yaml.safe_load(f)

                post.overwrite_with_dict(info)
                posts.append(post)

    return posts


def generate_post_index_html(posts: list[Post]) -> None:
    @dataclass
    class PostIndex:
        dir: str
        languages: list
        title: str
        date: str

    post_dict = {}
    for post in posts:
        if post.root_dir not in post_dict:
            post_dict[post.root_dir] = PostIndex(
                str(post.root_dir), [post.language], post.title, post.date
            )
        else:
            post_dict[post.root_dir].languages.append(post.language)

    env = Environment(loader=FileSystemLoader("templates"))
    base_template = env.get_template("base.html")
    posts_template = env.get_template("posts.html")

    posts_rendered = posts_template.render(posts=post_dict.values())
    page_rendered = base_template.render(
        contents=posts_rendered,
        styles=["static/main.css", "static/posts.css"],
        root_path=".",
    )

    with open("posts.html", "w") as f:
        f.write(page_rendered)


def generate_posts_html(languages: list[str]) -> None:
    posts: list[Post] = get_all_post_info()
    posts = [x for x in posts if x.published]
    posts.sort(key=lambda post: post.date, reverse=True)

    # Generate the individual post pages
    for post in posts:
        generate_post_html(post)

        # Create a symlink that points to the main post
        # This way `posts/<name>/` is also a valid url
        if post.main:
            index = post.root_dir / "index.html"
            try:
                index.symlink_to(post.get_html_path().name)
            except FileExistsError:
                pass

    # Generate the post index
    generate_post_index_html(posts)
