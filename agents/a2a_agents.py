"""A2A Protocol Marketplace Agents"""
from core.a2a_protocol import A2AAgent
from agents.browser_buyer import browser_buyer


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
    import time
    from datetime import datetime
    price = params.get("price", 0)
    name = params.get("name", "Item")

    # Define buyers
    buyers = [
        {"agent": buyer, "name": "buyer1", "display": "Budget Buyer"},
        {"agent": buyer2, "name": "buyer2", "display": "Conservative Buyer"},
        {"agent": browser_buyer, "name": "browser_buyer", "display": "Web Research Buyer"}
    ]

    evaluations = []

    for b in buyers:
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()

        response = seller.send_message(b['agent'], "evaluate_listing", {"name": name, "price": price})

        end_timestamp = datetime.now().isoformat()
        elapsed = round((time.time() - start_time) * 1000)

        evaluations.append({
            "buyer": b['name'],
            "display_name": b['display'],
            "result": response.result,
            "start_time": start_timestamp,
            "end_time": end_timestamp,
            "elapsed_ms": elapsed
        })

    return {"evaluations": evaluations}







seller.register_capability("request_evaluation", handle_request_evaluation)

def handle_request_evaluation_stream(params):
    """Stream evaluation results as they complete"""
    import time
    from datetime import datetime
    from browser_buyer import set_log_callback
    price = params.get("price", 0)
    name = params.get("name", "Item")

    # Seller started
    yield {
        "type": "started",
        "buyer": "seller",
        "display_name": "Seller",
        "timestamp": datetime.now().isoformat()
    }
    yield {"type": "log", "buyer": "seller", "message": f"Received evaluation request for {name} at ${price}", "timestamp": datetime.now().isoformat()}

    buyers = [
        {"agent": buyer, "name": "buyer1", "display": "Budget Buyer"},
        {"agent": buyer2, "name": "buyer2", "display": "Conservative Buyer"},
        {"agent": browser_buyer, "name": "browser_buyer", "display": "Web Research Buyer"}
    ]

    for b in buyers:
        yield {"type": "log", "buyer": "seller", "message": f"Contacting {b['display']}...", "timestamp": datetime.now().isoformat()}

        # Send "started" message
        start_timestamp = datetime.now().isoformat()
        yield {
            "type": "started",
            "buyer": b['name'],
            "display_name": b['display'],
            "timestamp": start_timestamp
        }

        # For browser buyer, send browsing logs
        if b['name'] == 'browser_buyer':
            yield {"type": "log", "buyer": b['name'], "message": "Opening browser...", "timestamp": datetime.now().isoformat()}
            yield {"type": "log", "buyer": b['name'], "message": "Navigating to Amazon...", "timestamp": datetime.now().isoformat()}

        start_time = time.time()

        # Send progress logs during evaluation
        if b['name'] == 'browser_buyer':
            yield {"type": "log", "buyer": b['name'], "message": "Waiting for search results...", "timestamp": datetime.now().isoformat()}

        response = seller.send_message(b['agent'], "evaluate_listing", {"name": name, "price": price})

        if b['name'] == 'browser_buyer':
            yield {"type": "log", "buyer": b['name'], "message": "Extracting prices...", "timestamp": datetime.now().isoformat()}
            yield {"type": "log", "buyer": b['name'], "message": "Comparing with market data...", "timestamp": datetime.now().isoformat()}
        end_timestamp = datetime.now().isoformat()
        elapsed = round((time.time() - start_time) * 1000)

        # Send "completed" message
        yield {
            "type": "completed",
            "buyer": b['name'],
            "display_name": b['display'],
            "result": response.result,
            "timestamp": end_timestamp,
            "elapsed_ms": elapsed
        }

        yield {"type": "log", "buyer": "seller", "message": f"Received {response.result['decision']} from {b['display']}", "timestamp": datetime.now().isoformat()}

    yield {"type": "log", "buyer": "seller", "message": "All evaluations completed", "timestamp": datetime.now().isoformat()}


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
