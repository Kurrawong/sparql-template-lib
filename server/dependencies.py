from fastapi import Path

from server.models import TemplateName


async def validate_template_name(template_name: str = Path(...)) -> str:
    TemplateName(name=template_name)
    return template_name