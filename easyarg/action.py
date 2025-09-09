from collections.abc import Callable
from .exceptions import UnexpectedValueException, MissingValueException

class Action[T]:
    def read_argument(self, flag: str, input: str | None) -> T:
        raise NotImplementedError

class VariadicAction[T](Action[T]):
    def update_argument(self, flag: str, previous_value: T, input: str | None) -> T:
        raise NotImplementedError

class ConstantAction[T](Action[T]):
    def __init__(self, value: T) -> None:
        self._value = value

    def read_argument(self, flag: str, input: str | None) -> T:
        if input is not None:
            raise UnexpectedValueException(flag, input)
        return self._value

class BoolAction(ConstantAction[bool]):
    def __init__(self) -> None:
        super().__init__(True)

class SingleValueAction[T](Action[T]):
    def _read_input(self, input: str) -> T:
        raise NotImplementedError

    def read_argument(self, flag: str, input: str | None) -> T:
        if input is None:
            raise MissingValueException(flag)
        return self._read_input(input)

class StrAction(SingleValueAction[str]):
    def _read_input(self, input: str) -> str:
        return input

class IntAction(SingleValueAction[int]):
    def _read_input(self, input: str) -> int:
        return int(input)

class FloatAction(SingleValueAction[float]):
    def _read_input(self, input: str) -> float:
        return float(input)

class ListAction[T](VariadicAction[list[T]]):
    def __init__(self, action: Action[T]) -> None:
        self._action = action

    def read_argument(self, flag: str, input: str | None) -> list[T]:
        return [self._action.read_argument(flag, input)]

    def update_argument(self, flag: str, previous_value: list[T], input: str | None) -> list[T]:
        if input is None:
            raise MissingValueException(flag)
        return previous_value + [self._action.read_argument(flag, input)]
