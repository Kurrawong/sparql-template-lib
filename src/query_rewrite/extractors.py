from lark import Visitor, Tree


class VarExtractor(Visitor):
    def __init__(self):
        self._vars = set()

    @property
    def vars(self):
        return self._vars

    def var(self, _var: Tree) -> None:
        self._vars.add(_var.children[0].value)


class InlineDataExtractor(Visitor):
    def __init__(self):
        self._inline_data_blocks = set()

    @property
    def inline_data_blocks(self):
        return self._inline_data_blocks

    def inline_data(self, _inline_data: Tree) -> None:
        self._inline_data_blocks.add(_inline_data)
