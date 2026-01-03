from pydantic import BaseModel, ConfigDict

class WireModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        # frozen=True,
        strict=True,
        validate_assignment=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        use_enum_values=True,
    )

