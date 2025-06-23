from loglight.handlers.BaseHandler import BaseHandler


class FileHandler(BaseHandler):
    def __init__(self, file_path: str, mode="a", enable_internal_logging=True):
        super().__init__(enable_internal_logging)
        self.file = open(file_path, mode, encoding="utf-8")

    def emit(self, log_str: str):
        self.file.write(log_str + "\n")
        self.file.flush()

    def __del__(self):
        if not self.file.closed:
            self.file.close()
