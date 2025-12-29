import threading
import time
import os
import pathlib
from importlib import reload

from watchdog.events import (
    FileModifiedEvent,
    PatternMatchingEventHandler,
)
from watchdog.observers import Observer
from flask import Flask, send_from_directory

import generator

app = Flask(__name__, static_folder="../static")


@app.route("/")
def index():
    return send_from_directory("../", "index.html")


@app.route("/<path:page>")
def static_page(page):
    path = pathlib.Path(page)

    print(path)
    if path.suffix in [".png", ".jpg", ".webm", ".py", ".txt"]:
        return send_from_directory(os.path.join("..", path.parent), path.name)

    if pathlib.Path(f"{page}.html").exists():
        return send_from_directory("../", f"{page}.html")

    return send_from_directory(os.path.join("..", path), "index.html")


def regenerate() -> None:
    global generator
    try:
        generator = reload(generator)
        generator.generate()
    except Exception as e:
        print(e)


class FileModifiedHandler(PatternMatchingEventHandler):
    mod: int = 0

    def on_modified(self, event: FileModifiedEvent) -> None:
        # self.mod = (self.mod + 1) % 2
        # For some reason we always get 2 events for each change
        if self.mod == 0:
            print(">> Regenerating")
            regenerate()


def observe_file():
    event_handler = FileModifiedHandler(
        patterns=[
            "templates/*.html",
            "src/**.py",
            "posts/**/*.md",
            "posts/**/info.yml",
        ],
        ignore_directories=True,
        case_sensitive=False,
    )
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


if __name__ == "__main__":
    regenerate()
    threading.Thread(target=observe_file, daemon=True).start()
    app.run(debug=False)
