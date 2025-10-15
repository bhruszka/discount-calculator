from domain.entities.discount import AmountDiscount
from domain.entities.discount_condition import ProductCodeDiscountCondition
from domain.services.calculator_service import DiscountCalculatorService
from domain.services.discount_resolver_service import DiscountResolverService
from domain.value_objects import CartItem, Money


class TestDiscountCalculatorService:
    """Test DiscountCalculatorService class."""

    def test_create_service(self):
        """Test creating DiscountCalculatorService with discounts."""
        discount = AmountDiscount(Money(10, "USD"), conditions=None)
        service = DiscountCalculatorService([discount])
        assert service.discount_resolver_service is not None

    def test_calculate_total_discount_with_empty_cart(self):
        """Test calculating total discount with empty cart."""
        discount = AmountDiscount(Money(10, "USD"), conditions=None)
        service = DiscountCalculatorService([discount])

        result = service.calculate_total_discount([])

        assert result == 0

    def test_calculate_total_discount_with_single_item(self):
        """Test calculating total discount with single cart item."""
        discount = AmountDiscount(Money(10, "USD"), conditions=None)
        service = DiscountCalculatorService([discount])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_total_discount([cart_item])

        assert result.amount == 10
        assert result.currency == "USD"

    def test_calculate_total_discount_with_multiple_items(self):
        """Test calculating total discount with multiple cart items."""
        # Different discounts for different items
        discount1 = AmountDiscount(
            Money(10, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM001"})]
        )
        discount2 = AmountDiscount(
            Money(20, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM002"})]
        )
        discount3 = AmountDiscount(
            Money(15, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM003"})]
        )

        service = DiscountCalculatorService([discount1, discount2, discount3])
        cart_items = [
            CartItem("ITEM001", Money(100, "USD"), 1),
            CartItem("ITEM002", Money(200, "USD"), 1),
            CartItem("ITEM003", Money(150, "USD"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 45  # 10 + 20 + 15
        assert result.currency == "USD"

    def test_calculate_total_discount_with_zero_discounts(self):
        """Test calculating when all items have zero discount."""
        # Discount that doesn't match any items
        discount = AmountDiscount(
            Money(10, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM999"})]
        )
        service = DiscountCalculatorService([discount])
        cart_items = [
            CartItem("ITEM001", Money(100, "USD"), 1),
            CartItem("ITEM002", Money(200, "USD"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 0
        assert result.currency == "USD"

    def test_calculate_applies_discount_to_each_item(self):
        """Test that discount is applied to each eligible cart item."""
        discount = AmountDiscount(Money(5, "USD"), conditions=None)
        service = DiscountCalculatorService([discount])
        cart_items = [
            CartItem("ITEM001", Money(100, "USD"), 1),
            CartItem("ITEM002", Money(200, "USD"), 2),
            CartItem("ITEM003", Money(150, "USD"), 3),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 15  # 5 + 5 + 5
        assert result.currency == "USD"

    def test_calculate_total_discount_preserves_currency(self):
        """Test that total discount preserves currency."""
        discount = AmountDiscount(Money(10, "EUR"), conditions=None)
        service = DiscountCalculatorService([discount])
        cart_items = [
            CartItem("ITEM001", Money(100, "EUR"), 1),
            CartItem("ITEM002", Money(200, "EUR"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 20
        assert result.currency == "EUR"

    def test_calculate_total_discount_with_varying_quantities(self):
        """Test calculating discount with items of varying quantities."""
        discount1 = AmountDiscount(
            Money(5, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM001"})]
        )
        discount2 = AmountDiscount(
            Money(10, "USD"), conditions=[ProductCodeDiscountCondition({"ITEM002"})]
        )

        service = DiscountCalculatorService([discount1, discount2])
        cart_items = [
            CartItem("ITEM001", Money(50, "USD"), 5),  # quantity 5
            CartItem("ITEM002", Money(100, "USD"), 2),  # quantity 2
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 15  # 5 + 10
        assert result.currency == "USD"

    def test_custom_resolver_class(self):
        """Test that service accepts custom resolver_class."""

        # Create a custom resolver class that returns a fixed discount
        class CustomResolver(DiscountResolverService):
            def _calculate_discount(self, cart_item: CartItem) -> Money:
                return Money(100, cart_item.price.currency)

        discount = AmountDiscount(Money(10, "USD"), conditions=None)
        service = DiscountCalculatorService([discount], resolver_class=CustomResolver)

        cart_item = CartItem("ITEM001", Money(200, "USD"), 1)
        result = service.calculate_total_discount([cart_item])

        # Custom resolver always returns 100, not the discount amount
        assert result.amount == 100
        assert result.currency == "USD"
