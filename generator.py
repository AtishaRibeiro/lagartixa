from bs4 import BeautifulSoup
from marko import Parser, Renderer, convert
import os
import pathlib
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import re


def get_header(rel_dir: str) -> BeautifulSoup:
    with open("templates/header.html", "r") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    images = soup.find_all("img")
    for i in images:
        i["src"] = os.path.join(rel_dir, i["src"])

    return soup


def get_relative_dir_offset(dir: str) -> str:
    if dir == ".":
        return "."
    nr_dirs = dir.count("/") + 1
    return "/".join([".."] * nr_dirs)


def anchor_headers(soup: BeautifulSoup):
    # Create id's for headers so they can be anchored
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for header in headers:
        text = header.get_text()
        text = text.lower()
        text = text.replace(" ", "-")
        header["id"] = text


def syntax_highlighting(soup: BeautifulSoup):
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


def image_titles(soup: BeautifulSoup):
    img_counter = 1
    img_dict = {}

    for img in soup.find_all("img"):
        if img.get("id") == "site-logo":
            continue

        img_id = pathlib.Path(img["src"]).stem.replace(" ", "-")
        img_dict[img_id] = f"Figure {img_counter}"

        # Wrap img in a div
        div = soup.new_tag("div", attrs={"class": "img-div"})
        img.parent.insert(img.parent.contents.index(img), div)
        div.append(img)

        # Change parent <p> to a <div>
        div.parent.name = "div"
        div.parent["class"] = "img-root"

        if title := img.get("title"):
            title = f"<b>Figure {img_counter}:</b> {title}"
        else:
            title = f"<b>Figure {img_counter}</b>"

        title_soup = BeautifulSoup(title, "html.parser")
        title = soup.new_tag("p", attrs={"class": "img-title"})
        title.append(title_soup)
        img.insert_after(title)

        img_counter += 1

    # Replace image references
    img_link_regex = re.compile(r"\[\[(.*?)\]\]")
    for text_node in soup.find_all(string=True):
        if match := set(img_link_regex.findall(text_node)):
            new_text = text_node
            for m in match:
                to_replace = f"[[{m}]]"
                figure_ref = f"<i>{img_dict[m]}</i>"
                new_text = new_text.replace(to_replace, figure_ref)
            new_text = BeautifulSoup(new_text, "html.parser")
            text_node.replace_with(new_text)


def process_html(html: str, dir: str, pretty: bool = False) -> None:
    soup: BeatifulSoup = BeautifulSoup(html, "html.parser")
    rel_dir = get_relative_dir_offset(dir)

    css = os.path.join(rel_dir, "static", "main.css")
    template = f"""
    <html>
    <head><link rel="stylesheet" href={css}></head>
    <body></body>
    </html>"""
    new_soup: BeautifulSoup = BeautifulSoup(template, "html.parser")

    header = get_header(rel_dir)
    new_soup.body.append(header)
    new_soup.body.append(soup)

    anchor_headers(new_soup)
    syntax_highlighting(new_soup)
    image_titles(new_soup)

    if pretty:
        return new_soup.prettify()
    return str(new_soup)


def generate_post_html(name: str) -> None:
    post_dir = os.path.join("posts", name)
    markdown = os.path.join(post_dir, "text.md")
    with open(markdown, "r") as f:
        html = convert(f.read())

    html = process_html(html, post_dir, False)
    html_path = os.path.join(post_dir, f"{name}.html")
    with open(html_path, "w") as f:
        f.write(html)


def main():
    generate_post_html("globe")


if __name__ == "__main__":
    main()
