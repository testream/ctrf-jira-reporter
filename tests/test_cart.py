"""Cart tests.

These tests cover the core shopping-cart behaviour.
One test is deliberately broken to demonstrate how Testream surfaces
failures in the Jira dashboard — with the error diff and stack trace
visible, and a one-click button to create a Jira issue from the failed test.

Look for the "INTENTIONALLY FAILING" comment below.
"""

import sys
import os

# Add the project root to the path so `src` can be imported directly.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.cart import Cart


APPLE_ID = "prod-001"
APPLE_NAME = "Apple"
APPLE_PRICE = 120  # 1.20 in pence/cents

BANANA_ID = "prod-002"
BANANA_NAME = "Banana"
BANANA_PRICE = 80  # 0.80 in pence/cents


# ── adding items ──────────────────────────────────────────────────────────────

def test_add_item_default_quantity():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE)
    items = cart.get_items()
    assert len(items) == 1
    assert items[0].quantity == 1


def test_add_item_specified_quantity():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=3)
    assert cart.get_items()[0].quantity == 3


def test_add_item_increments_quantity_for_duplicate():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=2)
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=1)
    assert cart.get_items()[0].quantity == 3


def test_add_item_holds_multiple_different_items():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE)
    cart.add_item(BANANA_ID, BANANA_NAME, BANANA_PRICE)
    assert len(cart.get_items()) == 2


def test_add_item_raises_for_zero_quantity():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=0)


def test_add_item_raises_for_negative_quantity():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=-1)


# ── removing items ────────────────────────────────────────────────────────────

def test_remove_item_decrements_quantity():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=3)
    cart.remove_item(APPLE_ID, quantity=2)
    assert cart.get_items()[0].quantity == 1


def test_remove_item_removes_item_at_zero():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=3)
    cart.remove_item(APPLE_ID, quantity=3)
    assert cart.is_empty()


def test_remove_item_removes_when_quantity_exceeds_stock():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=3)
    cart.remove_item(APPLE_ID, quantity=99)
    assert cart.is_empty()


def test_remove_item_raises_for_missing_item():
    cart = Cart()
    with pytest.raises(KeyError, match="does-not-exist"):
        cart.remove_item("does-not-exist")


# ── totals ────────────────────────────────────────────────────────────────────

def test_total_is_zero_for_empty_cart():
    assert Cart().get_total() == 0


def test_total_for_single_item():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=2)  # 2 × 120 = 240
    assert cart.get_total() == 240


def test_total_for_multiple_items():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=2)   # 240
    cart.add_item(BANANA_ID, BANANA_NAME, BANANA_PRICE, quantity=3)  # 240
    assert cart.get_total() == 480


# ── clear ─────────────────────────────────────────────────────────────────────

def test_clear_empties_the_cart():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE)
    cart.add_item(BANANA_ID, BANANA_NAME, BANANA_PRICE)
    cart.clear()
    assert cart.is_empty()
    assert len(cart.get_items()) == 0


# ── checkout ──────────────────────────────────────────────────────────────────

def test_checkout_returns_items_and_total():
    cart = Cart()
    cart.add_item(APPLE_ID, APPLE_NAME, APPLE_PRICE, quantity=2)
    result = cart.checkout()
    assert result["total"] == 240
    assert len(result["items"]) == 1


# ─────────────────────────────────────────────────────────────────────────────
# INTENTIONALLY FAILING TEST
#
# This test asserts the wrong exception message to simulate a real-world
# regression. In Testream you will see the exact error diff, the full
# stack trace, and you can open a Jira issue for it in one click.
# ─────────────────────────────────────────────────────────────────────────────
def test_checkout_raises_descriptive_error_for_empty_cart():
    cart = Cart()
    with pytest.raises(ValueError) as exc_info:
        cart.checkout()
    # BUG: wrong expected message — the real message is
    # "Cannot check out with an empty cart"
    assert exc_info.value.args[0] == "Cart is empty"
