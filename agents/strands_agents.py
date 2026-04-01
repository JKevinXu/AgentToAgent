"""Strands Agent Implementation for A2A Marketplace"""
try:
    from strands import Strands
except ImportError:
    # Mock Strands for testing
    class Strands:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions
        def tool(self):
            return lambda f: f
        def run(self, prompt):
            return f"{self.name}: {prompt}"

from core.a2a_protocol import A2AAgent

# Buyer Agent
buyer_agent = Strands(
    name="buyer",
    instructions="You are a buyer agent. Browse listings and evaluate if you want to buy them based on price and value. Budget: $100."
)

# A2A wrapper for Strands buyer
strands_buyer_a2a = A2AAgent(
    name="strands_buyer",
    description="Strands-powered buyer agent",
    capabilities=["evaluate_listing"]
)

@buyer_agent.tool()
def browse_listings() -> str:
    """View available listings"""
    return "Listings available"

@buyer_agent.tool()
def evaluate_listing(listing_id: str) -> str:
    """Evaluate if a listing is worth buying"""
    return "Evaluation result"

def handle_strands_evaluate(params):
    """A2A handler that uses Strands buyer agent"""
    name = params.get("name", "Item")
    price = params.get("price", 0)

    prompt = f"Evaluate this listing: {name} at ${price}. Should we buy it?"
    response = buyer_agent.run(prompt)

    if price > 100:
        return {"decision": "reject", "reason": "Over $100 budget"}
    elif price < 60:
        return {"decision": "accept", "reason": "Good deal"}
    else:
        return {"decision": "maybe", "reason": "Fair price"}

strands_buyer_a2a.register_capability("evaluate_listing", handle_strands_evaluate)
