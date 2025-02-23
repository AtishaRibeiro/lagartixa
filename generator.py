from bs4 import BeautifulSoup, Tag
from marko import Parser, Renderer, convert
import os


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


def handle_html(html: str, dir: str, pretty: bool = False) -> None:
    soup: BeatifulSoup = BeautifulSoup(html, "html.parser")
    rel_dir = get_relative_dir_offset(dir)

    css = os.path.join(rel_dir, "static", "main.css")
    print(css)
    template = f"""
    <html>
    <head><link rel="stylesheet" href={css}></head>
    <body></body>
    </html>"""
    new_soup: BeautifulSoup = BeautifulSoup(template, "html.parser")

    header = get_header(rel_dir)
    new_soup.body.append(header)
    new_soup.body.append(soup)

    if pretty:
        return new_soup.prettify()
    return str(new_soup)


def generate_post_html(name: str) -> None:
    post_dir = os.path.join("posts", name)
    markdown = os.path.join(post_dir, "text.md")
    with open(markdown, "r") as f:
        html = convert(f.read())

    html = handle_html(html, post_dir, False)
    html_path = os.path.join(post_dir, f"{name}.html")
    with open(html_path, "w") as f:
        f.write(html)


def main():
    generate_post_html("globe")


if __name__ == "__main__":
    main()
