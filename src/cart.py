"""Shopping cart implementation.

Used by the pytest test suite to generate realistic CTRF test results
that are uploaded to Jira via @testream/upload-action (Testream CLI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CartItem:
    id: str
    name: str
    price: int  # unit price in pence/cents
    quantity: int


class Cart:
    """A simple in-memory shopping cart."""

    def __init__(self) -> None:
        self._items: Dict[str, CartItem] = {}

    def add_item(self, item_id: str, name: str, price: int, quantity: int = 1) -> None:
        """Add a product to the cart, or increment its quantity if already present."""
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        if item_id in self._items:
            self._items[item_id].quantity += quantity
        else:
            self._items[item_id] = CartItem(id=item_id, name=name, price=price, quantity=quantity)

    def remove_item(self, item_id: str, quantity: int = 1) -> None:
        """Decrease quantity by *quantity*. Removes the item when quantity reaches 0."""
        if item_id not in self._items:
            raise KeyError(f'Item "{item_id}" not found in cart')
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")
        item = self._items[item_id]
        if item.quantity <= quantity:
            del self._items[item_id]
        else:
            item.quantity -= quantity

    def get_total(self) -> int:
        """Return the total price (sum of price × quantity for every item)."""
        return sum(i.price * i.quantity for i in self._items.values())

    def get_items(self) -> List[CartItem]:
        """Return a snapshot of all cart items."""
        return list(self._items.values())

    def clear(self) -> None:
        """Remove all items from the cart."""
        self._items.clear()

    def is_empty(self) -> bool:
        """True when the cart contains no items."""
        return len(self._items) == 0

    def checkout(self) -> dict:
        """Validate and lock the cart for checkout. Raises if the cart is empty."""
        if self.is_empty():
            raise ValueError("Cannot check out with an empty cart")
        return {"items": self.get_items(), "total": self.get_total()}
