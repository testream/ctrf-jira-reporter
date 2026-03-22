"""Product tests.

These tests cover product validation, price formatting, discount calculation,
and stock checking.

See the "INTENTIONALLY FAILING" comment below for a test that is deliberately
broken to demonstrate Testream failure inspection in Jira.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.product import Product, format_price, validate_product, get_discounted_price


VALID_PRODUCT = Product(
    id="prod-001",
    name="Wireless Headphones",
    price=7999,
    stock=42,
    category="Electronics",
)


# ── format_price ──────────────────────────────────────────────────────────────

def test_format_price_usd():
    assert format_price(1999) == "$19.99"


def test_format_price_gbp():
    assert format_price(7999, "GBP") == "£79.99"


def test_format_price_zero():
    assert format_price(0) == "$0.00"


def test_format_price_whole_dollars():
    assert format_price(1000) == "$10.00"


# ── validate_product ──────────────────────────────────────────────────────────

def test_validate_returns_no_errors_for_valid_product():
    assert validate_product(VALID_PRODUCT) == []


def test_validate_error_for_missing_id():
    p = Product(id="", name="Headphones", price=7999, stock=42, category="Electronics")
    assert "id is required" in validate_product(p)


def test_validate_error_for_missing_name():
    p = Product(id="prod-001", name="", price=7999, stock=42, category="Electronics")
    assert "name is required" in validate_product(p)


def test_validate_error_for_negative_price():
    p = Product(id="prod-001", name="Headphones", price=-1, stock=42, category="Electronics")
    assert "price must be a non-negative number" in validate_product(p)


def test_validate_error_for_negative_stock():
    p = Product(id="prod-001", name="Headphones", price=7999, stock=-5, category="Electronics")
    assert "stock must be a non-negative number" in validate_product(p)


def test_validate_error_for_missing_category():
    p = Product(id="prod-001", name="Headphones", price=7999, stock=42, category="")
    assert "category is required" in validate_product(p)


# ─────────────────────────────────────────────────────────────────────────────
# INTENTIONALLY FAILING TEST
#
# This test checks that a product with multiple missing fields produces
# 2 validation errors. The real implementation returns 4.
# Testream will show the exact assertion diff in the Jira dashboard.
# ─────────────────────────────────────────────────────────────────────────────
def test_validate_multiple_errors_for_missing_fields():
    # id="", name="", price=999, stock=-1, category="" → 4 errors (id, name, stock, category)
    p = Product(id="", name="", price=999, stock=-1, category="")
    errors = validate_product(p)
    # BUG: expects 2 errors but there are actually 4 (id, name, stock, category)
    assert len(errors) == 2, f"Expected 2 validation errors but got: {errors}"


# ── get_discounted_price ──────────────────────────────────────────────────────

def test_discounted_price_ten_percent():
    assert get_discounted_price(1000, 10) == 900


def test_discounted_price_fifty_percent():
    assert get_discounted_price(1000, 50) == 500


def test_discounted_price_hundred_percent():
    assert get_discounted_price(1000, 100) == 0


def test_discounted_price_zero_percent():
    assert get_discounted_price(1000, 0) == 1000


def test_discounted_price_raises_for_negative():
    with pytest.raises(ValueError):
        get_discounted_price(1000, -1)


def test_discounted_price_raises_for_over_100():
    with pytest.raises(ValueError):
        get_discounted_price(1000, 101)


# ── is_in_stock ───────────────────────────────────────────────────────────────

def test_is_in_stock_when_positive():
    assert VALID_PRODUCT.is_in_stock() is True


def test_is_out_of_stock_when_zero():
    p = Product(id="prod-001", name="Headphones", price=7999, stock=0, category="Electronics")
    assert p.is_in_stock() is False
