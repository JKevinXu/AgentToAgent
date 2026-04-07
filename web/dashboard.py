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

        if price > 120:
            return {"decision": "not_buy", "reason": "Overpriced"}
        elif price < 60:
            return {"decision": "buy", "reason": "Good deal"}
        else:
            return {"decision": "buy", "reason": "Fair price"}

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
    pass

if st.button("Simulate Buyer Evaluation"):
    response = seller.send_message(
        buyer,
        "evaluate_listing",
        {"price": price}
    )

    result = response.result
    decision = result["decision"]

    if decision == "buy":
        st.success(f"✅ {result['reason']}")
    elif decision == "not_buy":
        st.error(f"❌ {result['reason']}")
    else:
        st.warning(f"🤔 {result['reason']}")

    st.json(result)

