"""Discount and coupon tests.

See the "INTENTIONALLY FAILING" comment below for a test that is deliberately
broken to demonstrate Testream failure inspection in Jira.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from datetime import datetime, timezone
from src.discount import Coupon, CouponType, apply_percentage, apply_fixed, validate_coupon, apply_coupon


FUTURE = datetime(2099, 12, 31, tzinfo=timezone.utc)
NOW = datetime(2025, 6, 1, 12, 0, 0, tzinfo=timezone.utc)

PERCENTAGE_COUPON = Coupon(
    code="SUMMER20",
    type=CouponType.PERCENTAGE,
    value=20,
    expires_at=FUTURE,
)

FIXED_COUPON = Coupon(
    code="SAVE500",
    type=CouponType.FIXED,
    value=500,
    expires_at=FUTURE,
)


# ── apply_percentage ──────────────────────────────────────────────────────────

def test_apply_percentage_twenty_percent():
    assert apply_percentage(1000, 20) == 800


def test_apply_percentage_zero_percent():
    assert apply_percentage(1000, 0) == 1000


def test_apply_percentage_hundred_percent():
    assert apply_percentage(1000, 100) == 0


def test_apply_percentage_clamped_to_zero():
    assert apply_percentage(100, 100) >= 0


def test_apply_percentage_raises_for_negative():
    with pytest.raises(ValueError):
        apply_percentage(1000, -1)


def test_apply_percentage_raises_for_over_100():
    with pytest.raises(ValueError):
        apply_percentage(1000, 101)


# ── apply_fixed ───────────────────────────────────────────────────────────────

def test_apply_fixed_subtracts_amount():
    assert apply_fixed(1000, 300) == 700


def test_apply_fixed_clamped_when_exceeds_price():
    assert apply_fixed(200, 500) == 0


def test_apply_fixed_zero_discount():
    assert apply_fixed(1000, 0) == 1000


def test_apply_fixed_raises_for_negative():
    with pytest.raises(ValueError):
        apply_fixed(1000, -1)


# ── validate_coupon ───────────────────────────────────────────────────────────

def test_validate_coupon_valid_percentage():
    assert validate_coupon(PERCENTAGE_COUPON, 5000, NOW) == []


def test_validate_coupon_valid_fixed():
    assert validate_coupon(FIXED_COUPON, 5000, NOW) == []


def test_validate_coupon_expired():
    expired = Coupon(
        code="OLD10",
        type=CouponType.PERCENTAGE,
        value=10,
        expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    errors = validate_coupon(expired, 5000, NOW)
    assert "Coupon has expired" in errors


def test_validate_coupon_minimum_order_not_met():
    coupon = Coupon(
        code="BIG20",
        type=CouponType.PERCENTAGE,
        value=20,
        expires_at=FUTURE,
        min_order_value=10000,
    )
    errors = validate_coupon(coupon, 5000, NOW)
    assert any("Minimum order value" in e for e in errors)


# ─────────────────────────────────────────────────────────────────────────────
# INTENTIONALLY FAILING TEST
#
# This test checks that an expired coupon with an unmet minimum order value
# produces 3 validation errors. The real implementation returns 2.
# Testream will flag this in Jira with the exact diff.
# ─────────────────────────────────────────────────────────────────────────────
def test_validate_coupon_multiple_errors():
    bad_coupon = Coupon(
        code="BAD",
        type=CouponType.PERCENTAGE,
        value=10,
        expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
        min_order_value=20000,
    )
    errors = validate_coupon(bad_coupon, 5000, NOW)
    # BUG: expects 3 errors but only 2 are returned (expired + min order)
    assert len(errors) == 3, f"Expected 3 validation errors but got: {errors}"


# ── apply_coupon ──────────────────────────────────────────────────────────────

def test_apply_coupon_percentage():
    assert apply_coupon(1000, PERCENTAGE_COUPON, NOW) == 800  # 20% off


def test_apply_coupon_fixed():
    assert apply_coupon(1000, FIXED_COUPON, NOW) == 500  # 500 off


def test_apply_coupon_raises_for_expired():
    expired = Coupon(
        code="OLD10",
        type=CouponType.PERCENTAGE,
        value=10,
        expires_at=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    with pytest.raises(ValueError, match="Coupon has expired"):
        apply_coupon(1000, expired, NOW)
