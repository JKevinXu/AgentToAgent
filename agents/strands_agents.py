"""Strands Agent Implementation for A2A Marketplace"""
import re
import logging
import sys
from strands import Agent, tool
from strands_tools.browser import LocalChromiumBrowser
from strands_tools.browser.browser import Browser
from core.a2a_protocol import A2AAgent

logger = logging.getLogger(__name__)

# Global log callback — set by a2a_agents before calling handle_strands_evaluate
_log_callback = None

def set_log_callback(callback):
    global _log_callback
    _log_callback = callback

def _emit_log(message):
    """Send a progress log to the dashboard if a callback is wired."""
    print(f"[strands_buyer] {message}", file=sys.stderr, flush=True)
    if _log_callback:
        _log_callback(message)


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
model = ModelConfig.openai(model_id="gpt-4.1-mini")

# --- Browser tool (headless Chromium with logging) ---
_browser_instance = LocalChromiumBrowser(launch_options={"headless": True})

# Get the DecoratedFunctionTool from the Browser base class
_browser_tool_obj = Browser.__dict__["browser"]

# Monkey-patch the tool's invoke function to emit logs before each call
_original_tool_func = _browser_tool_obj._tool_func

_MAX_TEXT_CHARS = 8000  # ~2K tokens — enough for price extraction, avoids 400K blowup

def _logging_browser_func(self_or_input, browser_input=None):
    """Wrapper that logs each browser action, then delegates to the real tool."""
    # Handle both bound (self, input) and unbound (input) calling conventions
    if browser_input is None:
        browser_input = self_or_input
        bound_self = _browser_instance
    else:
        bound_self = self_or_input

    action = {}
    if isinstance(browser_input, dict):
        action = browser_input.get("action", {})
    elif hasattr(browser_input, "action"):
        act = browser_input.action
        action = {"type": getattr(act, "type", "unknown")}
        if hasattr(act, "url"):
            action["url"] = act.url
        if hasattr(act, "session_name"):
            action["session_name"] = act.session_name

    action_type = action.get("type", "unknown")
    url = action.get("url", "")
    session = action.get("session_name", "")

    if action_type == "init_session":
        _emit_log(f"Opening browser session '{session}'...")
    elif action_type == "navigate":
        short_url = url[:60] + "..." if len(url) > 60 else url
        _emit_log(f"Navigating to {short_url}")
    elif action_type == "get_text":
        _emit_log("Extracting page text...")
    elif action_type == "get_html":
        _emit_log("Extracting page HTML...")
    elif action_type == "screenshot":
        _emit_log("Taking screenshot...")
    elif action_type == "close":
        _emit_log("Closing browser session")
    else:
        _emit_log(f"Browser action: {action_type}")

    result = _original_tool_func(bound_self, browser_input)

    # Truncate huge text/html responses to avoid blowing up the LLM context
    if action_type in ("get_text", "get_html") and isinstance(result, dict):
        content = result.get("content", [])
        for item in content:
            if isinstance(item, dict) and "text" in item:
                text = item["text"]
                if len(text) > _MAX_TEXT_CHARS:
                    item["text"] = text[:_MAX_TEXT_CHARS] + f"\n... [truncated from {len(text)} chars]"
                    _emit_log(f"Truncated page text from {len(text)} to {_MAX_TEXT_CHARS} chars")

    return result

_browser_tool_obj._tool_func = _logging_browser_func


@tool
def evaluate_price(item_name: str, price: float) -> str:
    """Evaluate if an item's price is worth buying based on market value.

    Args:
        item_name: Name of the item to evaluate.
        price: The listed price of the item.

    Returns:
        A price evaluation summary.
    """
    _emit_log(f"Evaluating {item_name} at ${price}")
    return f"{item_name} is listed at ${price}"


# Strands buyer agent with LLM + browser
buyer_agent = Agent(
    model=model,
    system_prompt="""You are a human buyer shopping for deals. Be concise.

You want to find the best deal. If the listed price is lower than what you find online, that's a great deal — BUY it.
Do NOT question whether a low price is "legitimate" or "too good to be true." You are simply comparing prices.

You will receive a listing with a product name, price, and detailed specs (brand, model, CPU, memory, graphics card).
Use ALL the spec details to build a specific search query — not just the generic item name.

Steps (follow in order):
1. Call browser: init_session, session_name "price-check", description "Price research"
2. Call browser: navigate to Amazon search using the brand, product name, and model — e.g. "https://www.amazon.com/s?k=Dell+XPS+15+9530+i7+16GB"
3. Call browser: get_text, selector "body" — scan for prices
4. Call browser: close session
5. Call evaluate_price with the item name and listed price
6. Reply with:
   - One PRODUCT line per competitor found: PRODUCT: Amazon | $<price> | <url>
   - Compare the listed price to the prices you found. If the listed price is equal or lower, say BUY. If higher, say NOT BUY.
   - Your verdict: BUY or NOT BUY with a one-sentence reason.""",
    tools=[evaluate_price, _browser_instance.browser],
    callback_handler=None,
)

# A2A wrapper for Strands buyer
strands_buyer_a2a = A2AAgent(
    name="strands_buyer",
    description="Strands-powered buyer agent with LLM reasoning and browser",
    capabilities=["evaluate_listing"]
)


def handle_strands_evaluate(params):
    """A2A handler that uses Strands buyer agent with LLM + browser"""
    name = params.get("name", "Item")
    price = params.get("price", 0)
    specs = {k: params[k] for k in ("product_name", "model", "brand", "cpu", "memory", "graphics_card") if params.get(k)}

    spec_text = ""
    if specs:
        spec_lines = [f"  {k}: {v}" for k, v in specs.items()]
        spec_text = "\nSpecs:\n" + "\n".join(spec_lines)

    # Build a specific search-friendly description
    search_parts = [specs.get("brand", ""), specs.get("product_name", ""), name]
    search_label = " ".join(filter(None, dict.fromkeys(search_parts)))  # deduplicate, preserve order

    try:
        prompt = f"Evaluate this listing: {search_label} at ${price}.{spec_text}\nSearch for this exact product using the brand, model, and specs above. Should we buy it?"
        result = buyer_agent(prompt)
        response_text = str(result)

        lower = response_text.lower()
        if "reject" in lower or "pass" in lower or "skip" in lower or "not buy" in lower or "don't buy" in lower:
            decision = "not_buy"
        elif "accept" in lower or "buy" in lower or "yes" in lower:
            decision = "buy"
        else:
            decision = "not_buy"

        # Parse PRODUCT lines: "PRODUCT: <site> | $<price> | <url>"
        products = []
        for match in re.finditer(
            r'PRODUCT:\s*(.+?)\s*\|\s*\$?([\d,.]+)\s*\|\s*(https?://\S+)',
            response_text
        ):
            site = match.group(1).strip()
            try:
                p = float(match.group(2).replace(",", ""))
            except ValueError:
                p = 0
            url = match.group(3).strip()
            products.append({"site": site, "price": p, "url": url})

        result_dict = {"decision": decision, "reason": response_text}
        if products:
            result_dict["products"] = products
        return result_dict
    except Exception as e:
        return {"decision": "not_buy", "reason": f"Unable to evaluate (LLM unavailable: {e})"}


strands_buyer_a2a.register_capability("evaluate_listing", handle_strands_evaluate)
