from .action import Action

class ActionRegistry:
    def __init__(self) -> None:
        pass

    def get_action(self, ty: type) -> Action:
        raise NotImplementedError

global_registry = ActionRegistry()
