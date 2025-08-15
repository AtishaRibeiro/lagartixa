import threading
import time
import os
import pathlib
from importlib import reload

from watchdog.events import (
    FileSystemEvent,
    FileModifiedEvent,
    RegexMatchingEventHandler,
    PatternMatchingEventHandler,
)
from watchdog.observers import Observer
from flask import Flask, send_from_directory, abort

import generator

app = Flask(__name__, static_folder="../static")


@app.route("/")
def index():
    return send_from_directory("../", "index.html")


@app.route("/<path:page>")
def static_page(page):
    path = pathlib.Path(page)

    if path.suffix in [".png", ".jpg"]:
        return send_from_directory(os.path.join("..", path.parent), path.name)

    return send_from_directory("../", f"{page}.html")


class FileModifiedHandler(PatternMatchingEventHandler):
    mod: int = 0

    def on_modified(self, event: FileModifiedEvent) -> None:
        global generator
        print(event)
        self.mod = (self.mod + 1) % 2
        # For some reason we always get 2 events for each change
        if self.mod == 0:
            print(">> Regenerating")

            generator = reload(generator)
            generator.generate()


def observe_file():
    event_handler = FileModifiedHandler(
        patterns=["templates/*.html", "src/generator.py"],
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
    threading.Thread(target=observe_file, daemon=True).start()
    app.run(debug=False)
