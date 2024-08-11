from fasthtml.common import *
from headers import hdrs
from pathlib import Path

app, rt = fast_app(hdrs=hdrs)
setup_toasts(app)

js = """let edHtml = me("#editorHtml");
let edJson = me("#editorJson");
let cmHtml = CodeMirror(edHtml, { mode: "sparql", foldGutter: true, gutters: ["CodeMirror-foldgutter"] });
let cmJson = CodeMirror(edJson, { mode: "application/json", foldGutter: true, gutters: ["CodeMirror-foldgutter"] });
cmHtml.on("change", _ => edHtml.send("edited"));
cmJson.on("change", _ => edJson.send("edited"));"""


def set_cm_html(s):
    return run_js("cmHtml.setValue({s});", s=s)


def set_cm_json(s):
    return run_js("cmJson.setValue({s});", s=s)


def set_cm_result(s):
    return run_js("cmResult.setValue({s});", s=s)


def concatenate_strings(html_str, json_str):
    return html_str + "\n" + json_str


@rt("/")
def get():
    samp = Path("../tests/template_queries/construct_multiple.rq").read_text()
    ed_html_kw = dict(
        hx_post="/",
        target_id="details",
        hx_vals="js:{sparql_template: cmHtml.getValue(), json: cmJson.getValue()}",
    )
    ed_json_kw = dict(
        hx_post="/",
        target_id="details",
        hx_vals="js:{sparql_template: cmHtml.getValue(), json: cmJson.getValue()}",
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
        Div(id="editorResult"),
    )
    return Titled(
        "Concatenate SPARQL and JSON",
        frm,
        Script(js),
        Div(id="details"),
        set_cm_html(samp),
        set_cm_json("{}"),
    )


@rt("/")
def post(sparql_template: str, json: str):
    concatenated = concatenate_strings(sparql_template, json)
    return Pre(Code(concatenated, lang="html"))


serve()
