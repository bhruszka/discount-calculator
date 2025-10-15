from domain.entities.discount_condition import DiscountCondition
from domain.value_objects import CartItem, Money, Percentage


class Discount:
    """Base class for cart item discounts with conditional eligibility.

    Args:
        conditions: Optional list of conditions that must be met for discount eligibility.
    """

    def __init__(self, conditions: list[DiscountCondition] | None):
        self.conditions = conditions or []

    def is_eligible(self, cart_item: CartItem):
        """Check if cart item meets all discount conditions.

        Args:
            cart_item: Cart item to check eligibility for.

        Returns:
            True if all conditions are met.
        """
        return all([c.is_eligible(cart_item) for c in self.conditions])

    def calculate(self, cart_item: CartItem) -> Money | None:
        """Calculate discount amount if eligible and currency matches.

        Args:
            cart_item: Cart item to calculate discount for.

        Returns:
            Discount amount or None if ineligible or currency mismatch.
        """
        if not self.is_eligible(cart_item):
            return None

        amount = self._calculate(cart_item)
        if amount.currency != cart_item.price.currency:
            return None

        return amount

    def _calculate(self, cart_item: CartItem) -> Money:
        """Calculate the discount amount.

        Args:
            cart_item: Cart item to calculate discount for.

        Returns:
            Raw discount amount.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()


class AmountDiscount(Discount):
    """Fixed amount discount.

    Args:
        amount: Fixed discount amount.
        conditions: Optional list of eligibility conditions.
    """

    def __init__(self, amount: Money, conditions: list[DiscountCondition] | None):
        self.amount = amount
        super().__init__(conditions)

    def _calculate(self, cart_item: CartItem) -> Money:
        """Return the fixed discount amount.

        Args:
            cart_item: Cart item (unused for fixed discount).

        Returns:
            Fixed discount amount.
        """
        return self.amount


class PercentageDiscount(Discount):
    """Percentage-based discount.

    Args:
        percentage: Discount percentage to apply.
        conditions: Optional list of eligibility conditions.
    """

    def __init__(
        self, percentage: Percentage, conditions: list[DiscountCondition] | None
    ):
        self.percentage = percentage
        super().__init__(conditions)

    def _calculate(self, cart_item: CartItem) -> Money:
        """Calculate discount as percentage of item price.

        Args:
            cart_item: Cart item to calculate discount for.

        Returns:
            Discount amount based on percentage of unit price.
        """
        price = cart_item.price
        amount = price.amount * self.percentage.percentage // 100
        return Money(amount, price.currency)
