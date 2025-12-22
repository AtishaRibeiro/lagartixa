import inspect
import json
import pathlib


class Data:
    """Class that ties json data to the file that uses this class."""

    def __init__(self, suffix: str = "", local: bool = False):
        caller_file = pathlib.Path(inspect.stack()[1].filename).stem
        self.__name = caller_file + (f"_{suffix}" if suffix else "")
        # Remove `c_` prefix
        self.__name = self.__name.split("_", 1)[1]
        dir = pathlib.Path(__file__).parent.parent / "_data"
        if local:
            dir /= "local"
        self.__file_path = dir / f"{self.__name}.json"
        exists = self.__file_path.exists()
        try:
            file_mode = "r+" if exists else "w+"
            self.__file = open(self.__file_path, file_mode, encoding="utf-8-sig")

            if exists:
                self.__json = json.load(self.__file)
            else:
                self.__json = {}
        except Exception as e:
            print("Failed to read " + str(self.__file_path))
            raise e

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__file.seek(0)
        json.dump(self.__json, self.__file)
        self.__file.truncate()

        self.__file.close()

    def __getitem__(self, key):
        return self.__json[key]

    def __setitem__(self, key, value):
        self.__json[key] = value

    def __delitem__(self, key):
        del self.__json[key]

    def __contains__(self, key):
        return key in self.__json
