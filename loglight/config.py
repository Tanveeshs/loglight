from dataclasses import dataclass
from typing import Callable, Optional, TextIO
import sys
import json


@dataclass
class LoggerConfig:
    level: str = "INFO"
    output: Optional[TextIO] = sys.stdout
    include_timestamp: bool = True
    serializer: Callable = json.dumps  # function to convert dict to str

    def __post_init__(self):
        self.level = self.level.upper()
