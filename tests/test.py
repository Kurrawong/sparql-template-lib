import pytest
from sparql.parser import sparql_parser

from src.query_rewrite import query_rewrite


@pytest.mark.parametrize(
    "query, expected_query",
    [
        [
            """
            CONSTRUCT {
              ?s ?p ?o
            }
            WHERE {
              VALUES ?o { UNDEF "bound as well" }
              ?s ?p ?o ;
                 <https://property> "Person" .
            }
        """,
        """
        """,
        ],
        # [
        #     """
        #     CONSTRUCT {
        #       ?s ?p ?o
        #     }
        #     WHERE {
        #       VALUES ( ?s ?o ) { ( <https://myuri> "literally" ) ( "langtag"@en "3.14"^^<http://www.w3.org/2001/XMLSchema#decimal> ) ( <https://boolean> true ) }
        #       ?s ?p ?o ;
        #          <https://property> "Person" .
        #     }
        # """,
        #     """
        #     CONSTRUCT  {
        #         ?s ?p ?o
        #     }
        #     WHERE {
        #         VALUES (?s ?o ) {
        #         }
        #         ?s ?p  ?o ;
        #             <https://property> "Person"
        #     }
        #     """,
        # ],
    ],
)
def test(query: str, expected_query: str):
    query = query_rewrite(query)
    ast = sparql_parser.parse(query)
    expected_ast = sparql_parser.parse(expected_query)
    assert ast == expected_ast, query
