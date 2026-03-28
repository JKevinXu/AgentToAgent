"""A2A HTTP Client - Connect to distributed agents"""
import requests

class RemoteAgent:
    def __init__(self, base_url, agent_name):
        self.base_url = base_url
        self.agent_name = agent_name

    def send_message(self, method, params):
        """Send A2A message via HTTP"""
        url = f"{self.base_url}/agent/{self.agent_name}"
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": "1"
        }
        response = requests.post(url, json=payload)
        return response.json()

    def get_card(self):
        """Get agent card"""
        url = f"{self.base_url}/agent/{self.agent_name}/card"
        response = requests.get(url)
        return response.json()

if __name__ == "__main__":
    BASE_URL = "http://localhost:8000"
    print("=== Distributed A2A Demo ===\n")

    seller = RemoteAgent(BASE_URL, "seller")
    print("Seller card:", seller.get_card())

    result = seller.send_message("get_listings", {})
    print("\nListings:", result['result'])

    buyer = RemoteAgent(BASE_URL, "buyer")
    result = buyer.send_message("evaluate_listing", {"price": 50})
    print("\nBuyer evaluation:", result['result'])

