import abc

from mcp.server.fastmcp.resources import FunctionResource

from mcp_groceries_server.server import server, types


class Provider(abc.ABC):
    def __init__(self):
        server.add_tool(
            self.add_items_to_cart,
            name="add_items_to_cart",
            description="Add groceries to basket. Result is updated cart",
        )
        server.add_tool(
            self.remove_items_from_cart,
            name="remove_items_from_cart",
            description="Remove groceries from basket. Result is updated cart",
        )
        server.add_resource(
            FunctionResource(
                fn=self.search,
                uri="groceries://search/{item}",
                name="search",
                description="Lookup for item on the provider site, search should be in hebrew",
                mime_type="text/plain",
            )
        )

        # Setting as tool as a workaround as langchain mcp adapter doesn't support resources yet
        server.add_tool(
            self.search,
            name="search",
            description="Lookup for item on the provider site, search should be in hebrew",
        )
        
        server.add_tool(
            self.authorize,
            name="user_authorization",
            description="Allow the user to authorize - this should be done manually by the user",
        )

    @abc.abstractmethod
    async def add_items_to_cart(
        self, items: list[types.CartItemSchema]
    ) -> dict[str, list[dict]]: ...

    @abc.abstractmethod
    async def remove_items_from_cart(
        self, items: list[types.CartItemSchema]
    ) -> dict[str, list[dict]]: ...

    @abc.abstractmethod
    async def search(self, item: str) -> dict[str, list[dict]]: ...

    async def authorize(self) -> None:
        pass