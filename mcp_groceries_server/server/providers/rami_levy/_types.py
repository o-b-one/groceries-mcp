import pydantic


class CartItemSchema(pydantic.BaseModel):
    id: str = pydantic.Field(description="The id of the item")
    quantity: str = pydantic.Field(description="Quantity of the product")
