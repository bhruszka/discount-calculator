import pytest
from domain.value_objects import Money, Percentage


class TestMoney:
    """Test Money value object."""

    def test_immutability(self, usd_money):
        """Test that Money is immutable."""
        with pytest.raises(AttributeError):
            usd_money.amount = 200

    def test_add_same_currency(self, usd_money, small_usd_money):
        """Test adding Money objects with same currency."""
        result = usd_money + small_usd_money
        assert result.amount == 110
        assert result.currency == "USD"

    def test_add_different_currency_raises_error(self, usd_money, eur_money):
        """Test that adding different currencies raises ValueError."""
        with pytest.raises(
            ValueError, match="Cannot add Money with different currencies"
        ):
            usd_money + eur_money

    def test_add_non_money_returns_not_implemented(self, usd_money):
        """Test that adding non-Money object returns NotImplemented."""
        result = usd_money.__add__("invalid")
        assert result is NotImplemented

    def test_radd_with_money_object(self, usd_money, small_usd_money):
        """Test __radd__ with Money object (reverse addition)."""
        result = usd_money.__radd__(small_usd_money)
        assert result.amount == 110
        assert result.currency == "USD"

    def test_sum_with_list_of_money(self, usd_money, small_usd_money):
        """Test using sum() with list of Money objects."""
        total = sum([usd_money, small_usd_money, Money(50, "USD")])
        assert total.amount == 160
        assert total.currency == "USD"


class TestPercentage:
    """Test Percentage value object."""

    def test_immutability(self, percentage_50):
        """Test that Percentage is immutable."""
        with pytest.raises(AttributeError):
            percentage_50.percentage = 75

    def test_percentage_below_zero_raises_error(self):
        """Test that percentage below 0 raises ValueError."""
        with pytest.raises(
            ValueError, match="percentage has to be a float value between 0 and 100"
        ):
            Percentage(-1)

    def test_percentage_above_hundred_raises_error(self):
        """Test that percentage above 100 raises ValueError."""
        with pytest.raises(
            ValueError, match="percentage has to be a float value between 0 and 100"
        ):
            Percentage(101)


class TestCartItem:
    """Test CartItem value object."""

    def test_immutability(self, cart_item_multiple_quantity):
        """Test that CartItem is immutable."""
        with pytest.raises(AttributeError):
            cart_item_multiple_quantity.code = "ITEM002"
        with pytest.raises(AttributeError):
            cart_item_multiple_quantity.quantity = 5

    def test_total_price_calculation(self, cart_item_multiple_quantity):
        """Test total_price calculation."""
        total = cart_item_multiple_quantity.total_price
        assert total.amount == 300
        assert total.currency == "USD"

    def test_total_price_preserves_currency(self, cart_item_eur):
        """Test that total_price preserves currency."""
        total = cart_item_eur.total_price
        assert total.amount == 100
        assert total.currency == "EUR"
