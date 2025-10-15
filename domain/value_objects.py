class Money:
    """Immutable value object representing a monetary amount with currency."""

    def __init__(self, amount: int, currency: str):
        self.__amount = amount
        self.__currency = currency

    @property
    def amount(self) -> int:
        """Get the monetary amount."""
        return self.__amount

    @property
    def currency(self) -> str:
        """Get the currency code."""
        return self.__currency

    def __add__(self, other: "Money") -> "Money":
        """Add two Money objects. Only same currency allowed."""
        if not isinstance(other, Money):
            return NotImplemented
        if self.__currency != other.__currency:
            raise ValueError(
                f"Cannot add Money with different currencies: {self.__currency} and {other.__currency}"
            )
        return Money(self.__amount + other.__amount, self.__currency)

    def __radd__(self, other):
        """Support sum() function with Money objects."""
        # sum() starts with 0, so we need to handle that case
        if other == 0:
            return self
        return self.__add__(other)


class Percentage:
    """Immutable value object representing a percentage value between 0 and 100."""

    def __init__(self, percentage: int):
        if percentage < 0 or percentage > 100:
            raise ValueError(
                f"percentage has to be a float value between 0 and 100 - not {percentage}"
            )
        self.__percentage = percentage

    @property
    def percentage(self) -> int:
        """Get the percentage value."""
        return self.__percentage


class CartItem:
    """Immutable value object representing a shopping cart item."""

    def __init__(self, code: str, price: Money, quantity: int):
        self.__code = code
        self.__price = price
        self.__quantity = quantity

    @property
    def code(self) -> str:
        """Get the product code."""
        return self.__code

    @property
    def price(self) -> Money:
        """Get the unit price."""
        return self.__price

    @property
    def quantity(self) -> int:
        """Get the quantity."""
        return self.__quantity

    @property
    def total_price(self) -> Money:
        """Calculate the total price (quantity × unit price)."""
        return Money(self.__quantity * self.__price.amount, self.__price.currency)
