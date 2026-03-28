"""A2A Marketplace Dashboard"""
import streamlit as st
from a2a_protocol import A2AAgent

# Initialize agents
@st.cache_resource
def init_agents():
    seller = A2AAgent(
        name="seller",
        description="Marketplace seller",
        capabilities=["get_listings"]
    )

    buyer = A2AAgent(
        name="buyer",
        description="Marketplace buyer",
        capabilities=["evaluate_listing"]
    )

    def evaluate(params):
        price = params.get("price", 0)
        budget = params.get("budget", 100)

        if price > budget:
            return {"decision": "reject", "reason": f"Over budget (${budget})"}
        elif price < budget * 0.6:
            return {"decision": "accept", "reason": "Good deal"}
        else:
            return {"decision": "maybe", "reason": "Fair price"}

    buyer.register_capability("evaluate_listing", evaluate)
    return seller, buyer

seller, buyer = init_agents()

st.title("🛒 A2A Marketplace Dashboard")

st.header("Simulate Buyer Behavior")

col1, col2 = st.columns(2)

with col1:
    item_name = st.text_input("Item Name", "Laptop")
    price = st.number_input("Price ($)", min_value=0, value=80)

with col2:
    buyer_budget = st.number_input("Buyer Budget ($)", min_value=0, value=100)

if st.button("Simulate Buyer Evaluation"):
    response = seller.send_message(
        buyer,
        "evaluate_listing",
        {"price": price, "budget": buyer_budget}
    )

    result = response.result
    decision = result["decision"]

    if decision == "accept":
        st.success(f"✅ {result['reason']}")
    elif decision == "reject":
        st.error(f"❌ {result['reason']}")
    else:
        st.warning(f"🤔 {result['reason']}")

    st.json(result)

