import inspect
import sys

from collections.abc import Callable
from enum import Enum
from inspect import Parameter

from .action_registry import ActionRegistry, global_registry
from .action import Action

class Option[T]:
    def __init__(self, name: str | int, action: Action[T], short_names: list[str] = [], long_names: list[str] = [], *, positional: bool = False, flag: bool = False):
        self.name = name
        self.action = action
        self.short_names = short_names
        self.long_names = long_names
        self.positional = positional
        self.flag = flag

class Command[T]:
    def __init__(self, function: Callable[..., T], *, action_registry: ActionRegistry = global_registry) -> None:
        self.function: Callable = function
        self.positional_options: list[Option] = []
        self.short_options: dict[str | int, Option] = {}
        self.long_options: dict[str | int, Option] = {}

        signature = inspect.signature(function, eval_str=True)
        for index, (_, parameter) in enumerate(signature.parameters.items()):
            if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                raise ValueError('* and ** parameters are not allowed')
            positional = parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)

            short_names = []
            long_names = []
            parameter_name: int | str
            if positional:
                parameter_name = index
            else:
                parameter_name = parameter.name
                first_letter = parameter.name[0]
                if first_letter.lower() not in self.short_options:
                    short_names.append(first_letter.lower())
                elif first_letter.upper() not in self.short_options:
                    short_names.append(first_letter.lower())
                long_names = [parameter.name.replace('_', '-')]

            read = action_registry.get_action(parameter.annotation)

            option = Option(parameter_name, read, short_names, long_names, positional=positional, flag=parameter.annotation == bool)
            self.add_option(option)

    def __call__(self, *args: list, **kwargs: dict) -> T:
        return self.function(*args, **kwargs)

    def add_option(self, option: Option) -> None:
        if option.positional:
            self.positional_options.append(option)

        for name in option.short_names:
            self.short_options[name] = option

        for name in option.long_names:
            self.long_options[name] = option

    def parse(self, arguments: list[str]) -> dict:
        from .argument_parser import ArgumentParser

        parser = ArgumentParser(arguments, self)
        parser.parse()
        return parser.option_values

    def run(self) -> T:
        all_args = self.parse(sys.argv[1:])
        args = []
        kwargs = {}
        for name, value in all_args.items():
            if isinstance(name, int):
                args.append(value)
            else:
                kwargs[name] = value
        return self.function(*args, **kwargs)
