from domain.entities.discount_condition import DiscountCondition
from domain.value_objects import CartItem, Money, Percentage


class Discount:
    """Base class for cart item discounts with conditional eligibility."""

    def __init__(self, conditions: list[DiscountCondition] | None):
        self.conditions = conditions or []

    def is_eligible(self, cart_item: CartItem):
        """Check if cart item meets all discount conditions."""
        return all([c.is_eligible(cart_item) for c in self.conditions])

    def calculate(self, cart_item: CartItem) -> Money | None:
        """Calculate discount amount if eligible and currency matches."""
        if not self.is_eligible(cart_item):
            return None

        amount = self._calculate(cart_item)
        if amount.currency != cart_item.price.currency:
            return None

        return amount

    def _calculate(self, cart_item: CartItem) -> Money:
        """Calculate the discount amount. Must be implemented by subclasses."""
        raise NotImplementedError()


class AmountDiscount(Discount):
    """Fixed amount discount."""

    def __init__(self, amount: Money, conditions: list[DiscountCondition] | None):
        self.amount = amount
        super().__init__(conditions)

    def _calculate(self, cart_item: CartItem) -> Money:
        """Return the fixed discount amount."""
        return self.amount


class PercentageDiscount(Discount):
    """Percentage-based discount."""

    def __init__(
        self, percentage: Percentage, conditions: list[DiscountCondition] | None
    ):
        self.percentage = percentage
        super().__init__(conditions)

    def _calculate(self, cart_item: CartItem) -> Money:
        """Calculate discount as percentage of item price."""
        price = cart_item.price
        amount = price.amount * self.percentage.percentage // 100
        return Money(amount, price.currency)
