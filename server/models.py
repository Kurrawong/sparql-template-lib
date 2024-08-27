from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, RootModel, field_validator


class Head(BaseModel):
    vars: List[str]


class VarValue(BaseModel):
    type: str
    value: str
    xml_lang: Optional[str] = Field(None, alias="xml:lang", exclude=True)
    datatype: Optional[str] = Field(None, exclude=True)

    @field_validator('datatype', 'xml_lang')
    def check_mutually_exclusive(cls, v: Optional[str], info: Any) -> Optional[str]:
        values = info.data
        other_field = 'xml_lang' if info.field_name == 'datatype' else 'datatype'
        if v is not None and values.get(other_field) is not None:
            raise ValueError(f"'xml:lang' and 'datatype' are mutually exclusive")
        return v

    model_config = {
        'json_encoders': {
            str: lambda v: v or None
        }
    }


class VarBinding(RootModel):
    root: Dict[str, VarValue]


class Arguments(BaseModel):
    bindings: List[VarBinding] = Field(default_factory=list)


class SparqlArguments(BaseModel):
    head: Optional[Head] = None
    arguments: Arguments


class TemplateName(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$",
        description="Template name must start with a letter, contain only letters, numbers, hyphens, or underscores, "
                    "and be 1-64 characters long.",
    )


class TemplateInfo(BaseModel):
    template: str
    arguments: List[str]


class TemplateList(BaseModel):
    templates: List[str]
