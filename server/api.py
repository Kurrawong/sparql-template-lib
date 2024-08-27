from typing import Annotated

from fastapi import FastAPI, HTTPException, Body, Depends, Path
from starlette.responses import Response, PlainTextResponse

from server.dependencies import validate_template_name
from server.models import TemplateList, SparqlArguments
from server.services import list_templates, save_template, delete_template, get_template_arguments, retrieve_template, \
    insert_arguments

app = FastAPI()


# FastAPI routes
@app.get("/templates")
async def get_all_templates():
    templates = list_templates()
    return TemplateList(templates=templates)


@app.get("/templates/{template_name}",
         responses={
             200: {
                 "content": {"application/sparql-query": {}},
                 "description": "Returns the requested SPARQL query template."
             },
             404: {"description": "Template not found."}
         })
async def get_template(
        template_name: Annotated[str, Path(description="Name of the SPARQL query template")]
) -> Response:
    try:
        template_content = retrieve_template(template_name)
        return Response(content=template_content, media_type="application/sparql-query")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Template not found")


@app.put("/templates/{template_name}")
async def create_or_update_template(
        template_name: str = Depends(validate_template_name),
        template: str = Body(..., media_type="application/sparql-query"),
):
    save_template(template_name, template)
    return {"message": f"Template '{template_name}' saved successfully"}


@app.delete("/templates/{template_name}")
async def remove_template(template_name: str):
    delete_template(template_name)
    return {"message": f"Template '{template_name}' deleted successfully"}


@app.post("/templates/{template_name}")
async def populate_template(
        template_name: str,
        args: SparqlArguments = Body(..., media_type="application/sparql-arguments+json")
):
    try:
        result = insert_arguments(template_name, args)
        return Response(content=result, media_type="application/sparql-query")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/templates/{template_name}/arguments")
async def get_arguments(template_name: str = Depends(validate_template_name)):
    return PlainTextResponse(content="not yet implemented")
    # try:
    #     args = get_template_arguments(template_name)
    #     return {"arguments": args}
    # except KeyError:
    #     raise HTTPException(status_code=404, detail="Template not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
