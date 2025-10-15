import pytest
from unittest.mock import Mock
from domain.services.discount_resolver_service import (
    DiscountResolverService,
    BestDiscountResolverService,
)
from domain.entities.discount import Discount
from domain.value_objects import CartItem, Money


class TestDiscountResolverService:
    """Test base DiscountResolverService class."""

    def test_create_with_discounts(self):
        """Test creating service with discount list."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount2 = Mock(spec=Discount)
        service = DiscountResolverService([mock_discount1, mock_discount2])
        assert len(service.discounts) == 2

    def test_calculate_discount_not_implemented(self):
        """Test that base class _calculate_discount raises NotImplementedError."""
        service = DiscountResolverService([])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)
        with pytest.raises(NotImplementedError):
            service._calculate_discount(cart_item)

    def test_calculate_discount_caps_at_total_price(self):
        """Test that discount is capped at total price."""
        mock_discount = Mock(spec=Discount)
        service = BestDiscountResolverService([mock_discount])

        # Mock a discount that returns more than the item price
        mock_discount.calculate.return_value = Money(500, "USD")

        cart_item = CartItem("ITEM001", Money(100, "USD"), 3)  # total: 300 USD

        result = service.calculate_discount(cart_item)

        # Should be capped at total price (300)
        assert result.amount == 300
        assert result.currency == "USD"

    def test_calculate_discount_below_total_price(self):
        """Test discount that is below total price."""
        mock_discount = Mock(spec=Discount)
        service = BestDiscountResolverService([mock_discount])

        mock_discount.calculate.return_value = Money(50, "USD")

        cart_item = CartItem("ITEM001", Money(100, "USD"), 3)  # total: 300 USD

        result = service.calculate_discount(cart_item)

        assert result.amount == 50
        assert result.currency == "USD"


class TestBestDiscountResolverService:
    """Test BestDiscountResolverService class."""

    def test_create_service(self):
        """Test creating BestDiscountResolverService."""
        mock_discount = Mock(spec=Discount)
        service = BestDiscountResolverService([mock_discount])
        assert len(service.discounts) == 1

    def test_calculate_discount_with_no_discounts(self):
        """Test calculating discount with no discounts returns zero."""
        service = BestDiscountResolverService([])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        assert result.amount == 0
        assert result.currency == "USD"

    def test_calculate_discount_with_single_discount(self):
        """Test calculating with single applicable discount."""
        mock_discount = Mock(spec=Discount)
        mock_discount.calculate.return_value = Money(10, "USD")

        service = BestDiscountResolverService([mock_discount])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        assert result.amount == 10
        assert result.currency == "USD"
        mock_discount.calculate.assert_called_once_with(cart_item)

    def test_selects_best_discount_from_multiple(self):
        """Test that service selects highest discount from multiple options."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = Money(10, "USD")

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = Money(25, "USD")

        mock_discount3 = Mock(spec=Discount)
        mock_discount3.calculate.return_value = Money(15, "USD")

        service = BestDiscountResolverService(
            [mock_discount1, mock_discount2, mock_discount3]
        )
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        assert result.amount == 25
        assert result.currency == "USD"

    def test_ignores_none_discounts(self):
        """Test that None discounts are ignored."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = None

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = Money(20, "USD")

        mock_discount3 = Mock(spec=Discount)
        mock_discount3.calculate.return_value = None

        service = BestDiscountResolverService(
            [mock_discount1, mock_discount2, mock_discount3]
        )
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        assert result.amount == 20
        assert result.currency == "USD"

    def test_all_discounts_none_returns_zero(self):
        """Test that all None discounts returns zero."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = None

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = None

        service = BestDiscountResolverService([mock_discount1, mock_discount2])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        assert result.amount == 0
        assert result.currency == "USD"

    def test_equal_discounts_returns_first_found(self):
        """Test behavior when multiple discounts have equal value."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = Money(20, "USD")

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = Money(20, "USD")

        service = BestDiscountResolverService([mock_discount1, mock_discount2])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        result = service.calculate_discount(cart_item)

        # Should return 20 (both are equal, implementation picks first one matched)
        assert result.amount == 20
        assert result.currency == "USD"

    def test_calls_all_discount_calculations(self):
        """Test that all discount calculations are called."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = Money(10, "USD")

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = Money(15, "USD")

        service = BestDiscountResolverService([mock_discount1, mock_discount2])
        cart_item = CartItem("ITEM001", Money(100, "USD"), 1)

        service.calculate_discount(cart_item)

        mock_discount1.calculate.assert_called_once_with(cart_item)
        mock_discount2.calculate.assert_called_once_with(cart_item)

    def test_best_discount_capped_at_total_price(self):
        """Test that best discount is capped at cart item total price."""
        mock_discount1 = Mock(spec=Discount)
        mock_discount1.calculate.return_value = Money(200, "USD")

        mock_discount2 = Mock(spec=Discount)
        mock_discount2.calculate.return_value = Money(300, "USD")

        service = BestDiscountResolverService([mock_discount1, mock_discount2])
        cart_item = CartItem("ITEM001", Money(50, "USD"), 4)  # total: 200 USD

        result = service.calculate_discount(cart_item)

        # Best discount is 300, but should be capped at total price of 200
        assert result.amount == 200
        assert result.currency == "USD"
