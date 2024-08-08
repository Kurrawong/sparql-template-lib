from sparql.parser import sparql_parser
from sparql.serializer import SparqlSerializer

from src.query_rewrite.extractors import VarExtractor
from src.query_rewrite.transformers import BaseTransformer
from src.query_rewrite.transformers.dataset_clause import DatasetClauseTransformer, InlineDataTransformer


# class OlisTransformer(DatasetClauseTransformer, GraphGraphPatternTransformer):
#     ...


def query_rewrite(query: str):
    # TODO: Infer SPARQL query type (query vs update) and provide a way to specify explicitly.
    ast = sparql_parser.parse(query)

    # vars_extractor = VarExtractor()
    # vars_extractor.visit(ast)
    # vars = vars_extractor.vars

    with InlineDataTransformer() as transformer:
        # with OlisTransformer(service, vars) as transformer:
        ast = transformer.transform(ast)
        serializer = SparqlSerializer()
        serializer.visit_topdown(ast)
    print(serializer.result)
    return serializer.result
