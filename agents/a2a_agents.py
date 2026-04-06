"""A2A Protocol Marketplace Agents"""
from core.a2a_protocol import A2AAgent
from agents.browser_buyer import browser_buyer
from agents.strands_agents import strands_buyer_a2a, set_log_callback as set_strands_log_callback


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
        {"agent": browser_buyer, "name": "browser_buyer", "display": "Web Research Buyer"},
        {"agent": strands_buyer_a2a, "name": "strands_buyer", "display": "Strands Buyer"}
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
    from agents.browser_buyer import set_log_callback
    import threading
    import queue
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
        {"agent": browser_buyer, "name": "browser_buyer", "display": "Web Research Buyer"},
        {"agent": strands_buyer_a2a, "name": "strands_buyer", "display": "Strands Buyer"}
    ]

    event_queue = queue.Queue()

    def evaluate_buyer(b):
        """Run buyer evaluation in thread"""
        # Send started
        event_queue.put({"type": "started", "buyer": b['name'], "display_name": b['display'], "timestamp": datetime.now().isoformat()})

        # Send logs
        if b['name'] == 'browser_buyer':
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Opening browser...", "timestamp": datetime.now().isoformat()})
            time.sleep(0.1)
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Navigating to Amazon...", "timestamp": datetime.now().isoformat()})
            time.sleep(0.1)
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Waiting for search results...", "timestamp": datetime.now().isoformat()})
            time.sleep(0.1)

        if b['name'] == 'strands_buyer':
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Initializing Strands agent...", "timestamp": datetime.now().isoformat()})
            time.sleep(0.2)
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Launching headless browser...", "timestamp": datetime.now().isoformat()})
            time.sleep(0.2)
            # Wire up live log callback so tool invocations stream to the dashboard
            def strands_log_cb(msg):
                event_queue.put({"type": "log", "buyer": "strands_buyer", "message": msg, "timestamp": datetime.now().isoformat()})
            set_strands_log_callback(strands_log_cb)

        start_time = time.time()
        response = seller.send_message(b['agent'], "evaluate_listing", {"name": name, "price": price})
        elapsed = round((time.time() - start_time) * 1000)

        if b['name'] == 'browser_buyer':
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Extracting prices...", "timestamp": datetime.now().isoformat()})
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Comparing with market data...", "timestamp": datetime.now().isoformat()})

        if b['name'] == 'strands_buyer':
            set_strands_log_callback(None)  # clear callback
            event_queue.put({"type": "log", "buyer": b['name'], "message": "Finalizing decision...", "timestamp": datetime.now().isoformat()})

        # Send completed
        event_queue.put({"type": "completed", "buyer": b['name'], "display_name": b['display'], "result": response.result, "timestamp": datetime.now().isoformat(), "elapsed_ms": elapsed})
        event_queue.put({"type": "log", "buyer": "seller", "message": f"Received {response.result['decision']} from {b['display']}", "timestamp": datetime.now().isoformat()})

    # Start all buyers in parallel
    threads = []
    for b in buyers:
        yield {"type": "log", "buyer": "seller", "message": f"Contacting {b['display']}...", "timestamp": datetime.now().isoformat()}
        t = threading.Thread(target=evaluate_buyer, args=(b,))
        t.start()
        threads.append(t)

    # Stream events as they arrive
    completed = 0
    while completed < len(buyers):
        try:
            event = event_queue.get(timeout=0.05)
            yield event
            if event.get("type") == "completed":
                completed += 1
        except queue.Empty:
            continue

    # Wait for all threads
    for t in threads:
        t.join()

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
