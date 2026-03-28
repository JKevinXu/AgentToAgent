"""A2A Protocol Marketplace Agents"""
from a2a_protocol import A2AAgent
from browser_buyer import browser_buyer


# Seller Agent
seller = A2AAgent(
    name="seller",
    description="Marketplace seller agent",
    capabilities=["get_listings", "confirm_sale"]
)

def handle_get_listings(params):
    return {
        "listings": [
            {"id": "item_0", "name": "Laptop", "price": 80},
            {"id": "item_1", "name": "Phone", "price": 50}
        ]
    }

seller.register_capability("get_listings", handle_get_listings)

def handle_request_evaluation(params):
    """Seller requests evaluation from all buyers"""
    price = params.get("price", 0)
    name = params.get("name", "Item")

    # Query all buyers
    evaluations = []

    # Buyer 1
    response = seller.send_message(buyer, "evaluate_listing", {"price": price})
    evaluations.append({"buyer": "buyer1", "result": response.result})

    # Buyer 2
    response = seller.send_message(buyer2, "evaluate_listing", {"price": price})
    evaluations.append({"buyer": "buyer2", "result": response.result})

    # Browser Buyer
    response = seller.send_message(browser_buyer, "evaluate_listing", {"name": name, "price": price})
    evaluations.append({"buyer": "browser_buyer", "result": response.result})

    return {"evaluations": evaluations}



seller.register_capability("request_evaluation", handle_request_evaluation)


# Buyer Agent
buyer = A2AAgent(
    name="buyer",
    description="Marketplace buyer agent",
    capabilities=["evaluate_listing"]
)

def handle_evaluate(params):
    price = params.get("price", 0)
    if price > 100:
        return {"decision": "reject", "reason": "Over budget"}
    elif price < 60:
        return {"decision": "accept", "reason": "Good deal"}
    else:
        return {"decision": "maybe", "reason": "Fair price"}

buyer.register_capability("evaluate_listing", handle_evaluate)

# Buyer Agent 2 (Budget-conscious)
buyer2 = A2AAgent(
    name="buyer2",
    description="Budget-conscious buyer agent",
    capabilities=["evaluate_listing"]
)

def handle_evaluate2(params):
    price = params.get("price", 0)
    if price > 70:
        return {"decision": "reject", "reason": "Too expensive for budget buyer"}
    elif price < 40:
        return {"decision": "accept", "reason": "Excellent deal!"}
    else:
        return {"decision": "maybe", "reason": "Acceptable price"}

buyer2.register_capability("evaluate_listing", handle_evaluate2)

# Demo
if __name__ == "__main__":
    print("=== A2A Protocol Demo ===\n")

    # Discover seller
    print("Seller Agent Card:")
    print(seller.get_agent_card())
    print()

    # Buyer queries seller
    response = buyer.send_message(seller, "get_listings", {})
    print(f"Listings: {response.result}")
    print()

    # Seller queries buyer for evaluation
    response = seller.send_message(buyer, "evaluate_listing", {"price": 50})
    print(f"Buyer 1 evaluation: {response.result}")

    # Seller queries buyer2 for evaluation
    response = seller.send_message(buyer2, "evaluate_listing", {"price": 50})
    print(f"Buyer 2 evaluation: {response.result}")
