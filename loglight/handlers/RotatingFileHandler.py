# loglight/handlers.py
import os
import sys

from loglight.handlers.BaseHandler import BaseHandler


class RotatingFileHandler(BaseHandler):
    def __init__(
        self,
        file_path,
        max_bytes=10 * 1024 * 1024,
        backup_count=5,
        mode="a",
        enable_internal_logging=True,
    ):
        super().__init__(enable_internal_logging)
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.mode = mode
        self.file = open(file_path, mode, encoding="utf-8")

    def emit(self, log_str: str):
        self.file.write(log_str + "\n")
        self.file.flush()
        if self.should_rotate():
            self.rotate()

    def should_rotate(self):
        self.file.seek(0, os.SEEK_END)
        return self.file.tell() >= self.max_bytes

    def rotate(self):
        self.file.close()
        # Windows os.rename fails if destination exists; remove the oldest backup
        # first and use os.replace for atomic overwrite semantics across platforms.
        oldest_backup = f"{self.file_path}.{self.backup_count}"
        if os.path.exists(oldest_backup):
            os.remove(oldest_backup)

        for i in range(self.backup_count - 1, 0, -1):
            sfn = f"{self.file_path}.{i}"
            dfn = f"{self.file_path}.{i + 1}"
            if os.path.exists(sfn):
                os.replace(sfn, dfn)
        # Rename current log file to .1
        if os.path.exists(self.file_path):
            os.replace(self.file_path, f"{self.file_path}.1")
        # Reopen fresh log file
        self.file = open(self.file_path, self.mode, encoding="utf-8")

    def __del__(self):
        if not self.file.closed:
            self.file.close()
