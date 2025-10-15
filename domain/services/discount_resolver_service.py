from domain.entities.discount import Discount
from domain.value_objects import CartItem, Money


class DiscountResolverService:
    """Base service for resolving and calculating discounts for cart items."""

    def __init__(self, discounts: list[Discount]):
        self.discounts = discounts

    def calculate_discount(self, cart_item: CartItem) -> Money:
        """Calculate discount for a cart item, capped at total price."""
        discount_value = self._calculate_discount(cart_item)
        if discount_value.amount > cart_item.total_price.amount:
            return cart_item.total_price

        return discount_value

    def _calculate_discount(self, cart_item: CartItem) -> Money:
        """Calculate the discount value for a cart item. Must be implemented by subclasses."""
        raise NotImplementedError()


class BestDiscountResolverService(DiscountResolverService):
    """Resolver that applies the best (highest value) discount from available discounts."""

    def _calculate_discount(self, cart_item: CartItem) -> Money:
        """Find and return the best discount value for a cart item."""
        best_discount_value = Money(0.0, cart_item.price.currency)
        for discount in self.discounts:
            discount_value = discount.calculate(cart_item)
            if discount_value and discount_value.amount > best_discount_value.amount:
                best_discount_value = discount_value
        return best_discount_value
