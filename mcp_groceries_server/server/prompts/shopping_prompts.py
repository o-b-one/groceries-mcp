import dataclasses

from mcp_groceries_server.server.mcp_server import server


@dataclasses.dataclass
class UserMessage:
    content: str


@server.prompt()
def start_shopping(shopping_list: str, preferences: str) -> list[UserMessage]:
    """Use this prompt to determain how to start the shopping process"""
    return [
        UserMessage(
            content=f"""
            ### Prompt for Shopping Agent
            **Objective:**
            Using the shopping tools, search for the required grocery items, add them to the basket, and select an appropriate delivery window.

            **Important:**
            - Make sure that you don't buy more than it's needed for each article.
            - If quantity not defined use the default of 1
            - Be frugal, for each item in the list evaluate price and quantity_evaluation and choose the most cost efficient item
            - Remove items from the existing basket if not found in the new list
            - Evaluate the best grocery from the search based on text similarity and price per gram
            - Translate the groceries to Hebrew before search
            - If an item is **out of stock**, find the best alternative. Notice the user cannot answer your questions, you should decide on your own
            - Example substitutions:
                - If Gruyère cheese is unavailable, select another semi-hard cheese.
                - If Tahini is unavailable, a sesame-based alternative may work.


            **Preferences:**
            {preferences or "None"}

            ### Step 1: Search for items
            - Search each item in the list while considering the user preferences.
            - Collect the IDs and selling method as you will need them for the next step to update the cart
            
            #### Shopping List:
                {shopping_list}

            **Important:**
            - If item is not found try to find an alternative
            ---

            ### Step 2: Add carts into the cart
            - You must use `add_items_to_cart` to add items into the cart based on the findings from previous step
            - Assume authotization already took place
            - provide the quantity from the user shopping list. If quantity not provided, use quantity of 1
            
            **Important:**
            - You must follow the list by adding only items found in the list and by the user preferences, nothing more

            ### Step 3: Conclusion
            
            Return the user the following details:
            
            #### Added Items
            
            - Items added to the cart
            
            #### Alternatives
            
            - Alternative for items that couldn't be found
            #### Missing Items

            - Items could not be found and not alternative found
            
            
            #### Discounts and Deals 
            - <item_name>: <description of the available deals/discounts>

            ---

            **Important:** Ensure efficiency and accuracy throughout the process.
            """
        ),
    ]
