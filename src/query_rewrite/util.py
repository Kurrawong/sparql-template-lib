from lark import Tree, Token


def get_prefixed_name(prefixed_name: Tree):
    value = prefixed_name.children[0]
    if isinstance(value, Token):
        return value.value
    else:
        raise TypeError(f"Unexpected prefixed_name value type: {type(value)}")


def get_iri(iri: Tree):
    value = iri.children[0]
    if isinstance(value, Token):
        return value.value[1:-1]
    elif isinstance(value, Tree):
        if value.data == "prefixed_name":
            get_prefixed_name(value)
        else:
            raise ValueError(f"Unexpected iri value type: {value.data}")
    else:
        raise TypeError(f"Unexpected iri value type: {type(value)}")


def get_source_selector(source_selector: Tree):
    value = source_selector.children[0]
    if value.data == "iri":
        return get_iri(value)
    else:
        raise ValueError(f"Unexpected source_selector value type: {value.data}")


def get_default_graph_clause(default_graph_clause: Tree):
    value = default_graph_clause.children[0]
    if value.data == "source_selector":
        return get_source_selector(value)
    else:
        raise ValueError(f"Unexpected default_graph_clause value type: {value.data}")


def get_named_graph_clause(named_graph_clause: Tree):
    value = named_graph_clause.children[1]
    if value.data == "source_selector":
        return get_source_selector(value)
    else:
        raise ValueError(f"Unexpected default_graph_clause value type: {value.data}")


def get_dataset_clause_value(dataset_clause: Tree):
    value = dataset_clause.children[1]
    if value.data == "default_graph_clause":
        return get_default_graph_clause(value)
    elif value.data == "named_graph_clause":
        return get_named_graph_clause(value)
    else:
        raise ValueError(f"Unexpected dataset_clause value type: {value.data}")


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
