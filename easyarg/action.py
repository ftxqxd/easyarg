from collections.abc import Callable
from .exceptions import UnexpectedValueException, MissingValueException

class Action[T]:
    def read_arg(self, value: str | None) -> T:
        # TODO: Rethink this API as it relies on mutating the actions, which is kinda bad if you want to parse more than one arg list on the same Command
        raise NotImplementedError

class AtMostOnceAction[T](Action[T]):
    def __init__(self) -> None:
        self._seen = False

    def _read(self, value: str | None) -> T:
        raise NotImplementedError

    def read_arg(self, value: str | None) -> T:
        if self._seen:
            raise UnexpectedValueException()
        self._seen = True
        return self._read(value)

class BoolAction(AtMostOnceAction[bool]):
    def _read(self, value: str | None) -> bool:
        if value is not None:
            raise UnexpectedValueException()
        return True

class SingleValueAction[T](AtMostOnceAction[T]):
    def _read_str(self, value: str) -> str:
        raise NotImplementedError

    def _read(self, value: str | None) -> T:
        if value is None:
            raise MissingValueException()
        return self._read_str(value)

class StrAction(SingleValueAction[str]):
    def _read_str(self, value: str) -> str:
        return value

class IntAction(SingleValueAction[int]):
    def _read_str(self, value: str) -> int:
        return int(value)

class FloatAction(SingleValueAction[float]):
    def _read_str(self, value: str) -> float:
        return float(value)

class ListAction[T](Action[list[T]]):
    def __init__(self, action: Action[T]) -> None:
        self._action = action
        self._args = []

    def read_arg(self, value: str | None) -> list[T]:
        self._args.append(self._action.read_arg(value))
        return self._args
