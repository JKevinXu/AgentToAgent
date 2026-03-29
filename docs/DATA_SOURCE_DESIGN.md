# Real Data Source Integration Design

## Overview
Design for integrating the A2A marketplace buyer agents with real-time market data sources to enable authentic price comparison and market research.

## Current State

**Limitations:**
- Hardcoded market prices for 3 items only
- No real-time data updates
- Limited product coverage
- Static price ranges

**Impact:**
- Buyer decisions based on outdated/fictional data
- Cannot evaluate new products
- No market trend awareness

## Objectives

1. Connect to real pricing APIs
2. Enable dynamic market research
3. Support unlimited product types
4. Provide historical price trends
5. Real-time data updates

## Data Source Options

### Option 1: E-commerce APIs
- Amazon Product Advertising API
- eBay Browse API
- Pros: Real pricing data, comprehensive
- Cons: Rate limits, authentication, costs

### Option 2: Web Scraping
- BeautifulSoup + Requests
- Scrapy framework
- Pros: Flexible, free
- Cons: Fragile, legal concerns, maintenance

### Option 3: Price Tracking Services
- CamelCamelCamel API (Amazon history)
- Keepa API
- Pros: Historical trends, price alerts
- Cons: Limited to specific platforms

### Option 4: Browser Automation Tools
- Playwright / Puppeteer
- Selenium WebDriver
- Pros: Access any website, JavaScript rendering, realistic behavior
- Cons: Slower, resource-intensive, maintenance overhead

**Browser Tool Benefits:**
- No API keys or authentication needed
- Access sites without public APIs
- Handle dynamic content (JavaScript-rendered prices)
- Simulate real user browsing patterns

## Recommended Architecture

### Phase 1: Mock API Layer
```python
class PriceDataSource:
    def get_market_price(self, product_name):
        # Returns: {avg, min, max, currency}
        pass

    def get_price_history(self, product_name, days=30):
        # Returns: [{date, price}, ...]
        pass
```

### Phase 2: Real API Integration
```python
class EbayDataSource(PriceDataSource):
    def __init__(self, api_key):
        self.api_key = api_key

    def get_market_price(self, product_name):
        # Call eBay API
        # Parse response
        # Return standardized format
```

### Phase 3: Caching Layer
- Redis for price caching (TTL: 1 hour)
- Reduce API calls and costs
- Faster response times

## Implementation Plan

### Step 1: Abstract Interface
Create `PriceDataSource` base class

### Step 2: Mock Implementation
Expanded static data for testing

### Step 3: API Integration
Integrate eBay Browse API (free tier)

### Step 3b: Browser Tool (Alternative)
Use Playwright for sites without APIs
```python
from playwright.sync_api import sync_playwright

def get_price_from_web(product_name):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Navigate and scrape
```

### Step 4: Caching
Add Redis caching (TTL: 1 hour)

### Step 5: Fallback
API fails → cached/mock data

## Security
- API keys in environment variables
- Rate limiting
- Input validation

## Cost
- eBay API: Free (5000 calls/day)
- Redis: ~$10/month
- Total: ~$10/month

