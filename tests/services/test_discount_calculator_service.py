from unittest.mock import Mock
from domain.services.calculator_service import DiscountCalculatorService
from domain.services.discount_resolver_service import DiscountResolverService
from domain.value_objects import CartItem, Money


class TestDiscountCalculatorService:
    """Test DiscountCalculatorService class."""

    def test_create_service(self):
        """Test creating DiscountCalculatorService."""
        mock_resolver = Mock(spec=DiscountResolverService)
        service = DiscountCalculatorService(mock_resolver)
        assert service.discount_resolver_service == mock_resolver

    def test_calculate_total_discount_with_empty_cart(self):
        """Test calculating total discount with empty cart."""
        mock_resolver = Mock(spec=DiscountResolverService)
        service = DiscountCalculatorService(mock_resolver)

        result = service.calculate_total_discount([])

        assert result == 0
        mock_resolver.calculate_discount.assert_not_called()

    def test_calculate_total_discount_with_single_item(self):
        """Test calculating total discount with single cart item."""
        mock_resolver = Mock(spec=DiscountResolverService)
        mock_resolver.calculate_discount.return_value = Money(10, "USD")

        service = DiscountCalculatorService(mock_resolver)
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_total_discount([cart_item])

        assert result.amount == 10
        assert result.currency == "USD"
        mock_resolver.calculate_discount.assert_called_once_with(cart_item)

    def test_calculate_total_discount_with_multiple_items(self):
        """Test calculating total discount with multiple cart items."""
        mock_resolver = Mock(spec=DiscountResolverService)

        # Setup different discounts for different items
        def discount_side_effect(cart_item):
            discounts = {
                "ITEM001": Money(10, "USD"),
                "ITEM002": Money(20, "USD"),
                "ITEM003": Money(15, "USD"),
            }
            return discounts.get(cart_item.code, Money(0, "USD"))

        mock_resolver.calculate_discount.side_effect = discount_side_effect

        service = DiscountCalculatorService(mock_resolver)
        cart_items = [
            CartItem("ITEM001", Money(100, "USD"), 1),
            CartItem("ITEM002", Money(200, "USD"), 1),
            CartItem("ITEM003", Money(150, "USD"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 45  # 10 + 20 + 15
        assert result.currency == "USD"
        assert mock_resolver.calculate_discount.call_count == 3

    def test_calculate_total_discount_with_zero_discounts(self):
        """Test calculating when all items have zero discount."""
        mock_resolver = Mock(spec=DiscountResolverService)
        mock_resolver.calculate_discount.return_value = Money(0, "USD")

        service = DiscountCalculatorService(mock_resolver)
        cart_items = [
            CartItem("ITEM001", Money(100, "USD"), 1),
            CartItem("ITEM002", Money(200, "USD"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 0
        assert result.currency == "USD"

    def test_calculate_calls_resolver_for_each_item(self):
        """Test that resolver is called for each cart item."""
        mock_resolver = Mock(spec=DiscountResolverService)
        mock_resolver.calculate_discount.return_value = Money(5, "USD")

        service = DiscountCalculatorService(mock_resolver)
        cart_item1 = CartItem("ITEM001", Money(100, "USD"), 1)
        cart_item2 = CartItem("ITEM002", Money(200, "USD"), 2)
        cart_item3 = CartItem("ITEM003", Money(150, "USD"), 3)

        service.calculate_total_discount([cart_item1, cart_item2, cart_item3])

        assert mock_resolver.calculate_discount.call_count == 3
        mock_resolver.calculate_discount.assert_any_call(cart_item1)
        mock_resolver.calculate_discount.assert_any_call(cart_item2)
        mock_resolver.calculate_discount.assert_any_call(cart_item3)

    def test_calculate_total_discount_preserves_currency(self):
        """Test that total discount preserves currency."""
        mock_resolver = Mock(spec=DiscountResolverService)
        mock_resolver.calculate_discount.return_value = Money(10, "EUR")

        service = DiscountCalculatorService(mock_resolver)
        cart_items = [
            CartItem("ITEM001", Money(100, "EUR"), 1),
            CartItem("ITEM002", Money(200, "EUR"), 1),
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 20
        assert result.currency == "EUR"

    def test_calculate_total_discount_with_varying_quantities(self):
        """Test calculating discount with items of varying quantities."""
        mock_resolver = Mock(spec=DiscountResolverService)

        def discount_side_effect(cart_item):
            # Each item gets a different discount regardless of quantity
            discounts = {
                "ITEM001": Money(5, "USD"),
                "ITEM002": Money(10, "USD"),
            }
            return discounts.get(cart_item.code, Money(0, "USD"))

        mock_resolver.calculate_discount.side_effect = discount_side_effect

        service = DiscountCalculatorService(mock_resolver)
        cart_items = [
            CartItem("ITEM001", Money(50, "USD"), 5),  # quantity 5
            CartItem("ITEM002", Money(100, "USD"), 2),  # quantity 2
        ]

        result = service.calculate_total_discount(cart_items)

        assert result.amount == 15  # 5 + 10
        assert result.currency == "USD"

    def test_calculate_uses_injected_resolver(self):
        """Test that service uses the injected resolver service."""
        mock_resolver1 = Mock(spec=DiscountResolverService)
        mock_resolver1.calculate_discount.return_value = Money(10, "USD")

        mock_resolver2 = Mock(spec=DiscountResolverService)
        mock_resolver2.calculate_discount.return_value = Money(20, "USD")

        # Create two services with different resolvers
        service1 = DiscountCalculatorService(mock_resolver1)
        service2 = DiscountCalculatorService(mock_resolver2)

        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result1 = service1.calculate_total_discount([cart_item])
        result2 = service2.calculate_total_discount([cart_item])

        assert result1.amount == 10
        assert result2.amount == 20
