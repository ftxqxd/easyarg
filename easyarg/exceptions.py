class EasyargException(Exception):
    pass

class UnknownOptionException(EasyargException):
    def __init__(self, name: str) -> None:
        super().__init__(f"unknown option: {name}")

class MissingValueException(EasyargException):
    def __init__(self, name: str) -> None:
        super().__init__(f"value required for parameter {name}")

class UnexpectedValueException(EasyargException):
    def __init__(self, name: str | None, value: str) -> None:
        if name is not None:
            super().__init__(f"unexpected value for flag {name}: {value}")
        else:
            super().__init__(f"unexpected positional argument: {value}")