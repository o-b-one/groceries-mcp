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

            ### Step 1: Search for items and add to basket
            - Search each item in the list while considering the user preferences.
            - Collect the IDs as you will need them for the next step to update the basekt
            - Use the relevant tools to add and remove items to the basket based on the findings from previous step
            #### Shopping List:
                {shopping_list}

            **Important:**
            - You must follow the list by adding only items found in the list and by the user preferences, nothing more
            - If the basket contains items not found in the list you should remove those items
            - If item is not found try to find an alternative, add it to the basket with quantity 1
            ---
            ### Step 2: Conclusion
            
            Return the user the following details:
            
            - Items added to the cart
            - Alternative for items that couldn't be found
            - Items could not be found and not alternative found

            ---

            **Important:** Ensure efficiency and accuracy throughout the process.
            """
        ),
    ]
