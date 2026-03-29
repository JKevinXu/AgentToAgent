"""Real Browser-Based Price Scraper"""
from playwright.sync_api import sync_playwright
import re

def scrape_amazon_price(product_name):
    """Scrape real price from Amazon"""
    print(f"[Amazon] Opening browser for: {product_name}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Search Amazon
            search_url = f"https://www.amazon.com/s?k={product_name.replace(' ', '+')}"
            print(f"[Amazon] Navigating to: {search_url}")
            page.goto(search_url, timeout=10000)

            # Wait for results
            print(f"[Amazon] Waiting for search results...")
            page.wait_for_selector('[data-component-type="s-search-result"]', timeout=5000)

            # Extract first result price
            price_elem = page.query_selector('.a-price .a-offscreen')
            if price_elem:
                price_text = price_elem.inner_text()
                price = float(re.sub(r'[^\d.]', '', price_text))

                # Get product title
                title_elem = page.query_selector('h2 .a-text-normal')
                title = title_elem.inner_text() if title_elem else "Unknown"

                print(f"[Amazon] Found: {title} - ${price}")
                browser.close()
                return {"site": "Amazon", "price": price, "title": title}

            print(f"[Amazon] No price found")
            browser.close()
    except Exception as e:
        print(f"[Amazon] Error: {e}")
    return None

def scrape_ebay_price(product_name):
    """Scrape real price from eBay"""
    print(f"[eBay] Opening browser for: {product_name}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            search_url = f"https://www.ebay.com/sch/i.html?_nkw={product_name.replace(' ', '+')}"
            print(f"[eBay] Navigating to: {search_url}")
            page.goto(search_url, timeout=10000)

            # Extract first result price
            print(f"[eBay] Extracting price...")
            price_elem = page.query_selector('.s-item__price')
            if price_elem:
                price_text = price_elem.inner_text()
                price = float(re.sub(r'[^\d.]', '', price_text))
                print(f"[eBay] Found price: ${price}")
                browser.close()
                return {"site": "eBay", "price": price}

            print(f"[eBay] No price found")
            browser.close()
    except Exception as e:
        print(f"[eBay] Error: {e}")
    return None

def scrape_prices(product_name):
    """Scrape prices from multiple sources"""
    print(f"Scraping prices for: {product_name}")
    sources = []

    result = scrape_amazon_price(product_name)
    if result:
        sources.append(result)

    result = scrape_ebay_price(product_name)
    if result:
        sources.append(result)

    return sources

if __name__ == "__main__":
    prices = scrape_prices("Laptop")
    print(f"Found: {prices}")



