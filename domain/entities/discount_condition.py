from domain.value_objects import CartItem


class DiscountCondition:
    """Base class for discount eligibility conditions."""

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item meets the condition.

        Args:
            cart_item: Cart item to check.

        Returns:
            True if condition is met.

        Raises:
            NotImplementedError: Must be implemented by subclasses.
        """
        raise NotImplementedError()


class MinQuantityDiscountCondition(DiscountCondition):
    """Condition that checks if cart item meets minimum quantity requirement.

    Args:
        min_quantity: Minimum required quantity.
    """

    def __init__(self, min_quantity: int):
        super().__init__()
        self.min_quantity = min_quantity

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item quantity meets or exceeds minimum.

        Args:
            cart_item: Cart item to check.

        Returns:
            True if quantity >= min_quantity.
        """
        return cart_item.quantity >= self.min_quantity


class ProductCodeDiscountCondition(DiscountCondition):
    """Condition that checks if cart item product code is in allowed set.

    Args:
        product_codes: Set of eligible product codes.
    """

    def __init__(self, product_codes: set[str]):
        self.product_codes = product_codes
        super().__init__()

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item product code is in the allowed set.

        Args:
            cart_item: Cart item to check.

        Returns:
            True if product code is in allowed set.
        """
        return cart_item.code in self.product_codes
