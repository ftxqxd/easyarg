from __future__ import annotations
from dataclasses import dataclass
from .exceptions import *
from typing import TYPE_CHECKING
from .command import Option, Command, OptionKind

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
                self.tokens.append(LongArgumentToken(argument[1:]))
            else:
                self.tokens.append(BareArgumentToken(argument))
        self.command = command
        self.option_values: dict[int | str, object] = {}

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
        if isinstance(value_token, BareArgumentToken):
            value = value_token.value
            self.next_token()
        return value

    def set_option_value(self, option: Option, value: str | None) -> None:
        self.option_values[option.name] = option.action.read_arg(value)

    def parse(self) -> None:
        positional_option_index = 0

        while len(self.tokens) > 0:
            token = self.next_token()
            match token:
                case LongArgumentToken(name, value):
                    if name not in self.command.long_options:
                        raise UnknownOptionException(name)
                    option = self.command.long_options[name]
                    if option.kind != OptionKind.FLAG and value is None:
                        value = self.next_bare_argument()
                    self.set_option_value(option, value)
                case ShortArgumentToken(options):
                    short_name = options[0]
                    value = options[1:]
                    option = self.command.short_options[name]
                    if option.kind == OptionKind.FLAG:
                        # If it's a flag argument, allow chaining several in a single argument
                        if value != '':
                            self.tokens.insert(0, ShortArgumentToken(value))
                        value = None
                    elif value == '':
                        value = self.next_bare_argument()
                    self.set_option_value(option, value)
                case BareArgumentToken(value):
                    if positional_option_index > len(self.command.positional_options):
                        raise UnexpectedValueException(None, value)
                    option = self.command.positional_options[positional_option_index]
                    if option.kind != OptionKind.VARIADIC:
                        positional_option_index += 1
                    self.set_option_value(option, value)
                case SeparatorToken():
                    raise NotImplementedError('--')


