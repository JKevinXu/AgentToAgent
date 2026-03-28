"""Demo: A2A Marketplace"""
from marketplace import marketplace, Listing, Transaction

# Seller creates listings
listing1 = Listing(id="item_0", seller_id="seller", name="Laptop", price=80)
listing2 = Listing(id="item_1", seller_id="seller", name="Phone", price=50)

marketplace.create_listing(listing1)
marketplace.create_listing(listing2)

print("Available listings:")
for l in marketplace.get_available_listings():
    print(f"  {l.id}: {l.name} - ${l.price}")

# Buyer purchases
tx = marketplace.create_transaction("item_1", "buyer")
print(f"\nTransaction created: {tx.id}")

# Seller confirms
marketplace.confirm_transaction(tx.id)
print(f"Transaction confirmed: {tx.status}")
print(f"Listing status: {marketplace.listings['item_1'].status}")
