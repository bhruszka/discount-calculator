from domain.services.discount_resolver_service import DiscountResolverService
from domain.value_objects import CartItem, Money


class DiscountCalculatorService:
    """Service for calculating total discounts for cart items."""

    def __init__(self, discount_resolver_service: DiscountResolverService):
        self.discount_resolver_service = discount_resolver_service

    def calculate_total_discount(self, cart_items: list[CartItem]) -> Money:
        """Calculate the total discount for all cart items."""
        discounts = [
            self.discount_resolver_service.calculate_discount(c_i) for c_i in cart_items
        ]
        return sum(discounts)
