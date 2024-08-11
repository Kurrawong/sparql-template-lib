from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

from src.query_rewrite.transformers import BaseTransformer
from src.query_rewrite.transformers.dataset_clause import InlineDataTransformer


def query_rewrite(query: str, query_arguments: dict):
    # TODO: Infer SPARQL query type (query vs update) and provide a way to specify explicitly.
    ast = sparql_parser.parse(query)
    with InlineDataTransformer(query_arguments=query_arguments) as transformer:
        ast = transformer.transform(ast)
        serializer = SparqlSerializer()
        serializer.visit_topdown(ast)
    print(serializer.result)
    return serializer.result
