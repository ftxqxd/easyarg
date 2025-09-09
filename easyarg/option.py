from .action import Action

class Option[T]:
    def __init__(
        self,
        name: str | int,
        parameter_name: str,
        action: Action[T],
        short_names: list[str] = [],
        long_names: list[str] = [],
        *,
        required: bool = False,
        positional: bool = False,
    ):
        self.name = name
        self.parameter_name = parameter_name
        self.action = action
        self.short_names = short_names
        self.long_names = long_names
        self.positional = positional
        self.required = required

    def user_readable_name(self) -> str:
        if isinstance(self.name, int):
            return f'positional argument {self.name + 1} ({self.parameter_name.upper()})'
        if self.long_names:
            return f'option --{self.long_names[0]}'
        return f'option -{self.short_names[0]}'
