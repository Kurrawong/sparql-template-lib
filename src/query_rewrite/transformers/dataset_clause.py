from copy import deepcopy

from lark import Tree, Token

from src.query_rewrite import BaseTransformer
from src.query_rewrite.util import set_value, get_dataset_clause_value


class DatasetClauseTransformer(BaseTransformer):
    def _dataset_clause_rewrite(
            self, children: list[Tree | Token]
    ) -> tuple[list[Tree | Token], list[Tree]]:
        dataset_clauses = list(
            filter(
                lambda x: isinstance(x, Tree) and x.data == "dataset_clause", children
            )
        )

        # Discard previous dataset_clause nodes.
        children = list(
            filter(
                lambda x: isinstance(x, Token)
                          or isinstance(x, Tree)
                          and x.data != "dataset_clause",
                children,
            )
        )

        new_nodes = []
        for dataset_clause in dataset_clauses:
            iri = get_dataset_clause_value(dataset_clause)
            graph_clause_type = dataset_clause.children[1].data

            real_graph_iris = self._get_real_graph_iris(iri)

            for real_graph_iri in real_graph_iris:
                new_node = deepcopy(dataset_clause)
                set_value(
                    new_node,
                    [graph_clause_type, "source_selector", "iri", "IRIREF"],
                    f"<{real_graph_iri}>",
                )
                new_nodes.append(new_node)

        return children, new_nodes

    def select_query(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._dataset_clause_rewrite(children)
        children = children[:1] + list(new_nodes) + children[1:]
        return Tree("select_query", children)

    def construct_construct_template(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._dataset_clause_rewrite(children)
        children = children[:1] + list(new_nodes) + children[1:]
        return Tree("construct_construct_template", children)

    def construct_triples_template(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._dataset_clause_rewrite(children)
        children = list(new_nodes) + children
        return Tree("construct_triples_template", children)

    def describe_query(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._dataset_clause_rewrite(children)

        position_to_insert = None
        var_or_iri_last_position = None
        for i, child in enumerate(children):
            if isinstance(child, Token) and child.type == "ASTERIX":
                position_to_insert = i
            elif isinstance(child, Tree) and child.data == "var_or_iri":
                var_or_iri_last_position = i

        if var_or_iri_last_position:
            position_to_insert = var_or_iri_last_position

        if position_to_insert is None:
            raise RuntimeError(
                f"Failed to determine position to insert new dataset_clause nodes. Could not find ASTERIX or var_or_iri"
            )

        position_to_insert += 1

        children = (
                children[:position_to_insert]
                + list(new_nodes)
                + children[position_to_insert:]
        )

        return Tree("describe_query", children)

    def ask_query(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._dataset_clause_rewrite(children)
        children = children[:1] + list(new_nodes) + children[1:]
        return Tree("ask_query", children)


# class InlineDataTransformer(BaseTransformer):
#
#     def _inline_data_clause_rewrite(
#             self, children: list[Tree | Token]
#     ) -> tuple[list[Tree | Token], list[Tree]]:
#         ild_clauses = list(
#             filter(
#                 lambda x: isinstance(x, Tree) and x.data == "data_block", children
#             )
#         )
#
#         # Discard previous dataset_clause nodes.
#         children = list(
#             filter(
#                 lambda x: isinstance(x, Token)
#                           or isinstance(x, Tree)
#                           and x.data != "data_block",
#                 children,
#             )
#         )
#
#         new_nodes = []
#         for ild_clause in ild_clauses:
#             # iri = get_dataset_clause_value(ild_clause)
#             graph_clause_type = ild_clause.children[0].data
#
#             # replacement_values = self._get_real_graph_iris(iri)
#             replacement_values = ["https://replacement-uri"]
#
#             for replacement_value in replacement_values:
#                 new_node = deepcopy(ild_clause)
#                 set_value(
#                     new_node,
#                     [graph_clause_type, "data_block_value", "UNDEF"],
#                     f"<{replacement_value}>",
#                 )
#                 new_nodes.append(new_node)
#
#         return children, new_nodes
#
#     def inline_data(self, children: list[Tree | Token]) -> Tree:
#         children, new_nodes = self._inline_data_clause_rewrite(children)
#         children = children[:1] + list(new_nodes) + children[1:]
#         return Tree("inline_data", children)


class InlineDataTransformer(BaseTransformer):

    def _replace_undef_in_data_block(
            self, children: list[Tree | Token]
    ) -> tuple[list[Tree | Token], list[Tree]]:

        dataset_clauses = list(
            filter(
                lambda x: isinstance(x, Tree) and x.data == "data_block", children
            )
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

        replacement_values = {"p": ["test 1", "test 2"], "o": ["test 3", "test 4"]}
        arguments = {
            "head": {"vars": ["s", "o"]
                     },
            "arguments": {
                "bindings": [
                    {
                        "s": {"type": "uri", "value": "http://example.org/book/book6"},
                        "o": {"type": "literal", "value": "Harry Potter and the Half-Blood Prince"}
                    },
                    {
                        "s": {"type": "uri", "value": "http://example.org/book/book7"},
                        "o": {"type": "literal", "value": "Bob", "xml:lang": "en"}
                    },
                    {
                        "s": {"type": "uri", "value": "http://example.org/book/book8"},
                        "o": {
                            "datatype": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                            "type": "literal",
                            "value": "<p xmlns=\"http://www.w3.org/1999/xhtml\">My name is <b>alice</b></p>"
                        }
                    },
                    {
                        "s": {"type": "bnode", "value": "r1"},
                        "o": {"type": "bnode", "value": "r1"}
                    }

                ]
            }
        }
        replacement_values_list = []
        new_nodes = []
        for child in dataset_clauses:
            if isinstance(child, Tree) and child.data == 'data_block':
                for grandchild in child.children:
                    if isinstance(grandchild, Tree) and grandchild.data == 'inline_data_one_var':
                        for i, var_or_dbvg in enumerate(grandchild.children):
                            if isinstance(var_or_dbvg, Tree) and var_or_dbvg.data == 'var':
                                var = var_or_dbvg.children[0].value.lstrip('?')
                                replacement_values_list.append(replacement_values[var])
                            elif isinstance(var_or_dbvg, Tree) and var_or_dbvg.data == 'data_block_value':
                                for value in var_or_dbvg.children:
                                    if isinstance(value, Token) and value.value == 'UNDEF':
                                        grandchild.children.pop(i)
                                        for vals_set in replacement_values_list:
                                            for val in reversed(vals_set):
                                                grandchild.children.insert(i, Tree(Token('RULE', 'data_block_value'), [
                                                    Tree(Token('RULE', 'rdf_literal'), [Tree(Token('RULE', 'string'), [
                                                        Token('STRING_LITERAL2', f"\"{val}\"")])])]))
                                    new_nodes.append(child)
                    elif isinstance(grandchild, Tree) and grandchild.data == 'inline_data_full':
                        for i, var_or_dbvg in enumerate(grandchild.children):
                            if isinstance(var_or_dbvg, Tree) and var_or_dbvg.data == 'var':
                                var = var_or_dbvg.children[0].value.lstrip('?')
                                replacement_values_list.append(replacement_values[var])
                            elif isinstance(var_or_dbvg, Tree) and var_or_dbvg.data == 'data_block_value_group':
                                all_undef = False
                                for dbv in var_or_dbvg.children:
                                    if isinstance(dbv, Tree) and dbv.data == 'data_block_value':
                                        for value in dbv.children:
                                            if isinstance(value, Token):
                                                if value.value == 'UNDEF':
                                                    all_undef = True
                                                else:
                                                    all_undef = False
                                if all_undef:
                                    grandchild.children.pop(i)
                                    for vals_set in replacement_values_list:
                                        new_children = []
                                        new_children.append(Token('LEFT_PARENTHESIS', '(')),
                                        for val in reversed(vals_set):
                                            new_children.append(Tree(Token('RULE', 'data_block_value'),
                                                                     [
                                                                         Tree(Token('RULE', 'rdf_literal'), [
                                                                             Tree(Token('RULE', 'string'), [
                                                                                 Token('STRING_LITERAL2',
                                                                                       f"\"{val}\"")])])
                                                                     ]
                                                                     ))
                                        new_children.append(Token('RIGHT_PARENTHESIS', ')'))
                                        replacement_dbvg = Tree(Token('RULE', 'data_block_value_group'), new_children)
                                        grandchild.children.insert(i, replacement_dbvg)
                                    new_nodes.append(child)
        return children, new_nodes

    def inline_data(self, children: list[Tree | Token]) -> Tree:
        children, new_nodes = self._replace_undef_in_data_block(children)
        children = children[:1] + list(new_nodes) + children[1:]
        return Tree("inline_data", children)
