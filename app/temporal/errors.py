from dataclasses import dataclass


@dataclass
class DocumentNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

@dataclass
class DocumentUnsupportedError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)