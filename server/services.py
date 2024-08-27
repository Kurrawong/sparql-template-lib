from pathlib import Path as PLPath
from typing import List, Dict, Generator

from fastapi import Path as FAPIPath

from server.models import TemplateName
from stl import query_rewrite


def save_template(template_name: str, template: str):
    filename = PLPath(__file__).parent / f"templates/{template_name}.rq"
    filename.parent.mkdir(parents=True, exist_ok=True)
    filename.write_text(template)


def retrieve_template(template_name: str) -> str:
    return (PLPath(__file__).parent / f"templates/{template_name}.rq").read_text()


def delete_template(template_name: str):
    filename = PLPath(__file__).parent / f"templates/{template_name}.rq"
    filename.unlink()


def populate_template(template_name: str, args: Dict[str, str]) -> str:
    # Implementation here
    pass


def get_template_arguments(template_name: str) -> List[str]:
    pass
    # template_text = (Path(__file__).parent / f"templates/{template_name}.rq").read_text()
    # return query_rewrite(template_text, {})


def list_templates() -> list[str]:
    return [file.stem for file in (PLPath(__file__).parent / f"templates").iterdir()]


async def validate_template_name(template_name: str = FAPIPath(...)) -> str:
    TemplateName(name=template_name)
    return template_name


def insert_arguments(template_name: str, args: Dict[str, str]) -> str:
    template = retrieve_template(template_name)
    return query_rewrite(template, args.model_dump(by_alias=True))
