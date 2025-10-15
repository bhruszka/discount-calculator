import pytest
from unittest.mock import Mock
from domain.entities.discount import Discount, AmountDiscount, PercentageDiscount
from domain.entities.discount_condition import DiscountCondition
from domain.value_objects import CartItem, Money, Percentage


class TestDiscount:
    """Test base Discount class."""

    def test_calculate_not_implemented(self, cart_item_usd):
        """Test that base class _calculate raises NotImplementedError."""
        discount = Discount(conditions=None)
        with pytest.raises(NotImplementedError):
            discount._calculate(cart_item_usd)

    def test_is_eligible_with_no_conditions(self, cart_item_usd):
        """Test eligibility with no conditions returns True."""
        discount = Discount(conditions=None)
        assert discount.is_eligible(cart_item_usd) is True

    def test_is_eligible_with_empty_conditions_list(self, cart_item_usd):
        """Test eligibility with empty conditions list returns True."""
        discount = Discount(conditions=[])
        assert discount.is_eligible(cart_item_usd) is True

    def test_is_eligible_with_all_conditions_met(self, cart_item_usd):
        """Test eligibility when all conditions are met."""
        mock_condition1 = Mock(spec=DiscountCondition)
        mock_condition1.is_eligible.return_value = True
        mock_condition2 = Mock(spec=DiscountCondition)
        mock_condition2.is_eligible.return_value = True

        discount = Discount(conditions=[mock_condition1, mock_condition2])

        assert discount.is_eligible(cart_item_usd) is True
        mock_condition1.is_eligible.assert_called_once_with(cart_item_usd)
        mock_condition2.is_eligible.assert_called_once_with(cart_item_usd)

    def test_not_eligible_when_one_condition_fails(self, cart_item_usd):
        """Test not eligible when one condition fails."""
        mock_condition1 = Mock(spec=DiscountCondition)
        mock_condition1.is_eligible.return_value = True
        mock_condition2 = Mock(spec=DiscountCondition)
        mock_condition2.is_eligible.return_value = False

        discount = Discount(conditions=[mock_condition1, mock_condition2])

        assert discount.is_eligible(cart_item_usd) is False

    def test_calculate_returns_none_when_not_eligible(
        self, cart_item_usd, small_usd_money
    ):
        """Test calculate returns None when cart item is not eligible."""
        mock_condition = Mock(spec=DiscountCondition)
        mock_condition.is_eligible.return_value = False

        discount = AmountDiscount(small_usd_money, conditions=[mock_condition])

        result = discount.calculate(cart_item_usd)
        assert result is None

    def test_calculate_returns_none_when_currency_mismatch(
        self, cart_item_usd, eur_money
    ):
        """Test calculate returns None when currencies don't match."""
        discount = AmountDiscount(Money(10, "EUR"), conditions=None)

        result = discount.calculate(cart_item_usd)
        assert result is None


class TestAmountDiscount:
    """Test AmountDiscount class."""

    def test_create_amount_discount(self, small_usd_money):
        """Test creating an AmountDiscount."""
        discount = AmountDiscount(small_usd_money, conditions=None)
        assert discount.amount.amount == 10
        assert discount.amount.currency == "USD"

    def test_calculate_returns_fixed_amount(self, cart_item_usd, small_usd_money):
        """Test that calculate returns fixed amount."""
        discount = AmountDiscount(small_usd_money, conditions=None)

        result = discount.calculate(cart_item_usd)
        assert result.amount == 10
        assert result.currency == "USD"

    def test_calculate_with_conditions_met(self, cart_item_usd):
        """Test calculate when conditions are met."""
        mock_condition = Mock(spec=DiscountCondition)
        mock_condition.is_eligible.return_value = True

        amount = Money(15, "USD")
        discount = AmountDiscount(amount, conditions=[mock_condition])

        result = discount.calculate(cart_item_usd)
        assert result.amount == 15
        assert result.currency == "USD"

    def test_calculate_with_conditions_not_met(self, cart_item_usd):
        """Test calculate returns None when conditions not met."""
        mock_condition = Mock(spec=DiscountCondition)
        mock_condition.is_eligible.return_value = False

        amount = Money(15, "USD")
        discount = AmountDiscount(amount, conditions=[mock_condition])

        result = discount.calculate(cart_item_usd)
        assert result is None


class TestPercentageDiscount:
    """Test PercentageDiscount class."""

    def test_create_percentage_discount(self, percentage_10):
        """Test creating a PercentageDiscount."""
        discount = PercentageDiscount(percentage_10, conditions=None)
        assert discount.percentage.percentage == 10

    def test_calculate_percentage_discount(self, cart_item_usd, percentage_10):
        """Test calculating percentage discount."""
        discount = PercentageDiscount(percentage_10, conditions=None)

        result = discount.calculate(cart_item_usd)
        assert result.amount == 10
        assert result.currency == "USD"

    def test_calculate_percentage_discount_rounds_down(self):
        """Test that percentage calculation rounds down."""
        percentage = Percentage(15)
        discount = PercentageDiscount(percentage, conditions=None)
        cart_item = CartItem("ITEM001", Money(99, "USD"), 1)

        result = discount.calculate(cart_item)
        assert result.amount == 14  # 99 * 15 / 100 = 14.85, rounds down to 14

    def test_calculate_50_percent_discount(self, percentage_50):
        """Test 50% discount calculation."""
        discount = PercentageDiscount(percentage_50, conditions=None)
        cart_item = CartItem("ITEM001", Money(200, "USD"), 1)

        result = discount.calculate(cart_item)
        assert result.amount == 100
        assert result.currency == "USD"

    def test_calculate_100_percent_discount(self, percentage_100):
        """Test 100% discount calculation."""
        discount = PercentageDiscount(percentage_100, conditions=None)
        cart_item = CartItem("ITEM001", Money(150, "USD"), 1)

        result = discount.calculate(cart_item)
        assert result.amount == 150
        assert result.currency == "USD"

    def test_calculate_zero_percent_discount(self, cart_item_usd):
        """Test 0% discount calculation."""
        percentage = Percentage(0)
        discount = PercentageDiscount(percentage, conditions=None)

        result = discount.calculate(cart_item_usd)
        assert result.amount == 0
        assert result.currency == "USD"

    def test_calculate_with_conditions_met(self, cart_item_usd, percentage_20):
        """Test calculate when conditions are met."""
        mock_condition = Mock(spec=DiscountCondition)
        mock_condition.is_eligible.return_value = True

        discount = PercentageDiscount(percentage_20, conditions=[mock_condition])

        result = discount.calculate(cart_item_usd)
        assert result.amount == 20
        assert result.currency == "USD"

    def test_calculate_preserves_currency(self):
        """Test that percentage discount preserves currency."""
        percentage = Percentage(25)
        discount = PercentageDiscount(percentage, conditions=None)
        cart_item = CartItem("ITEM001", Money(80, "EUR"), 1)

        result = discount.calculate(cart_item)
        assert result.amount == 20
        assert result.currency == "EUR"
