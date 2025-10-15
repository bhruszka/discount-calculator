from domain.entities.discount import AmountDiscount, PercentageDiscount
from domain.entities.discount_condition import (
    MinQuantityDiscountCondition,
    ProductCodeDiscountCondition,
)
from domain.services.calculator_service import DiscountCalculatorService
from domain.value_objects import CartItem, Money, Percentage


class TestDiscountSystemIntegration:
    """Integration tests for the complete discount system."""

    def test_fixed_discount_on_all_products(self):
        """Test fixed discount (-100 EUR) applies to all products."""
        # Setup: Fixed 100 EUR discount on all products
        fixed_discount = AmountDiscount(Money(100, "EUR"), conditions=None)
        calculator = DiscountCalculatorService([fixed_discount])

        # Cart with multiple items
        cart_items = [
            CartItem("ITEM001", Money(500, "EUR"), 1),
            CartItem("ITEM002", Money(300, "EUR"), 2),
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        # Both items get 100 EUR discount
        assert total_discount.amount == 200  # 100 + 100
        assert total_discount.currency == "EUR"

    def test_percentage_discount_on_all_products(self):
        """Test percentage discount (-10%) applies to all products."""
        # Setup: 10% discount on all products
        percentage_discount = PercentageDiscount(Percentage(10), conditions=None)
        calculator = DiscountCalculatorService([percentage_discount])

        # Cart with multiple items
        cart_items = [
            CartItem("ITEM001", Money(100, "EUR"), 1),  # 10 EUR discount
            CartItem("ITEM002", Money(200, "EUR"), 1),  # 20 EUR discount
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 30  # 10 + 20
        assert total_discount.currency == "EUR"

    def test_volume_discount_minimum_quantity(self):
        """Test volume discount (-100 EUR if at least 10 products bought)."""
        # Setup: 100 EUR discount if at least 10 products
        volume_condition = MinQuantityDiscountCondition(min_quantity=10)
        volume_discount = AmountDiscount(
            Money(100, "EUR"), conditions=[volume_condition]
        )
        calculator = DiscountCalculatorService([volume_discount])

        # Cart with items meeting and not meeting volume requirement
        cart_items = [
            CartItem("ITEM001", Money(500, "EUR"), 10),  # Qualifies: 100 EUR discount
            CartItem(
                "ITEM002", Money(300, "EUR"), 5
            ),  # Does not qualify: 0 EUR discount
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 100  # Only first item qualifies
        assert total_discount.currency == "EUR"

    def test_discount_on_specific_product_codes(self):
        """Test discount applies only to specific product codes."""
        # Setup: 50 EUR discount only for ITEM001 and ITEM002
        product_condition = ProductCodeDiscountCondition({"ITEM001", "ITEM002"})
        specific_discount = AmountDiscount(
            Money(50, "EUR"), conditions=[product_condition]
        )
        calculator = DiscountCalculatorService([specific_discount])

        # Cart with items that match and don't match
        cart_items = [
            CartItem("ITEM001", Money(200, "EUR"), 1),  # Qualifies: 50 EUR
            CartItem("ITEM002", Money(200, "EUR"), 1),  # Qualifies: 50 EUR
            CartItem("ITEM003", Money(200, "EUR"), 1),  # Does not qualify: 0 EUR
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 100  # 50 + 50 + 0
        assert total_discount.currency == "EUR"

    def test_only_one_discount_applies_per_cart_line(self):
        """Test that only the best discount applies per cart line."""
        # Setup: Multiple discounts - best one should be selected
        small_discount = AmountDiscount(Money(10, "USD"), conditions=None)
        medium_discount = AmountDiscount(Money(50, "USD"), conditions=None)
        large_discount = AmountDiscount(Money(100, "USD"), conditions=None)

        calculator = DiscountCalculatorService(
            [small_discount, medium_discount, large_discount]
        )

        # Cart with one item
        cart_items = [
            CartItem("ITEM001", Money(500, "USD"), 1),
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        # Only the best (largest) discount applies
        assert total_discount.amount == 100
        assert total_discount.currency == "USD"

    def test_volume_discount_on_specific_products(self):
        """Test volume discount combined with product code condition."""
        # Setup: 100 EUR discount on ITEM001 if at least 5 products
        volume_condition = MinQuantityDiscountCondition(min_quantity=5)
        product_condition = ProductCodeDiscountCondition({"ITEM001"})
        combined_discount = AmountDiscount(
            Money(100, "EUR"), conditions=[volume_condition, product_condition]
        )

        calculator = DiscountCalculatorService([combined_discount])

        # Cart with various items
        cart_items = [
            CartItem("ITEM001", Money(500, "EUR"), 5),  # Qualifies: both conditions met
            CartItem(
                "ITEM001", Money(500, "EUR"), 3
            ),  # Does not qualify: quantity too low
            CartItem(
                "ITEM002", Money(500, "EUR"), 10
            ),  # Does not qualify: wrong product code
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 100  # Only first item qualifies
        assert total_discount.currency == "EUR"

    def test_percentage_volume_discount(self):
        """Test percentage discount with volume condition."""
        # Setup: 20% discount if at least 10 products
        volume_condition = MinQuantityDiscountCondition(min_quantity=10)
        percentage_volume_discount = PercentageDiscount(
            Percentage(20), conditions=[volume_condition]
        )

        calculator = DiscountCalculatorService([percentage_volume_discount])

        # Cart items
        cart_items = [
            CartItem(
                "ITEM001", Money(100, "USD"), 10
            ),  # Qualifies: 20% of 100 = 20 USD
            CartItem("ITEM002", Money(200, "USD"), 5),  # Does not qualify: 0 USD
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 20
        assert total_discount.currency == "USD"

    def test_discount_capped_at_item_total_price(self):
        """Test that discount cannot exceed the total price of cart item."""
        # Setup: Very large discount (more than item price)
        huge_discount = AmountDiscount(Money(1000, "EUR"), conditions=None)
        calculator = DiscountCalculatorService([huge_discount])

        # Cart with low-priced item
        cart_items = [
            CartItem(
                "ITEM001", Money(50, "EUR"), 2
            ),  # Total: 100 EUR, discount capped at 100
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        # Discount is capped at total price
        assert total_discount.amount == 100  # Not 1000
        assert total_discount.currency == "EUR"

    def test_empty_cart(self):
        """Test that empty cart returns zero discount."""
        discount = AmountDiscount(Money(100, "EUR"), conditions=None)
        calculator = DiscountCalculatorService([discount])

        total_discount = calculator.calculate_total_discount([])

        assert total_discount == 0

    def test_no_discounts_available(self):
        """Test that cart with no applicable discounts returns zero."""
        # Setup: Discount only for ITEM999
        product_condition = ProductCodeDiscountCondition({"ITEM999"})
        specific_discount = AmountDiscount(
            Money(100, "EUR"), conditions=[product_condition]
        )
        calculator = DiscountCalculatorService([specific_discount])

        # Cart with different items
        cart_items = [
            CartItem("ITEM001", Money(200, "EUR"), 1),
            CartItem("ITEM002", Money(300, "EUR"), 1),
        ]

        # Calculate total discount
        total_discount = calculator.calculate_total_discount(cart_items)

        assert total_discount.amount == 0
        assert total_discount.currency == "EUR"
