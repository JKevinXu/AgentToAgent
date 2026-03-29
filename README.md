# AgentToAgent

A2A Protocol marketplace system with real-time agent communication and web scraping.

## Project Structure

```
├── agents/          # Agent implementations (buyer, seller, browser)
├── core/            # A2A protocol and marketplace logic
├── web/             # Server, dashboards, web scraper
├── docs/            # Design documents
```

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers (for web scraping):
```bash
playwright install
```

## Running

1. Start the A2A server:
```bash
python -m web.a2a_server
```

2. Open the dashboard:
```bash
open web/dashboard_ws.html
```

3. Test the system by entering an item name and price, then click "Evaluate (Real-time Stream)"

## Features

- Real-time WebSocket streaming
- Multi-agent evaluation system
- Live web scraping from Amazon/eBay
- Distributed agent communication via HTTP
- A2A protocol implementation
