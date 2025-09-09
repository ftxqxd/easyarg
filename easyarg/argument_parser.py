from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

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
        return f'-' + self.value

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
        self.tokens: list[Token] = []
        for argument in arguments:
            if argument == '--':
                self.tokens.append(SeparatorToken())
            elif argument[:2] == '--':
                self.tokens.append(LongArgumentToken(argument[2:]))
            elif argument[0] == '-' and len(argument) > 1:
                self.tokens.append(ShortArgumentToken(argument[1:]))
            else:
                self.tokens.append(BareArgumentToken(argument))

        self.command = command
        self.option_values: dict[int | str, object] = {}
        self.positional_option_index = 0
        self.raw_mode = False

    def peek_token(self) -> Token | None:
        if len(self.tokens) == 0:
            return None
        return self.tokens[0]

    def next_token(self) -> Token:
        if len(self.tokens) == 0:
            raise MissingValueException('')
        token, *self.tokens = self.tokens
        return token

    def next_bare_argument(self) -> str | None:
        value_token = self.peek_token()
        value = None
        if isinstance(value_token, BareArgumentToken):
            value = value_token.value
            self.next_token()
        return value

    def set_option_value(self, option: Option, flag: str, input: str | None) -> None:
        if option.name in self.option_values:
            if not isinstance(option.action, VariadicAction):
                raise RepeatedOptionException(flag)
            previous_value = self.option_values[option.name]
            self.option_values[option.name] = option.action.update_argument(flag, previous_value, input)
        else:
            self.option_values[option.name] = option.action.read_argument(flag, input)

    def current_positional_option(self) -> Option:
        return self.command.positional_options[self.positional_option_index]

    def parse(self) -> None:
        while len(self.tokens) > 0:
            token = self.next_token()

            if self.raw_mode or isinstance(token, BareArgumentToken):
                argument_value = str(token)
                flag = f'positional argument #{self.positional_option_index + 1}'
                if self.positional_option_index >= len(self.command.positional_options):
                    raise TrailingArgumentException(argument_value)

                option = self.current_positional_option()
                if not isinstance(option.action, VariadicAction):
                    self.positional_option_index += 1

                self.set_option_value(option, flag, argument_value)
                continue

            match token:
                case LongArgumentToken(name, value):
                    if name not in self.command.long_options:
                        raise UnknownOptionException(str(token))
                    option = self.command.long_options[name]
                    if not isinstance(option.action, ConstantAction) and value is None:
                        value = self.next_bare_argument()
                    self.set_option_value(option, str(token), value)

                case ShortArgumentToken(options):
                    name = options[0]
                    value = options[1:]
                    option = self.command.short_options[name]
                    if isinstance(option.action, ConstantAction):
                        # If it's a flag argument, allow chaining several in a single argument
                        if value != '':
                            self.tokens.insert(0, ShortArgumentToken(value))
                        value = None
                    elif value == '':
                        value = self.next_bare_argument()
                    self.set_option_value(option, str(token), value)

                case SeparatorToken():
                    self.raw_mode = True

    def validate(self) -> None:
        missing_options: list[Option] = []
        for option in self.command.all_options:
            if option.required and option.name not in self.option_values:
                missing_options.append(option)

        # Complain about missing positional options before missing flags
        missing_options.sort(key=lambda option: (isinstance(option.name, str), option.name))
        if missing_options:
            raise MissingOptionException(missing_options[0])