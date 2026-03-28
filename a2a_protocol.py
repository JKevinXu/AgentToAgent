"""A2A Protocol Implementation"""
from dataclasses import dataclass, asdict
from typing import Optional
import json
from datetime import datetime

LOG_FILE = "a2a.log"

def log(message: str):
    """Log to file and console"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_line = f"[{timestamp}] {message}"
    print(log_line)
    with open(LOG_FILE, "a") as f:
        f.write(log_line + "\n")

@dataclass
class AgentCard:
    """Agent discovery card (.well-known/agent.json)"""
    name: str
    description: str
    capabilities: list[str]
    endpoint: str
    auth_method: str = "api_key"

@dataclass
class A2AMessage:
    """Standard A2A message format"""
    jsonrpc: str = "2.0"
    method: str = ""
    params: dict = None
    id: str = ""

@dataclass
class A2AResponse:
    """Standard A2A response format"""
    jsonrpc: str = "2.0"
    result: Optional[dict] = None
    error: Optional[dict] = None
    id: str = ""

class A2AAgent:
    """Base A2A Protocol Agent"""
    def __init__(self, name: str, description: str, capabilities: list[str]):
        self.card = AgentCard(
            name=name,
            description=description,
            capabilities=capabilities,
            endpoint=f"http://localhost:8000/{name}"
        )
        self.handlers = {}

    def register_capability(self, method: str, handler):
        """Register a capability handler"""
        self.handlers[method] = handler

    def handle_message(self, message: A2AMessage) -> A2AResponse:
        """Handle incoming A2A message"""
        log(f"[{self.card.name}] Received: {message.method}")

        if message.method not in self.handlers:
            return A2AResponse(
                id=message.id,
                error={"code": -32601, "message": "Method not found"}
            )

        try:
            result = self.handlers[message.method](message.params or {})
            log(f"[{self.card.name}] Response: {result}")
            return A2AResponse(id=message.id, result=result)
        except Exception as e:
            return A2AResponse(
                id=message.id,
                error={"code": -32603, "message": str(e)}
            )

    def send_message(self, target_agent, method: str, params: dict) -> A2AResponse:
        """Send A2A message to another agent"""
        msg = A2AMessage(method=method, params=params, id="1")
        return target_agent.handle_message(msg)

    def get_agent_card(self) -> dict:
        """Return agent card for discovery"""
        return asdict(self.card)

