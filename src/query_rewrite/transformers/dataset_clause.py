import copy

from lark import Tree, Token

from src.query_rewrite import BaseTransformer


class InlineDataTransformer(BaseTransformer):

    def __init__(self, query_arguments: dict):
        self.query_arguments = query_arguments
        super().__init__()

    def _replace_undef_in_data_block(
        self, children: list[Tree | Token]
    ) -> tuple[list[Tree | Token], list[Tree]]:

        dataset_clauses = list(
            filter(lambda x: isinstance(x, Tree) and x.data == "data_block", children)
        )

        # Discard previous dataset_clause nodes.
        children = list(
            filter(
                lambda x: isinstance(x, Token)
                or isinstance(x, Tree)
                and x.data != "data_block",
                children,
            )
        )

        replacement_values_list = []
        new_nodes = []
        for child in dataset_clauses:
            if isinstance(child, Tree) and child.data == "data_block":
                for grandchild in child.children:
                    if (
                        isinstance(grandchild, Tree)
                        and grandchild.data == "inline_data_one_var"
                    ):
                        for i, var_or_dbvg in enumerate(grandchild.children):
                            if (
                                isinstance(var_or_dbvg, Tree)
                                and var_or_dbvg.data == "var"
                            ):
                                var = var_or_dbvg.children[0].value.lstrip("?")
                                for binding in self.query_arguments["arguments"][
                                    "bindings"
                                ]:
                                    if var in binding:
                                        replacement_values_list.append(binding[var])
                            elif (
                                isinstance(var_or_dbvg, Tree)
                                and var_or_dbvg.data == "data_block_value"
                            ):
                                for value in var_or_dbvg.children:
                                    if (
                                        isinstance(value, Token)
                                        and value.value == "UNDEF"
                                    ):
                                        grandchild.children.pop(i)
                                        for vals_dict in replacement_values_list:
                                            if vals_dict["type"] == "uri":
                                                grandchild.children.insert(
                                                    i,
                                                    _create_dbv_uri(vals_dict),
                                                )
                                            elif vals_dict["type"] == "literal":
                                                if vals_dict.get("datatype"):
                                                    token_string = self._escape_multi_line_strings(vals_dict)
                                                    grandchild.children.insert(
                                                        i,
                                                        _create_dbv_literal_datatype(
                                                            token_string, vals_dict
                                                        ),
                                                    )
                                                elif vals_dict.get("xml:lang"):
                                                    grandchild.children.insert(
                                                        i,
                                                        _create_dbv_literal_lang(
                                                            vals_dict
                                                        ),
                                                    )
                                                else:  # plain literal
                                                    grandchild.children.insert(
                                                        i,
                                                        self._create_dbv_plain_literal(vals_dict),
                                                    )
                                    new_nodes.append(child)
                    elif (
                        isinstance(grandchild, Tree)
                        and grandchild.data == "inline_data_full"
                    ):
                        vars_in_ildf = []
                        for i, var_or_dbvg in enumerate(grandchild.children):
                            if (
                                isinstance(var_or_dbvg, Tree)
                                and var_or_dbvg.data == "var"
                            ):
                                var = var_or_dbvg.children[0].value.lstrip("?")
                                vars_in_ildf.append(var)
                            elif (
                                isinstance(var_or_dbvg, Tree)
                                and var_or_dbvg.data == "data_block_value_group"
                            ):
                                all_undef = False
                                for dbv in var_or_dbvg.children:
                                    if (
                                        isinstance(dbv, Tree)
                                        and dbv.data == "data_block_value"
                                    ):
                                        for value in dbv.children:
                                            if isinstance(value, Token):
                                                if value.value == "UNDEF":
                                                    all_undef = True
                                                else:
                                                    all_undef = False
                                if all_undef:
                                    grandchild.children.pop(i)
                                    for vals_set in reversed(self.query_arguments["arguments"]["bindings"]):
                                        # check each var has a supplied argument, if not it is UNDEF
                                        new_children = []
                                        # all_vals = {}
                                        # for var in vars_in_ildf:
                                        #     if var not in vals_set:
                                        #         all_vals[var] = {"type": "UNDEF"}
                                        new_children.append(
                                            Token("LEFT_PARENTHESIS", "(")
                                        ),
                                        for arg_var, arg_val in vals_set.items():
                                            if arg_val["type"] == "uri":
                                                new_children.append(
                                                    _create_dbv_uri(arg_val)
                                                )
                                            elif arg_val["type"] == "literal":
                                                dtype = arg_val.get("datatype")
                                                if dtype:
                                                    if dtype == "http://www.w3.org/2001/XMLSchema#boolean":
                                                        new_children.append(
                                                            Tree(Token('RULE', 'data_block_value'), [
                                                                Tree(Token('RULE', 'boolean_literal'), [
                                                                    Tree(Token('RULE', f"{arg_val["value"]}"),
                                                                         [Token(f"{arg_val["value"].upper()}", f"{arg_val["value"]}")])])])
                                                        )
                                                    else:
                                                        token_string = self._escape_multi_line_strings(arg_val)
                                                        new_children.append(
                                                            _create_dbv_literal_datatype(
                                                                token_string, arg_val
                                                            )
                                                        )
                                                elif arg_val.get("xml:lang"):
                                                    new_children.append(
                                                        _create_dbv_literal_lang(
                                                            arg_val
                                                        )
                                                    )
                                                else:
                                                    new_children.append(self._create_dbv_plain_literal(arg_val))
                                            elif arg_val["type"] == "UNDEF":
                                                new_children.append(
                                                    Tree(Token('RULE', 'data_block_value'), [Token('UNDEF', 'UNDEF')])
                                                )

                                        new_children.append(
                                            Token("RIGHT_PARENTHESIS", ")")
                                        )
                                        replacement_dbvg = Tree(
                                            Token("RULE", "data_block_value_group"),
                                            new_children,
                                        )
                                        grandchild.children.insert(i, replacement_dbvg)
                                    new_nodes.append(child)
        return children, new_nodes

    def _create_dbv_plain_literal(self, vals_dict):
        return Tree(
            Token(
                "RULE",
                "data_block_value",
            ),
            [
                Tree(
                    Token(
                        "RULE",
                        "rdf_literal",
                    ),
                    [
                        Tree(
                            Token(
                                "RULE",
                                "string",
                            ),
                            [
                                Token(
                                    "STRING_LITERAL2",
                                    f"\"{vals_dict['value']}\"",
                                )
                            ],
                        )
                    ],
                )
            ],
        )

    def _escape_multi_line_strings(self, vals_set: dict) -> list:
        if '"' in vals_set["value"]:
            token_string = [
                Token(
                    "STRING_LITERAL_LONG1",
                    f"'''{vals_set['value']}'''",
                )
            ]
        else:
            token_string = [
                Token(
                    "STRING_LITERAL2",
                    f'"{vals_set["value"]}"',
                )
            ]
        return token_string

    def inline_data(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._replace_undef_in_data_block(children)
        children = children[:1] + list(new_nodes) + children[1:]
        return Tree("inline_data", children)


def _create_dbv_uri(vals_dict):
    return Tree(
        Token("RULE", "data_block_value"),
        [
            Tree(
                Token("RULE", "iri"),
                [
                    Token(
                        "IRIREF",
                        f"<{vals_dict['value']}>",
                    )
                ],
            )
        ],
    )


def _create_dbv_literal_lang(vals_dict):
    return Tree(
        Token(
            "RULE",
            "data_block_value",
        ),
        [
            Tree(
                Token(
                    "RULE",
                    "rdf_literal",
                ),
                [
                    Tree(
                        Token(
                            "RULE",
                            "string",
                        ),
                        [
                            Token(
                                "STRING_LITERAL2",
                                f'"{vals_dict["value"]}"',
                            )
                        ],
                    ),
                    Tree(
                        Token(
                            "RULE",
                            "langtag",
                        ),
                        [
                            Token(
                                "LANGTAG",
                                f'@{vals_dict["xml:lang"]}',
                            )
                        ],
                    ),
                ],
            )
        ],
    )


def _create_dbv_literal_datatype(token_string, vals_dict):
    return Tree(
        Token(
            "RULE",
            "data_block_value",
        ),
        [
            Tree(
                Token(
                    "RULE",
                    "rdf_literal",
                ),
                [
                    Tree(
                        Token(
                            "RULE",
                            "string",
                        ),
                        token_string,
                    ),
                    Tree(
                        Token(
                            "RULE",
                            "datatype",
                        ),
                        [
                            Tree(
                                Token(
                                    "RULE",
                                    "iri",
                                ),
                                [
                                    Token(
                                        "IRIREF",
                                        f'<{vals_dict["datatype"]}>',
                                    )
                                ],
                            )
                        ],
                    ),
                ],
            )
        ],
    )
