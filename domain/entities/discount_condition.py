from domain.value_objects import CartItem


class DiscountCondition:
    """Base class for discount eligibility conditions."""

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item meets the condition. Must be implemented by subclasses."""
        raise NotImplementedError()


class MinQuantityDiscountCondition(DiscountCondition):
    """Condition that checks if cart item meets minimum quantity requirement."""

    def __init__(self, min_quantity: int):
        super().__init__()
        self.min_quantity = min_quantity

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item quantity meets or exceeds minimum."""
        return cart_item.quantity >= self.min_quantity


class ProductCodeDiscountCondition(DiscountCondition):
    """Condition that checks if cart item product code is in allowed set."""

    def __init__(self, product_codes: set[str]):
        self.product_codes = product_codes
        super().__init__()

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if cart item product code is in the allowed set."""
        return cart_item.code in self.product_codes
