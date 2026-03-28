"""Browser-Powered Buyer Agent"""
from a2a_protocol import A2AAgent, log
import random

try:
    from web_scraper import scrape_prices
    USE_REAL = True
except ImportError:
    USE_REAL = False
    print("Playwright not installed. Using simulation.")


# Browser Buyer Agent
browser_buyer = A2AAgent(
    name="browser_buyer",
    description="Buyer agent that uses browser automation for real-time price research",
    capabilities=["search_web", "compare_prices", "evaluate_listing"]
)

def search_web(params):
    """Browser search for product prices"""
    item_name = params.get("name", "")
    log(f"[browser_buyer] Searching web for: {item_name}")

    if USE_REAL:
        sources = scrape_prices(item_name)
        if not sources:
            sources = [
                {"site": "Amazon", "price": random.randint(70, 100)},
                {"site": "eBay", "price": random.randint(65, 95)}
            ]
    else:
        sources = [
            {"site": "Amazon", "price": random.randint(70, 100)},
            {"site": "eBay", "price": random.randint(65, 95)},
            {"site": "BestBuy", "price": random.randint(75, 105)}
        ]

    return {"item": item_name, "sources": sources}

browser_buyer.register_capability("search_web", search_web)

def compare_prices(params):
    """Compare prices across sources"""
    sources = params.get("sources", [])
    prices = [s["price"] for s in sources]

    return {
        "lowest": min(prices),
        "highest": max(prices),
        "average": sum(prices) / len(prices),
        "best_source": min(sources, key=lambda x: x["price"])
    }

browser_buyer.register_capability("compare_prices", compare_prices)

def evaluate_with_browser(params):
    """Evaluate listing using browser research"""
    item_name = params.get("name", "")
    price = params.get("price", 0)

    # Search web
    search_result = search_web({"name": item_name})
    comparison = compare_prices({"sources": search_result["sources"]})

    log(f"[browser_buyer] Found prices: ${comparison['lowest']}-${comparison['highest']}")

    # Evaluate
    score = 0
    reasons = []

    if price < comparison["lowest"]:
        score += 50; reasons.append("Below all competitors")
    elif price <= comparison["average"]:
        score += 35; reasons.append("Below average price")
    else:
        reasons.append("Above average price")

    score += random.randint(0, 30)

    decision = "accept" if score >= 60 else "maybe" if score >= 35 else "reject"

    return {
        "decision": decision,
        "score": score,
        "reasons": reasons,
        "comparison": comparison
    }

browser_buyer.register_capability("evaluate_listing", evaluate_with_browser)

# Demo
if __name__ == "__main__":
    from a2a_agents import seller

    print("=== Browser Buyer Demo ===\n")

    # Get listings
    response = browser_buyer.send_message(seller, "get_listings", {})
    listings = response.result["listings"]

    # Evaluate with browser research
    for item in listings:
        print(f"\n--- {item['name']} ---")
        result = browser_buyer.send_message(
            browser_buyer,
            "evaluate_listing",
            {"name": item["name"], "price": item["price"]}
        )
        print(f"Decision: {result.result['decision'].upper()}")
        print(f"Score: {result.result['score']}/100")
        print(f"Comparison: ${result.result['comparison']['lowest']}-${result.result['comparison']['highest']}")


