import typing

import pydantic


class CartItemSchema(pydantic.BaseModel):
    id: str = pydantic.Field(description="The id of the item")
    quantity: str = pydantic.Field(description="Quantity of the product")

    @pydantic.model_validator(mode="before")
    @classmethod
    def _fix_values(cls, data: typing.Any) -> typing.Any:
        data["id"] = str(data["id"])
        data["quantity"] = str(data["quantity"])
        return data
