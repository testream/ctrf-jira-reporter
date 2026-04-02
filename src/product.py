"""Product helpers.

Used by the pytest test suite to generate realistic CTRF test results
that are uploaded to Jira via @testream/cli (Testream CLI).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    id: str
    name: str
    price: int  # in pence/cents
    stock: int
    category: str

    def is_in_stock(self) -> bool:
        """Returns True when the product has at least one unit in stock."""
        return self.stock > 0


def format_price(amount_in_cents: int, currency: str = "USD") -> str:
    """Format a price in pence/cents into a human-readable currency string.

    e.g. format_price(1999) → "$19.99"
    """
    symbols = {"USD": "$", "GBP": "£", "EUR": "€"}
    symbol = symbols.get(currency, currency + " ")
    amount = amount_in_cents / 100
    return f"{symbol}{amount:.2f}"


def validate_product(product: Product) -> List[str]:
    """Validate that a product contains all required fields with valid values.

    Returns a list of error messages. An empty list means the product is valid.
    """
    errors: List[str] = []
    if not product.id or not product.id.strip():
        errors.append("id is required")
    if not product.name or not product.name.strip():
        errors.append("name is required")
    if product.price < 0:
        errors.append("price must be a non-negative number")
    if product.stock < 0:
        errors.append("stock must be a non-negative number")
    if not product.category or not product.category.strip():
        errors.append("category is required")
    return errors


def get_discounted_price(price_in_cents: int, discount_percent: int) -> int:
    """Apply a percentage discount and return the discounted price.

    Raises ValueError if discount_percent is outside [0, 100].
    """
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError("discount_percent must be between 0 and 100")
    return max(0, round(price_in_cents * (1 - discount_percent / 100)))
