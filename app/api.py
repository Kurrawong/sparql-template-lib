from fasthtml.common import *
from headers import hdrs
from pathlib import Path
import json

from stl.query_rewrite import query_rewrite

app, rt = fast_app(hdrs=hdrs)
setup_toasts(app)

js = """let edSparql = me("#editorHtml");
let edJson = me("#editorJson");
let edResult = me("#details");
let cmSparql = CodeMirror(edSparql, { mode: "sparql", foldGutter: true, gutters: ["CodeMirror-foldgutter"] });
let cmJson = CodeMirror(edJson, { mode: "application/json_string", foldGutter: true, gutters: ["CodeMirror-foldgutter"] });
let cmResult = CodeMirror(edResult, { mode: "sparql", foldGutter: true, gutters: ["CodeMirror-foldgutter"] });
cmSparql.on("change", _ => edSparql.send("edited"));
cmJson.on("change", _ => edJson.send("edited"));"""


def set_cm_sparql(s):
    return run_js("cmSparql.setValue({s});", s=s)


def set_cm_json(s):
    return run_js("cmJson.setValue({s});", s=s)


def set_cm_result(s):
    return run_js("cmResult.setValue({s});", s=s)


@rt("/")
def get():
    sample_template_query = Path(
        "../tests/template_queries/construct_single.rq"
    ).read_text()
    sample_arguments = Path("../tests/template_args/construct_single.saj").read_text()
    ed_html_kw = dict(
        hx_post="/",
        target_id="details",
        hx_vals="js:{sparql_template: cmSparql.getValue(), json_string: cmJson.getValue()}",
    )
    ed_json_kw = dict(
        hx_post="/",
        target_id="details",
        hx_vals="js:{sparql_template: cmSparql.getValue(), json_string: cmJson.getValue()}",
    )
    frm = Form(
        Div(
            id="editorHtml",
            **ed_html_kw,
            hx_trigger="edited delay:300ms, load delay:100ms"
        ),
        Div(
            id="editorJson",
            **ed_json_kw,
            hx_trigger="edited delay:300ms, load delay:100ms"
        ),
        Div(id="details"),
    )
    return Titled(
        "SPARQL Template Editor",
        frm,
        Script(js),
        Div(id="details"),
        set_cm_sparql(sample_template_query),
        set_cm_json(sample_arguments),
    )


@rt("/")
def post(sparql_template: str, json_string: str):
    test = json.loads(json_string)
    result = query_rewrite(sparql_template, test)
    set_cm_result(result)
    # return set_cm_result(result)
    return Pre(Code(result, lang="sparql"))


serve()
