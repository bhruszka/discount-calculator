"""
Discount Calculator System - Demo

This demo showcases the main features of the discount calculation system:
1. Fixed amount discounts
2. Percentage discounts
3. Volume discounts (minimum quantity)
4. Product-specific discounts
5. Best discount selection
"""

from domain.entities.discount import AmountDiscount, PercentageDiscount
from domain.entities.discount_condition import (
    MinQuantityDiscountCondition,
    ProductCodeDiscountCondition,
)
from domain.services.calculator_service import DiscountCalculatorService
from domain.value_objects import CartItem, Money, Percentage


def print_separator():
    print("\n" + "=" * 70 + "\n")


def demo_basic_discounts():
    """Demo 1: Basic discount types (fixed, percentage, volume)"""
    print("DEMO 1: Basic Discount Types")
    print("-" * 70)

    # Setup discount rules
    fixed_discount = AmountDiscount(Money(100, "EUR"), conditions=None)
    percentage_discount = PercentageDiscount(Percentage(10), conditions=None)
    volume_condition = MinQuantityDiscountCondition(min_quantity=10)
    volume_discount = AmountDiscount(Money(100, "EUR"), conditions=[volume_condition])

    discounts = [fixed_discount, percentage_discount, volume_discount]
    calculator = DiscountCalculatorService(discounts)

    # Cart items
    cart_items = [
        CartItem("ITEM001", Money(500, "EUR"), 1),  # Single item
        CartItem("ITEM002", Money(200, "EUR"), 5),  # 5 items
        CartItem("ITEM003", Money(100, "EUR"), 15),  # 15 items (volume eligible)
    ]

    print("\nCart Items:")
    for item in cart_items:
        print(f"  - {item.code}: {item.quantity}x {item.price.amount} EUR")

    print("\nAvailable Discounts:")
    print("  1. Fixed: -100 EUR")
    print("  2. Percentage: -10%")
    print("  3. Volume: -100 EUR if quantity >= 10")

    total_discount = calculator.calculate_total_discount(cart_items)

    print("\nDiscount Breakdown:")
    print("  ITEM001: 100 EUR (fixed) > 50 EUR (10%) → 100 EUR discount")
    print("  ITEM002: 100 EUR (fixed) > 20 EUR (10%) → 100 EUR discount")
    print("  ITEM003: 100 EUR (volume/fixed) > 10 EUR (10%) → 100 EUR discount")
    print(f"\n✓ Total Discount: {total_discount.amount} {total_discount.currency}")


def demo_product_specific():
    """Demo 2: Product-specific discounts"""
    print("DEMO 2: Product-Specific Discounts")
    print("-" * 70)

    # Setup: 20% discount only for premium products
    premium_condition = ProductCodeDiscountCondition({"PREMIUM001", "PREMIUM002"})
    premium_discount = PercentageDiscount(
        Percentage(20), conditions=[premium_condition]
    )

    # Regular 10% discount for all products
    regular_discount = PercentageDiscount(Percentage(10), conditions=None)

    calculator = DiscountCalculatorService([premium_discount, regular_discount])

    cart_items = [
        CartItem("PREMIUM001", Money(100, "EUR"), 1),  # Premium product
        CartItem("PREMIUM002", Money(200, "EUR"), 1),  # Premium product
        CartItem("REGULAR001", Money(100, "EUR"), 1),  # Regular product
    ]

    print("\nCart Items:")
    for item in cart_items:
        product_type = "Premium" if "PREMIUM" in item.code else "Regular"
        print(f"  - {item.code} ({product_type}): {item.price.amount} EUR")

    print("\nAvailable Discounts:")
    print("  1. Premium: -20% for PREMIUM001, PREMIUM002")
    print("  2. Regular: -10% for all products")

    total_discount = calculator.calculate_total_discount(cart_items)

    print("\nDiscount Breakdown:")
    print("  PREMIUM001: 20 EUR (20%) > 10 EUR (10%) → 20 EUR discount")
    print("  PREMIUM002: 40 EUR (20%) > 20 EUR (10%) → 40 EUR discount")
    print("  REGULAR001: 10 EUR (10% only) → 10 EUR discount")
    print(f"\n✓ Total Discount: {total_discount.amount} {total_discount.currency}")


def demo_combined_conditions():
    """Demo 3: Combining multiple conditions"""
    print("DEMO 3: Combined Conditions (Volume + Product-Specific)")
    print("-" * 70)

    # Setup: 200 EUR discount for BULK001 product only if buying 5+ items
    bulk_condition = ProductCodeDiscountCondition({"BULK001"})
    quantity_condition = MinQuantityDiscountCondition(min_quantity=5)
    bulk_volume_discount = AmountDiscount(
        Money(200, "EUR"), conditions=[bulk_condition, quantity_condition]
    )

    # Fallback: 10% discount for all
    fallback_discount = PercentageDiscount(Percentage(10), conditions=None)

    calculator = DiscountCalculatorService([bulk_volume_discount, fallback_discount])

    cart_items = [
        CartItem("BULK001", Money(100, "EUR"), 10),  # Meets both conditions
        CartItem("BULK001", Money(100, "EUR"), 3),  # Wrong quantity
        CartItem("OTHER001", Money(100, "EUR"), 10),  # Wrong product
    ]

    print("\nCart Items:")
    for item in cart_items:
        print(f"  - {item.code}: {item.quantity}x {item.price.amount} EUR")

    print("\nAvailable Discounts:")
    print("  1. Bulk Volume: -200 EUR for BULK001 if quantity >= 5")
    print("  2. Fallback: -10% for all products")

    total_discount = calculator.calculate_total_discount(cart_items)

    print("\nDiscount Breakdown:")
    print("  BULK001 (10 items): 200 EUR (bulk) > 10 EUR (10%) → 200 EUR discount")
    print("  BULK001 (3 items): Not eligible for bulk → 10 EUR discount (10%)")
    print("  OTHER001 (10 items): Not eligible for bulk → 10 EUR discount (10%)")
    print(f"\n✓ Total Discount: {total_discount.amount} {total_discount.currency}")


def demo_best_discount_selection():
    """Demo 4: Automatic best discount selection"""
    print("DEMO 4: Best Discount Selection")
    print("-" * 70)

    # Setup multiple competing discounts
    discounts = [
        AmountDiscount(Money(50, "EUR"), conditions=None),
        PercentageDiscount(Percentage(20), conditions=None),
        PercentageDiscount(Percentage(30), conditions=None),
    ]
    calculator = DiscountCalculatorService(discounts)

    cart_items = [
        CartItem("ITEM001", Money(100, "EUR"), 1),  # Price: 100 EUR
        CartItem("ITEM002", Money(300, "EUR"), 1),  # Price: 300 EUR
        CartItem("ITEM003", Money(1000, "EUR"), 1),  # Price: 1000 EUR
    ]

    print("\nCart Items:")
    for item in cart_items:
        print(f"  - {item.code}: {item.price.amount} EUR")

    print("\nAvailable Discounts:")
    print("  1. Fixed: -50 EUR")
    print("  2. Percentage: -20%")
    print("  3. Percentage: -30%")

    total_discount = calculator.calculate_total_discount(cart_items)

    print("\nDiscount Breakdown (best automatically selected):")
    print("  ITEM001: 50 EUR (fixed) > 30 EUR (30%) > 20 EUR (20%) → 50 EUR")
    print("  ITEM002: 90 EUR (30%) > 60 EUR (20%) > 50 EUR (fixed) → 90 EUR")
    print("  ITEM003: 300 EUR (30%) > 200 EUR (20%) > 50 EUR (fixed) → 300 EUR")
    print(f"\n✓ Total Discount: {total_discount.amount} {total_discount.currency}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print(" " * 15 + "DISCOUNT CALCULATOR SYSTEM - DEMO")
    print("=" * 70)

    demo_basic_discounts()
    print_separator()

    demo_product_specific()
    print_separator()

    demo_combined_conditions()
    print_separator()

    demo_best_discount_selection()
    print_separator()

    print("All demos completed successfully! ✓")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
