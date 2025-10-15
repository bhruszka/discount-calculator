from domain.entities.discount import Discount
from domain.services.discount_resolver_service import (
    DiscountResolverService,
    BestDiscountResolverService,
)
from domain.value_objects import CartItem, Money


class DiscountCalculatorService:
    """Service for calculating total discounts for cart items.

    Args:
        discounts: List of available discount rules.
        resolver_class: Strategy class for resolving best discount. Defaults to BestDiscountResolverService.
    """

    def __init__(
        self,
        discounts: list[Discount],
        resolver_class: type[DiscountResolverService] = BestDiscountResolverService,
    ):
        self.discount_resolver_service = resolver_class(discounts)

    def calculate_total_discount(self, cart_items: list[CartItem]) -> Money:
        """Calculate the total discount for all cart items.

        Args:
            cart_items: List of items in the shopping cart.

        Returns:
            Total discount amount across all items.
        """
        discounts = [
            self.discount_resolver_service.calculate_discount(c_i) for c_i in cart_items
        ]
        return sum(discounts)
