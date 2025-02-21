from bs4 import BeautifulSoup, Tag
from marko import Parser, Renderer, convert


def get_header() -> BeautifulSoup:
    with open("templates/header.html", "r") as f:
        return BeautifulSoup(f.read(), "html.parser")


def handle_html(html: str, pretty: bool = False):
    soup: BeatifulSoup = BeautifulSoup(html, "html.parser")

    css = "main.css"
    template = f"""
    <html>
    <head><link rel="stylesheet" href={css}></head>
    <body></body>
    </html>"""
    new_soup: BeautifulSoup = BeautifulSoup(template, "html.parser")

    header = get_header()
    # print(header)
    # new_soup.body.insert(0, header)
    new_soup.body.append(header)
    new_soup.body.append(soup)

    if pretty:
        return new_soup.prettify()
    return str(new_soup)


def main(markdown: str):
    with open(markdown, "r") as f:
        # p = Parser()
        # doc = p.parse(f.read())
        html = convert(f.read())

    html = handle_html(html, False)
    print(html)


if __name__ == "__main__":
    main("posts/globe.md")
