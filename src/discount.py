"""Discount and coupon logic.

Used by the pytest test suite to generate realistic CTRF test results
that are uploaded to Jira via @testream/upload-action (Testream CLI).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional


class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


@dataclass
class Coupon:
    code: str
    type: CouponType
    value: int  # percentage (0-100) or fixed amount in pence/cents
    expires_at: datetime
    min_order_value: Optional[int] = None  # minimum cart total in pence/cents


def apply_percentage(price_in_cents: int, percent: int) -> int:
    """Apply a percentage discount to a price. Returns the discounted price, clamped to 0."""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return max(0, round(price_in_cents * (1 - percent / 100)))


def apply_fixed(price_in_cents: int, discount_in_cents: int) -> int:
    """Apply a fixed discount to a price. Returns the discounted price, clamped to 0."""
    if discount_in_cents < 0:
        raise ValueError("discount amount must be non-negative")
    return max(0, price_in_cents - discount_in_cents)


def validate_coupon(coupon: Coupon, cart_total: int, now: Optional[datetime] = None) -> List[str]:
    """Validate a coupon against the current time and cart total.

    Returns a list of error messages. An empty list means the coupon is valid.
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)
    errors: List[str] = []

    if coupon.expires_at < now:
        errors.append("Coupon has expired")

    if coupon.min_order_value is not None and cart_total < coupon.min_order_value:
        errors.append(
            f"Minimum order value not met (requires {coupon.min_order_value} cents,"
            f" cart is {cart_total} cents)"
        )

    if coupon.type == CouponType.PERCENTAGE and not (0 <= coupon.value <= 100):
        errors.append("Percentage coupon value must be between 0 and 100")

    if coupon.type == CouponType.FIXED and coupon.value < 0:
        errors.append("Fixed coupon value must be non-negative")

    return errors


def apply_coupon(price_in_cents: int, coupon: Coupon, now: Optional[datetime] = None) -> int:
    """Apply a coupon to a price. Raises ValueError if the coupon has validation errors."""
    errors = validate_coupon(coupon, price_in_cents, now)
    if errors:
        raise ValueError("; ".join(errors))

    if coupon.type == CouponType.PERCENTAGE:
        return apply_percentage(price_in_cents, coupon.value)
    return apply_fixed(price_in_cents, coupon.value)
