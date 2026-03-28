"""Minimal A2A Marketplace using Strands"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Listing:
    id: str
    seller_id: str
    name: str
    price: float
    status: str = "available"

@dataclass
class Transaction:
    id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    price: float
    status: str = "pending"

class Marketplace:
    def __init__(self):
        self.listings = {}
        self.transactions = {}

    def create_listing(self, listing: Listing):
        self.listings[listing.id] = listing
        return listing

    def get_available_listings(self):
        return [l for l in self.listings.values() if l.status == "available"]

    def create_transaction(self, listing_id: str, buyer_id: str):
        listing = self.listings.get(listing_id)
        if not listing or listing.status != "available":
            return None

        tx = Transaction(
            id=f"tx_{len(self.transactions)}",
            listing_id=listing_id,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            price=listing.price
        )
        self.transactions[tx.id] = tx
        return tx

    def confirm_transaction(self, tx_id: str):
        tx = self.transactions.get(tx_id)
        if tx:
            tx.status = "confirmed"
            self.listings[tx.listing_id].status = "sold"
        return tx

marketplace = Marketplace()
