import sys


class ConsoleHandler:
    def __init__(self, stream=None):
        self.stream = stream or sys.stdout

    def emit(self, log_str: str):
        self.stream.write(log_str + "\n")
        self.stream.flush()
