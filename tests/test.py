import pytest
from sparql import sparql_parser

from src.query_rewrite import query_rewrite


@pytest.mark.parametrize(
    "query, query_arguments, expected_query",
    [
        [
            """
            CONSTRUCT {
              ?s ?p ?o
            }
            WHERE {
              VALUES ?o { UNDEF }
              ?s ?p ?o ;
                 <https://property> "Person" .
            }
        """,
            {
                "head": {"vars": ["o"]},
                "arguments": {
                    "bindings": [
                        {
                            "o": {
                                "type": "literal",
                                "value": "Harry Potter and the Half-Blood Prince",
                            }
                        },
                        {"o": {"type": "literal", "value": "Bob", "xml:lang": "en"}},
                        {
                            "o": {
                                "type": "uri",
                                "value": "http://example.org/book/book6",
                            },
                        },
                        {
                            "o": {
                                "datatype": "http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral",
                                "type": "literal",
                                "value": '<p xmlns="http://www.w3.org/1999/xhtml">My name is <b>alice</b></p>',
                            }
                        },
                    ]
                },
            },
            """CONSTRUCT  {
    ?s ?p ?o
}
WHERE {

    VALUES ?o {
        '''<p xmlns="http://www.w3.org/1999/xhtml">My name is <b>alice</b></p>'''^^<http://www.w3.org/1999/02/22-rdf-syntax-ns#XMLLiteral> 		<http://example.org/book/book6> 		"Bob"@en "Harry Potter and the Half-Blood Prince"
    }
    ?s ?p  ?o ;
        <https://property> "Person"
}
        """,
        ],
        [
            """
            CONSTRUCT  {
                ?s ?p ?o
            }
            WHERE {
                VALUES (?s ?o ) { ( UNDEF UNDEF )
                }
                ?s ?p  ?o ;
                    <https://property> "Person"
            }
            """,
            {
                "head": {"vars": ["s", "o"]},
                "arguments": {
                    "bindings": [
                        {
                            "s": {"type": "uri", "value": "https://myuri"},
                            "o": {"type": "literal", "value": "literally"},
                        },
                        {
                            "s": {
                                "type": "literal",
                                "value": "langtag",
                                "xml:lang": "en",
                            },
                            "o": {
                                "type": "literal",
                                "value": "3.14",
                                "datatype": "http://www.w3.org/2001/XMLSchema#decimal",
                            },
                        },
                        {
                            "s": {"type": "uri", "value": "https://boolean"},
                            "o": {
                                "type": "literal",
                                "value": "true",
                                "datatype": "http://www.w3.org/2001/XMLSchema#boolean",
                            },
                        }
                    ]
                },
            },
            """
            CONSTRUCT {
              ?s ?p ?o
            }
            WHERE {
              VALUES ( ?s ?o ) { ( <https://myuri> "literally" ) ( "langtag"@en "3.14"^^<http://www.w3.org/2001/XMLSchema#decimal> ) ( <https://boolean> true ) }
              ?s ?p ?o ;
                 <https://property> "Person" .
            }
        """,
        ],
    ],
)
def test(query: str, expected_query: str, query_arguments: dict):
    query = query_rewrite(query, query_arguments)
    ast = sparql_parser.parse(query)
    expected_ast = sparql_parser.parse(expected_query)
    assert ast == expected_ast, query
