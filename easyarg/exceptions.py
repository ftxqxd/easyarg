from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .option import Option

class EasyargException(Exception):
    pass

class UnknownOptionException(EasyargException):
    def __init__(self, flag: str) -> None:
        super().__init__(f"unknown option {flag}")

class TrailingArgumentException(EasyargException):
    def __init__(self, value: str) -> None:
        super().__init__(f"trailing argument: {value}")

class MissingOptionException(EasyargException):
    def __init__(self, option: Option) -> None:
        super().__init__(f"{option.user_readable_name()} must be provided")

class MissingValueException(EasyargException):
    def __init__(self, flag: str) -> None:
        super().__init__(f"a value is required for option {flag}")

class UnexpectedValueException(EasyargException):
    def __init__(self, flag: str, input: str) -> None:
        super().__init__(f"value provided for flag {flag}")

class RepeatedOptionException(EasyargException):
    def __init__(self, flag: str) -> None:
        super().__init__(f"option {flag} provided more than once")
