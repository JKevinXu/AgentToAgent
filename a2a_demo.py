"""A2A Direct Agent Interaction Demo"""
from strands import Strands

# Seller Agent
seller = Strands(
    name="seller",
    instructions="You sell items. When asked, provide item details and prices.",
)

@seller.tool()
def get_inventory() -> str:
    """Get available items for sale"""
    return "Laptop: $80, Phone: $50, Tablet: $120"

# Buyer Agent with access to seller
buyer = Strands(
    name="buyer",
    instructions="You evaluate items to buy. Ask the seller about inventory and evaluate prices.",
)

@buyer.tool()
def ask_seller(question: str) -> str:
    """Ask the seller a question"""
    response = seller.run(question, stream=False)
    return response

# Demo: Buyer queries seller directly
if __name__ == "__main__":
    print("=== A2A Direct Interaction ===\n")

    # Buyer asks seller about inventory
    result = buyer.run("What items do you have for sale?", stream=False)
    print(f"Buyer evaluation: {result}")
