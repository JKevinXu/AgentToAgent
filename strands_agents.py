"""Strands Agent Implementation for A2A Marketplace"""

# Note: Strands is not installed, this is a template
# Install with: pip install strands

from dataclasses import dataclass

@dataclass
class MockStrands:
    """Mock Strands for demonstration"""
    name: str
    instructions: str

    def tool(self):
        def decorator(func):
            return func
        return decorator

    def run(self, prompt="", stream=False):
        return f"{self.name} response"

# Create Strands agents
seller_agent = MockStrands(
    name="seller",
    instructions="You are a seller. List items and confirm sales."
)

@seller_agent.tool()
def get_inventory():
    """Get available items"""
    return "Laptop: $80, Phone: $50, Tablet: $120"

buyer_agent = MockStrands(
    name="buyer",
    instructions="You evaluate items. Budget: $100. Research prices before deciding."
)

@buyer_agent.tool()
def evaluate_item(name: str, price: float):
    """Evaluate if item is worth buying"""
    if price > 100:
        return f"❌ {name}: Over budget"
    elif price < 60:
        return f"✅ {name}: Good deal at ${price}"
    else:
        return f"🤔 {name}: Fair price at ${price}"

# Demo
if __name__ == "__main__":
    print("=== Strands A2A Demo ===\n")

    # Seller lists inventory
    print("Seller inventory:")
    print(get_inventory())

    # Buyer evaluates items
    print("\nBuyer evaluations:")
    print(evaluate_item("Laptop", 80))
    print(evaluate_item("Phone", 50))
    print(evaluate_item("Tablet", 120))


