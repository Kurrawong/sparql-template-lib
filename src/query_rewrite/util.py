from lark import Tree, Token


def set_value(node: Tree | Token, tree_path: list[str], new_value):
    if not tree_path:
        if isinstance(node, Token):
            node.value = new_value
            return
        else:
            raise TypeError(f"Unexpected node type {type(node)}")

    tree_path_type = tree_path[0]
    for child in node.children:
        if isinstance(child, Token):
            if len(tree_path) == 1:
                set_value(child, tree_path[1:], new_value)
        elif isinstance(child, Tree):
            if child.data == tree_path_type:
                set_value(child, tree_path[1:], new_value)
        else:
            raise TypeError(f"Unexpected child type {type(child)}")
