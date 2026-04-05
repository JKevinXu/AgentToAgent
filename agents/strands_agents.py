"""Strands Agent Implementation for A2A Marketplace"""
from strands import Agent, tool
from core.a2a_protocol import A2AAgent


class ModelConfig:
    """Configure the LLM model provider for Strands agents."""

    @staticmethod
    def bedrock(model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0", region="us-east-1", **kwargs):
        from strands.models.bedrock import BedrockModel
        return BedrockModel(model_id=model_id, region_name=region, **kwargs)

    @staticmethod
    def anthropic(model_id="claude-sonnet-4-20250514", max_tokens=1024, **kwargs):
        from strands.models.anthropic import AnthropicModel
        return AnthropicModel(model_id=model_id, max_tokens=max_tokens, **kwargs)

    @staticmethod
    def openai(model_id="gpt-4o-mini", **kwargs):
        from strands.models.openai import OpenAIModel
        return OpenAIModel(model_id=model_id, **kwargs)

    @staticmethod
    def ollama(host="http://localhost:11434", model_id="llama3", **kwargs):
        from strands.models.ollama import OllamaModel
        return OllamaModel(host=host, model_id=model_id, **kwargs)


# --- Configure model here ---
model = ModelConfig.openai(model_id="gpt-4.1-nano")


@tool
def evaluate_price(item_name: str, price: float, budget: float = 100.0) -> str:
    """Evaluate if an item's price is worth buying given a budget.

    Args:
        item_name: Name of the item to evaluate.
        price: The listed price of the item.
        budget: Maximum budget available.

    Returns:
        A price evaluation summary.
    """
    if price > budget:
        return f"{item_name} at ${price} exceeds budget of ${budget}"
    elif price < budget * 0.6:
        return f"{item_name} at ${price} is a great deal (well under ${budget} budget)"
    else:
        return f"{item_name} at ${price} is fairly priced (within ${budget} budget)"


# Strands buyer agent with LLM
buyer_agent = Agent(
    model=model,
    system_prompt="You are a buyer agent for a marketplace. Evaluate listings and decide whether to buy based on price and value. Your budget is $100. Use the evaluate_price tool, then give a clear decision: accept, reject, or maybe. Keep your response brief.",
    tools=[evaluate_price],
    callback_handler=None,
)

# A2A wrapper for Strands buyer
strands_buyer_a2a = A2AAgent(
    name="strands_buyer",
    description="Strands-powered buyer agent with LLM reasoning",
    capabilities=["evaluate_listing"]
)


def handle_strands_evaluate(params):
    """A2A handler that uses Strands buyer agent with LLM"""
    name = params.get("name", "Item")
    price = params.get("price", 0)

    try:
        result = buyer_agent(f"Evaluate this listing: {name} at ${price}. Should we buy it?")
        response_text = str(result)

        lower = response_text.lower()
        if "reject" in lower or "pass" in lower or "skip" in lower or "no" in lower:
            decision = "reject"
        elif "accept" in lower or "buy" in lower or "yes" in lower:
            decision = "accept"
        else:
            decision = "maybe"

        return {"decision": decision, "reason": response_text}
    except Exception as e:
        # Fallback to rule-based if LLM fails
        if price > 100:
            return {"decision": "reject", "reason": f"Over $100 budget (LLM unavailable: {e})"}
        elif price < 60:
            return {"decision": "accept", "reason": f"Good deal (LLM unavailable: {e})"}
        else:
            return {"decision": "maybe", "reason": f"Fair price (LLM unavailable: {e})"}


strands_buyer_a2a.register_capability("evaluate_listing", handle_strands_evaluate)
