"""Buyer Agent using Strands"""
from strands import Strands
from marketplace import marketplace

agent = Strands(
    name="buyer",
    instructions="You are a buyer agent. Browse listings and evaluate if you want to buy them based on price and value. Budget: $100.",
)

@agent.tool()
def browse_listings() -> str:
    """View available listings"""
    listings = marketplace.get_available_listings()
    return "\n".join([f"{l.id}: {l.name} - ${l.price}" for l in listings])

@agent.tool()
def evaluate_listing(listing_id: str) -> str:
    """Evaluate if a listing is worth buying"""
    listing = marketplace.listings.get(listing_id)
    if not listing:
        return "Listing not found"

    # Simple evaluation logic
    if listing.price > 100:
        return f"❌ {listing.name}: Too expensive (${listing.price} > $100 budget)"
    elif listing.price < 60:
        return f"✅ {listing.name}: Good deal at ${listing.price}"
    else:
        return f"🤔 {listing.name}: Fair price at ${listing.price}"

if __name__ == "__main__":
    agent.run()
