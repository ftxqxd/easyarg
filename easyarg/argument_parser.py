from __future__ import annotations

from dataclasses import dataclass

from .action import VariadicAction, ConstantAction
from .command import Command
from .exceptions import *
from .option import Option

@dataclass
class Token:
    value: str

@dataclass
class ShortArgumentToken(Token):
    def __str__(self) -> str:
        return '-' + self.value

@dataclass
class LongArgumentToken(Token):
    assignment: str | None = None
    def __init__(self, value: str, assignment: str | None = None) -> None:
        super().__init__(value)
        self.assignment = assignment
        if '=' in self.value and assignment is None:
            self.value, self.assignment = self.value.split('=', 1)

    def __str__(self) -> str:
        output = '--' + self.value
        if self.assignment is not None:
            output += '=' + self.assignment
        return output

@dataclass
class SeparatorToken(Token):
    def __init__(self) -> None:
        super().__init__('')

    def __str__(self) -> str:
        return '--'

@dataclass
class BareArgumentToken(Token):
    def __str__(self) -> str:
        return self.value

class ArgumentParser:
    def __init__(self, arguments: list[str], command: Command) -> None:
        self._tokens: list[Token] = []
        for argument in arguments:
            if argument == '--':
                self._tokens.append(SeparatorToken())
            elif argument[:2] == '--':
                self._tokens.append(LongArgumentToken(argument[2:]))
            elif argument[0] == '-' and len(argument) > 1:
                self._tokens.append(ShortArgumentToken(argument[1:]))
            else:
                self._tokens.append(BareArgumentToken(argument))

        self._command = command
        self._option_values: dict[int | str, object] = {}
        self._positional_option_index = 0
        self._raw_mode = False

    def option_values(self) -> dict[int | str, object]:
        return self._option_values.copy()

    def _peek_token(self) -> Token | None:
        if len(self._tokens) == 0:
            return None
        return self._tokens[0]

    def _next_token(self) -> Token:
        if len(self._tokens) == 0:
            raise MissingValueException('')
        token, *self._tokens = self._tokens
        return token

    def _next_bare_argument(self) -> str | None:
        value_token = self._peek_token()
        value = None
        if isinstance(value_token, BareArgumentToken):
            value = value_token.value
            self._next_token()
        return value

    def _set_option_value(self, option: Option, flag: str, input: str | None) -> None:
        if option.name in self._option_values:
            if not isinstance(option.action, VariadicAction):
                raise RepeatedOptionException(flag)
            previous_value = self._option_values[option.name]
            self._option_values[option.name] = option.action.update_argument(flag, previous_value, input)
        else:
            self._option_values[option.name] = option.action.read_argument(flag, input)

    def _current_positional_option(self) -> Option:
        return self._command.positional_options[self._positional_option_index]

    def parse(self) -> None:
        while len(self._tokens) > 0:
            token = self._next_token()

            if self._raw_mode or isinstance(token, BareArgumentToken):
                argument_value = str(token)
                flag = f'positional argument #{self._positional_option_index + 1}'
                if self._positional_option_index >= len(self._command.positional_options):
                    raise TrailingArgumentException(argument_value)

                option = self._current_positional_option()
                if not isinstance(option.action, VariadicAction):
                    self._positional_option_index += 1

                self._set_option_value(option, flag, argument_value)
                continue

            match token:
                case LongArgumentToken(name, value):
                    if name not in self._command.long_options:
                        raise UnknownOptionException(str(token))
                    option = self._command.long_options[name]
                    if not isinstance(option.action, ConstantAction) and value is None:
                        value = self._next_bare_argument()
                    self._set_option_value(option, str(token), value)

                case ShortArgumentToken(options):
                    name = options[0]
                    value = options[1:]
                    option = self._command.short_options[name]
                    if isinstance(option.action, ConstantAction):
                        # If it's a flag argument, allow chaining several in a single argument
                        if value != '':
                            self._tokens.insert(0, ShortArgumentToken(value))
                        value = None
                    elif value == '':
                        value = self._next_bare_argument()
                    self._set_option_value(option, str(token), value)

                case SeparatorToken():
                    self._raw_mode = True

    def validate(self) -> None:
        missing_options: list[Option] = []
        for option in self._command.all_options:
            if option.required and option.name not in self._option_values:
                missing_options.append(option)

        # Complain about missing positional options before missing flags
        missing_options.sort(key=lambda option: (isinstance(option.name, str), option.name))
        if missing_options:
            raise MissingOptionException(missing_options[0])
