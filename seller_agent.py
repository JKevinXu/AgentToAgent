"""Seller Agent using Strands"""
from strands import Strands
from marketplace import marketplace, Listing

agent = Strands(
    name="seller",
    instructions="You are a seller agent. Create listings and confirm purchases.",
)

@agent.tool()
def create_listing(name: str, price: float) -> str:
    """Create a new item listing"""
    listing = Listing(
        id=f"item_{len(marketplace.listings)}",
        seller_id="seller",
        name=name,
        price=price
    )
    marketplace.create_listing(listing)
    return f"Listed {name} for ${price}"

@agent.tool()
def confirm_sale(tx_id: str) -> str:
    """Confirm a transaction"""
    tx = marketplace.confirm_transaction(tx_id)
    return f"Confirmed sale: {tx_id}" if tx else "Transaction not found"

if __name__ == "__main__":
    agent.run()
