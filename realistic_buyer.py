"""Realistic Buyer Agent with Web Search and Comparison"""
from a2a_protocol import A2AAgent, log
import random

# Realistic Buyer Agent
realistic_buyer = A2AAgent(
    name="realistic_buyer",
    description="Buyer agent that researches and compares products",
    capabilities=["evaluate_listing", "research_product"]
)

def research_product(params):
    """Simulate web search for product research"""
    item_name = params.get("name", "")
    price = params.get("price", 0)

    # Simulate market research
    market_prices = {
        "Laptop": {"avg": 85, "min": 70, "max": 120},
        "Phone": {"avg": 55, "min": 40, "max": 80},
        "Tablet": {"avg": 90, "min": 75, "max": 110}
    }

    market = market_prices.get(item_name, {"avg": price, "min": price * 0.8, "max": price * 1.2})

    return {
        "item": item_name,
        "current_price": price,
        "market_avg": market["avg"],
        "market_range": f"${market['min']}-${market['max']}",
        "price_vs_market": round((price / market["avg"] - 1) * 100, 1)
    }

realistic_buyer.register_capability("research_product", research_product)

def evaluate_with_research(params):
    """Evaluate listing after research"""
    item_name = params.get("name", "")
    price = params.get("price", 0)

    # Research first
    research = research_product({"name": item_name, "price": price})
    log(f"[realistic_buyer] Researched {item_name}: {research['price_vs_market']}% vs market")

    # Multi-criteria scoring
    score = 0
    reasons = []

    # Price factor (40%)
    price_diff = research["price_vs_market"]
    if price_diff < -20:
        score += 40; reasons.append("Great price")
    elif price_diff < 0:
        score += 30; reasons.append("Below market")
    elif price_diff < 10:
        score += 20; reasons.append("Fair price")
    else:
        reasons.append("Above market")

    # Budget factor (30%)
    budget = params.get("budget", 100)
    if price <= budget * 0.7:
        score += 30; reasons.append("Within budget")
    elif price <= budget:
        score += 20
    else:
        reasons.append("Over budget")

    # Urgency/randomness (30%)
    urgency = random.randint(0, 30)
    score += urgency

    # Decision
    if score >= 70:
        decision = "accept"
    elif score >= 40:
        decision = "maybe"
    else:
        decision = "reject"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons,
        "research": research
    }

realistic_buyer.register_capability("evaluate_listing", evaluate_with_research)

# Demo
if __name__ == "__main__":
    from a2a_agents import seller

    print("=== Realistic Buyer Demo ===\n")

    # Get listings
    response = realistic_buyer.send_message(seller, "get_listings", {})
    listings = response.result["listings"]

    # Evaluate each listing
    for item in listings:
        print(f"\n--- Evaluating {item['name']} ---")
        result = realistic_buyer.send_message(
            realistic_buyer,
            "evaluate_listing",
            {"name": item["name"], "price": item["price"], "budget": 100}
        )
        print(f"Decision: {result.result['decision'].upper()}")
        print(f"Score: {result.result['score']}/100")
        print(f"Reasons: {', '.join(result.result['reasons'])}")


