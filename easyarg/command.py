import inspect
import sys

from collections.abc import Callable
from enum import Enum
from inspect import Parameter

from .action import Action
from .action_registry import ActionRegistry, global_registry
from .exceptions import *
from .option import Option

class Command[T]:
    def __init__(self, function: Callable[..., T], *, action_registry: ActionRegistry = global_registry) -> None:
        self.function: Callable = function
        self.positional_options: list[Option] = []
        self.short_options: dict[str | int, Option] = {}
        self.long_options: dict[str | int, Option] = {}
        self.all_options: set[Option] = set()

        signature = inspect.signature(function, eval_str=True)
        for index, (_, parameter) in enumerate(signature.parameters.items()):
            if parameter.kind in (Parameter.VAR_POSITIONAL, Parameter.VAR_KEYWORD):
                raise ValueError('* and ** parameters are not allowed')
            positional = parameter.kind in (Parameter.POSITIONAL_ONLY, Parameter.POSITIONAL_OR_KEYWORD)
            required = parameter.default is Parameter.empty

            short_names = []
            long_names = []
            option_name: int | str
            if positional:
                option_name = index
            else:
                option_name = parameter.name
                first_letter = parameter.name[0]
                if first_letter.lower() not in self.short_options:
                    short_names.append(first_letter.lower())
                elif first_letter.upper() not in self.short_options:
                    short_names.append(first_letter.lower())
                long_names = [parameter.name.replace('_', '-')]

            read = action_registry.get_action(parameter.annotation)

            option = Option(option_name, parameter.name, read, short_names, long_names, required=required, positional=positional)
            self.add_option(option)

    def __call__(self, *args: list, **kwargs: dict) -> T:
        return self.function(*args, **kwargs)

    def add_option(self, option: Option) -> None:
        self.all_options.add(option)

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
        parser.validate()
        return parser.option_values

    def run(self, args: list[str] | None = None) -> T:
        try:
            all_args = self.parse(args or sys.argv[1:])
        except EasyargException as exception:
            if args is not None:
                raise
            print(sys.argv[0] + ':', exception, file=sys.stderr)
            sys.exit(1)

        args = []
        kwargs = {}
        for name, value in all_args.items():
            if isinstance(name, int):
                args.append(value)
            else:
                kwargs[name] = value

        result = self.function(*args, **kwargs)
        if args is None and result is not None:
            print(result)
        return result
