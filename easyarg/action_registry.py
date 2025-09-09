from __future__ import annotations
from typing import Protocol

from .action import *

class GenericType(Protocol):
    __origin__: type
    __args__: tuple[type, ...]

type ActionSchema = Callable[..., Action]

class ActionRegistry:
    def __init__(self, action_registry: ActionRegistry | None = None) -> None:
        if not action_registry:
            self._actions: dict[type, Action] = {}
            self._action_schemas: dict[type, ActionSchema] = {}
        else:
            self._actions = action_registry._actions.copy()
            self._action_schemas = action_registry._action_schemas.copy()

    def register_action(self, ty: type, action: Action) -> None:
        self._actions[ty] = action

    def register_action_schema(self, ty: type, action_schema: ActionSchema) -> None:
        self._action_schemas[ty] = action_schema

    def get_action(self, ty: type | GenericType) -> Action:
        # If ty is a plain type, just get the appropriate action.
        if isinstance(ty, type):
            return self._actions[ty]

        # Otherwise, ty must be a GenericType. Get the action schema for the
        # generic type, and then recursively resolve the actions for its type
        # parameters.
        action_schema = self._action_schemas[ty.__origin__]
        arg_actions = []
        for arg in ty.__args__:
            arg_actions.append(self.get_action(arg))
        return action_schema(*arg_actions)

global_registry = ActionRegistry()
global_registry.register_action(int, IntAction())
global_registry.register_action(float, FloatAction())
global_registry.register_action(str, StrAction())
global_registry.register_action(bool, BoolAction())
global_registry.register_action_schema(list, lambda r: ListAction(r))