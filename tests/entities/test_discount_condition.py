import pytest
from domain.entities.discount_condition import (
    DiscountCondition,
    MinQuantityDiscountCondition,
    ProductCodeDiscountCondition,
)
from domain.value_objects import CartItem, Money


class TestDiscountCondition:
    """Test base DiscountCondition class."""

    def test_is_eligible_not_implemented(self, cart_item_usd):
        """Test that base class raises NotImplementedError."""
        condition = DiscountCondition()
        with pytest.raises(NotImplementedError):
            condition.is_eligible(cart_item_usd)


class TestMinQuantityDiscountCondition:
    """Test MinQuantityDiscountCondition."""

    def test_eligible_when_quantity_meets_minimum(self, cart_item_multiple_quantity):
        """Test eligibility when quantity meets minimum."""
        condition = MinQuantityDiscountCondition(min_quantity=3)
        assert condition.is_eligible(cart_item_multiple_quantity) is True

    def test_eligible_when_quantity_exceeds_minimum(self, cart_item_high_quantity):
        """Test eligibility when quantity exceeds minimum."""
        condition = MinQuantityDiscountCondition(min_quantity=3)
        assert condition.is_eligible(cart_item_high_quantity) is True

    def test_not_eligible_when_quantity_below_minimum(self):
        """Test not eligible when quantity is below minimum."""
        condition = MinQuantityDiscountCondition(min_quantity=3)
        cart_item = CartItem("ITEM001", Money(100, "USD"), 2)
        assert condition.is_eligible(cart_item) is False


class TestProductCodeDiscountCondition:
    """Test ProductCodeDiscountCondition."""

    def test_eligible_when_code_in_set(self, cart_item_usd):
        """Test eligibility when product code is in allowed set."""
        condition = ProductCodeDiscountCondition({"ITEM001", "ITEM002", "ITEM003"})
        assert condition.is_eligible(cart_item_usd) is True

    def test_not_eligible_when_code_not_in_set(self):
        """Test not eligible when product code is not in allowed set."""
        condition = ProductCodeDiscountCondition({"ITEM001", "ITEM002", "ITEM003"})
        cart_item = CartItem("ITEM999", Money(100, "USD"), 1)
        assert condition.is_eligible(cart_item) is False

    def test_eligible_with_single_code(self, cart_item_usd):
        """Test eligibility with single product code in set."""
        condition = ProductCodeDiscountCondition({"ITEM001"})
        assert condition.is_eligible(cart_item_usd) is True

    def test_not_eligible_with_empty_set(self, cart_item_usd):
        """Test not eligible with empty product code set."""
        condition = ProductCodeDiscountCondition(set())
        assert condition.is_eligible(cart_item_usd) is False

    def test_case_sensitive_matching(self):
        """Test that product code matching is case sensitive."""
        condition = ProductCodeDiscountCondition({"ITEM001"})
        cart_item = CartItem("item001", Money(100, "USD"), 1)
        assert condition.is_eligible(cart_item) is False
