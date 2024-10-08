from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

from stl.transformers.dataset_clause import InlineDataTransformer


def query_rewrite(query: str, query_arguments: dict) -> object:
    ast = sparql_parser.parse(query)
    with InlineDataTransformer(query_arguments=query_arguments) as transformer:
        ast = transformer.transform(ast)
        serializer = SparqlSerializer()
        serializer.visit_topdown(ast)
    return serializer.result
