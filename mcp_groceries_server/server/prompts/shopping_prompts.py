import dataclasses

from mcp_groceries_server.server.mcp_server import server


@dataclasses.dataclass
class UserMessage:
    content: str


@server.prompt()
def start_shopping(shopping_list: str, preferences: str) -> list[UserMessage]:
    """USe this prompt to determain how to start the shopping process"""
    return [
        UserMessage(
            content=f"""
            ### Prompt for Shopping Agent
            **Objective:**
            Using the shopping tools, search for the required grocery items, add them to the basket, and select an appropriate delivery window.

            **Important:**
            - Make sure that you don't buy more than it's needed for each article.
            - If quantity not defined use the default of 1
            - Remove items from the existing basket if not found in the new list
            - Evaluate the best grocery from the search based on text similarity and price per gram
            - Translate the groceries to Hebrew before search
            - If an item is **out of stock**, find the best alternative. Notice the user cannot answer your questions, you should decide on your own
            - Example substitutions:
            - If Gruyère cheese is unavailable, select another semi-hard cheese.
            - If Tahini is unavailable, a sesame-based alternative may work.


            **Preferences:**
            {preferences or "None"}

            ---
            """  # noqa: E501
        ),
        UserMessage(
            content=f"""
                ### Step 1: Add Items to the Basket

                - Condider the preferences
                #### Shopping List:
                {shopping_list}
                ---
            """
        ),
        UserMessage(
            content="""
            ### Step 2: Remove unlisted items from the Basket

            ---
            """
        ),
        UserMessage(
            content="""
            ### Step 3: Conclusion
            
            Return the user the following details:
            
            - Items added to the cart
            - Alternative for items that couldn't be found
            - Items could not be found and not alternative found

            ---

            **Important:** Ensure efficiency and accuracy throughout the process.
            """
        ),
    ]


# @server.prompt()
# def place_order(
# preferred_time_window: str,
# payment_method: typing.Optional[str] = None
# ) -> List[UserMessage]:
#     return [
#         UserMessage(
#             content=f""""""
#         ),
#     ]
