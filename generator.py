from bs4 import BeautifulSoup, Tag
from marko import Parser, Renderer, convert


def handle_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    css = "main.css"
    template = f"""
    <html>
    <head><link rel="stylesheet" href={css}></head>
    <body></body>
    </html>"""
    new_soup = BeautifulSoup(template, "html.parser")
    new_soup.body.append(soup)

    return str(new_soup)
    # return soup.prettify()


def main(markdown: str):
    with open(markdown, "r") as f:
        # p = Parser()
        # doc = p.parse(f.read())
        html = convert(f.read())

    html = handle_html(html)
    print(html)


if __name__ == "__main__":
    main("posts/globe.md")
