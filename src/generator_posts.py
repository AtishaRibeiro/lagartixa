import os
import pathlib
import yaml
import re
import copy
from dataclasses import dataclass, field
from typing import Optional

from bs4 import BeautifulSoup
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pygments import highlight
from jinja2 import Environment, FileSystemLoader
from marko import Parser, Renderer, convert

import util

with open("src/localisation.yml", "r") as f:
    LOCALISATION = yaml.safe_load(f)


@dataclass
class Post:
    root_dir: pathlib.Path
    title: str = "No title"
    img_path: str = ""
    img_alt: str = ""
    date: str = "1997-12-22"
    edited: Optional[str] = None
    language: str = "en"
    available_languages: list = field(default_factory=lambda: [])
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
        if v := d.get("img-path"):
            self.img_path = v
        if v := d.get("img-alt"):
            self.img_alt = v
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


def process_figures(soup: BeautifulSoup, dir: pathlib.Path, language: str) -> None:
    """Process images and videos"""

    img_counter = 1
    img_dict = {}
    figure_name = LOCALISATION["figure"][language]

    for img in soup.find_all("img"):
        if img.get("id") == "site-logo":
            continue

        img_src = pathlib.Path("/", dir, img["src"])
        img["src"] = img_src
        img_title = img.get("title")
        img_id = img_src.stem.replace(" ", "-")
        img_dict[img_id] = f"{figure_name} {img_counter}"

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
            title = f"<b>{figure_name} {img_counter}:</b> {img_title}"
        else:
            title = f"<b>{figure_name} {img_counter}</b>"

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
    process_figures(html, post_dir, post.language)

    env = Environment(loader=FileSystemLoader("templates"))
    post_template = env.get_template("post.html")
    post_rendered = post_template.render(
        content=str(html), post=post, localisation=LOCALISATION
    )

    rel_dir = util.get_relative_dir_offset(str(post_dir))
    css = os.path.join(rel_dir, "static", "main.css")
    base_template = env.get_template("base.html")
    post_rendered = base_template.render(
        contents=post_rendered,
        styles=[css],
        _class="centered-column",
        root_path=rel_dir,
    )

    util.write_html(post.get_html_path(), post_rendered)


def get_all_post_infos() -> list[Post]:
    """Go over all dirs in `posts/` and create a list of all posts
    that should be generated."""

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
            languages = info.get("languages", {})

            for i, (language, language_info) in enumerate(languages.items()):
                post = copy.deepcopy(base_post)
                post.language = language
                post.available_languages = languages.keys()
                post.main = i == 0

                lang_file = post.get_md_path()
                if not lang_file.exists():
                    print(f"Skipping post for language '{language}', no md file found")
                    continue

                if language_info is not None:
                    post.overwrite_with_dict(language_info)

                posts.append(post)

    return posts


def generate_post_index_html(posts: list[Post]) -> None:
    """Generate the `/posts` page, which links to all posts"""

    @dataclass
    class PostIndex:
        dir: str
        languages: list
        titles: list[str]
        date: str

    post_dict = {}
    for post in posts:
        if post.root_dir not in post_dict:
            post_dict[post.root_dir] = PostIndex(
                str(post.root_dir), [post.language], [post.title], post.date
            )
        else:
            post_dict[post.root_dir].languages.append(post.language)
            post_dict[post.root_dir].titles.append(post.title)

    env = Environment(loader=FileSystemLoader("templates"))
    posts_template = env.get_template("posts.html")
    posts_rendered = posts_template.render(posts=post_dict.values())

    base_template = env.get_template("base.html")
    page_rendered = base_template.render(
        contents=posts_rendered,
        styles=["static/main.css", "static/posts.css"],
        root_path=".",
    )

    util.write_html(pathlib.Path("posts.html"), page_rendered)


def generate_posts_html(languages: list[str]) -> None:
    """Go over all posts in `posts/` and generate their pages +
    the posts index page"""

    posts: list[Post] = get_all_post_infos()
    posts = [x for x in posts if x.published]
    posts.sort(key=lambda post: post.date, reverse=True)

    # Generate the individual post pages
    for post in posts:
        generate_post_html(post)

        # Create a symlink that points to the main language post
        # This way `posts/<name>/` is also a valid url
        if post.main:
            index = post.root_dir / "index.html"
            try:
                index.symlink_to(post.get_html_path().name)
            except FileExistsError:
                pass

    # Generate the post index
    generate_post_index_html(posts)
