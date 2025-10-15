import pytest
from domain.value_objects import CartItem, Money, Percentage


@pytest.fixture
def usd_money():
    """Standard USD Money object."""
    return Money(100, "USD")


@pytest.fixture
def eur_money():
    """Standard EUR Money object."""
    return Money(100, "EUR")


@pytest.fixture
def small_usd_money():
    """Small USD Money object."""
    return Money(10, "USD")


@pytest.fixture
def percentage_10():
    """10% percentage."""
    return Percentage(10)


@pytest.fixture
def percentage_20():
    """20% percentage."""
    return Percentage(20)


@pytest.fixture
def percentage_50():
    """50% percentage."""
    return Percentage(50)


@pytest.fixture
def percentage_100():
    """100% percentage."""
    return Percentage(100)


@pytest.fixture
def cart_item_usd(usd_money):
    """Standard cart item with USD currency."""
    return CartItem("ITEM001", usd_money, 1)


@pytest.fixture
def cart_item_eur(eur_money):
    """Standard cart item with EUR currency."""
    return CartItem("ITEM001", eur_money, 1)


@pytest.fixture
def cart_item_multiple_quantity(usd_money):
    """Cart item with quantity of 3."""
    return CartItem("ITEM001", usd_money, 3)


@pytest.fixture
def cart_item_high_quantity():
    """Cart item with high quantity."""
    return CartItem("ITEM001", Money(50, "USD"), 5)
