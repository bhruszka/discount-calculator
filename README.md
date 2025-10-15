# Discount Calculator System

A flexible, domain-driven discount calculation system for e-commerce shopping carts. Supports multiple discount types with conditional eligibility rules and automatic selection of the best discount per cart item.

## Quick Start

Try the interactive demo to see the system in action:

```bash
python3 demo.py
```

The demo showcases:
- Basic discount types (fixed, percentage, volume)
- Product-specific discounts
- Combined conditions (e.g., volume + product-specific)
- Automatic best discount selection

## Features

- **Fixed Amount Discounts** - Apply a fixed monetary discount (e.g., -100 EUR)
- **Percentage Discounts** - Apply percentage-based discounts (e.g., -10%)
- **Volume Discounts** - Minimum quantity requirements for discount eligibility
- **Product-Specific Discounts** - Target specific product codes
- **Best Discount Selection** - Automatically applies the highest value discount per item
- **Currency Safety** - Type-safe money operations with currency validation
- **Extensible Architecture** - Strategy pattern for custom discount resolution

## Installation

**Requirements:** Python 3.13+

The core discount calculation system has **no external dependencies** - you can use it directly with just Python 3.13+.

### For Development

If you want to run tests or contribute to the project:

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. (Optional) Install pre-commit hooks:
```bash
pre-commit install
```

## Usage

### Supported Discount Types

| Type | Rule | Example |
|------|------|---------|
| **Fixed discount** | -X \<currency\> | -100 EUR |
| **Percentage discount** | -X% | -10% |
| **Volume discount** | -X \<currency\> if at least N products are bought together | -100 EUR if at least 10 products are bought |
| **Product-specific discount** | Apply discount only to specific product codes | -20% only for products PREMIUM001, PREMIUM002 |

> **Tip:** Run `python3 demo.py` to see all discount types in action with detailed examples!

### Setting Up Discount Rules

```python
from domain.entities.discount import AmountDiscount, PercentageDiscount
from domain.entities.discount_condition import (
    MinQuantityDiscountCondition,
    ProductCodeDiscountCondition,
)
from domain.value_objects import Money, Percentage

# 1. Fixed discount: -100 EUR
fixed_discount = AmountDiscount(Money(100, "EUR"), conditions=None)

# 2. Percentage discount: -10%
percentage_discount = PercentageDiscount(Percentage(10), conditions=None)

# 3. Volume discount: -100 EUR if at least 10 products are bought
volume_condition = MinQuantityDiscountCondition(min_quantity=10)
volume_discount = AmountDiscount(Money(100, "EUR"), conditions=[volume_condition])

# 4. Product-specific discount: -20% only for PREMIUM001, PREMIUM002
product_condition = ProductCodeDiscountCondition({"PREMIUM001", "PREMIUM002"})
product_discount = PercentageDiscount(Percentage(20), conditions=[product_condition])
```

### Applying Discounts to Cart Items

```python
from domain.services.calculator_service import DiscountCalculatorService
from domain.value_objects import CartItem

# Create calculator with all discount rules
discounts = [fixed_discount, percentage_discount, volume_discount]
calculator = DiscountCalculatorService(discounts)

# Define cart items
cart_items = [
    CartItem("ITEM001", Money(500, "EUR"), 1),   # Single item
    CartItem("ITEM002", Money(200, "EUR"), 5),   # 5 items
    CartItem("ITEM003", Money(100, "EUR"), 15),  # 15 items (volume eligible)
]

# Calculate total discount (best discount per item is automatically selected)
total_discount = calculator.calculate_total_discount(cart_items)

# Results:
# ITEM001: 100 EUR (fixed) > 50 EUR (10% of 500) → 100 EUR discount
# ITEM002: 100 EUR (fixed) > 20 EUR (10% of 200) → 100 EUR discount
# ITEM003: 100 EUR (volume/fixed) > 10 EUR (10% of 100) → 100 EUR discount
# Total: 300 EUR
```

### Advanced: Combining Multiple Conditions

You can combine multiple conditions - all must be met for the discount to apply:

```python
# Example: Volume discount only for bulk products (both conditions required)
bulk_condition = ProductCodeDiscountCondition({"BULK001"})
quantity_condition = MinQuantityDiscountCondition(min_quantity=5)
bulk_volume_discount = AmountDiscount(
    Money(200, "EUR"),
    conditions=[bulk_condition, quantity_condition]
)
# This discount applies only if: product is BULK001 AND quantity >= 5
```

## Architecture

The system follows Domain-Driven Design principles with clear separation of concerns.

### Calculator Service

**[DiscountCalculatorService](domain/services/calculator_service.py)** - Main entry point for discount calculations.

```python
class DiscountCalculatorService:
    def __init__(
        self,
        discounts: list[Discount],
        resolver_class: type[DiscountResolverService] = BestDiscountResolverService,
    ):
        """
        Args:
            discounts: List of available discount rules.
            resolver_class: Strategy class for resolving best discount.
        """
```

**Usage:**
- Pass list of discounts to constructor
- Call `calculate_total_discount(cart_items)` to get total discount
- Optionally provide custom resolver strategy via `resolver_class` parameter

### Resolver Interface

**[DiscountResolverService](domain/services/discount_resolver_service.py)** - Strategy pattern for discount resolution.

**Base Class:**
```python
class DiscountResolverService:
    def calculate_discount(self, cart_item: CartItem) -> Money:
        """Calculate discount for a cart item, capped at total price."""

    def _calculate_discount(self, cart_item: CartItem) -> Money:
        """Must be implemented by subclasses."""
```

**Default Implementation:**
- **BestDiscountResolverService** - Selects the discount with the highest value
- Automatically caps discount at item's total price
- Returns zero discount if no eligible discounts found

**Custom Resolver:**
You can implement custom resolution strategies (e.g., first-match, random, weighted) by subclassing `DiscountResolverService` and implementing `_calculate_discount()`.

### Discount Interface

**[Discount](domain/entities/discount.py)** - Base class for all discount types.

**Base Class:**
```python
class Discount:
    def __init__(self, conditions: list[DiscountCondition] | None):
        """Conditions that must be met for discount eligibility."""

    def is_eligible(self, cart_item: CartItem) -> bool:
        """Check if all conditions are met."""

    def calculate(self, cart_item: CartItem) -> Money | None:
        """Calculate discount amount if eligible and currency matches."""

    def _calculate(self, cart_item: CartItem) -> Money:
        """Must be implemented by subclasses."""
```

**Built-in Implementations:**

1. **AmountDiscount** - Fixed monetary discount
   ```python
   AmountDiscount(Money(100, "EUR"), conditions=[...])
   ```

2. **PercentageDiscount** - Percentage-based discount
   ```python
   PercentageDiscount(Percentage(10), conditions=[...])
   ```

**Custom Discounts:**
Create new discount types by subclassing `Discount` and implementing `_calculate()`:
```python
class BuyOneGetOneFreeDiscount(Discount):
    def _calculate(self, cart_item: CartItem) -> Money:
        free_items = cart_item.quantity // 2
        return Money(free_items * cart_item.price.amount, cart_item.price.currency)
```

### Discount Condition Interface

**[DiscountCondition](domain/entities/discount_condition.py)** - Rules for discount eligibility.

**Base Class:**
```python
class DiscountCondition:
    def is_eligible(self, cart_item: CartItem) -> bool:
        """Must be implemented by subclasses."""
```

**Built-in Conditions:**

1. **MinQuantityDiscountCondition** - Minimum quantity requirement
   ```python
   MinQuantityDiscountCondition(min_quantity=3)
   ```

2. **ProductCodeDiscountCondition** - Product code whitelist
   ```python
   ProductCodeDiscountCondition({"PROD001", "PROD002"})
   ```

**Multiple Conditions:**
Discounts support multiple conditions - all must be met (AND logic):
```python
conditions = [
    MinQuantityDiscountCondition(5),
    ProductCodeDiscountCondition({"BULK001"}),
]
discount = AmountDiscount(Money(200, "EUR"), conditions=conditions)
```

**Custom Conditions:**
Create new conditions by subclassing `DiscountCondition`:
```python
class PriceRangeCondition(DiscountCondition):
    def __init__(self, min_price: Money, max_price: Money):
        self.min_price = min_price
        self.max_price = max_price

    def is_eligible(self, cart_item: CartItem) -> bool:
        return self.min_price.amount <= cart_item.price.amount <= self.max_price.amount
```

### Value Objects

**[Money](domain/value_objects.py)** - Immutable monetary amount with currency.
```python
money = Money(100, "EUR")
total = sum([money1, money2, money3])  # Supports sum()
combined = money1 + money2  # Supports addition (same currency only)
```

**[Percentage](domain/value_objects.py)** - Immutable percentage (0-100).
```python
discount_rate = Percentage(10)  # Validates range 0-100
```

**[CartItem](domain/value_objects.py)** - Immutable cart line item.
```python
item = CartItem("PROD001", Money(100, "EUR"), quantity=3)
item.total_price  # Money(300, "EUR") - calculated property
```

## Code Quality

The project uses automated code quality tools to maintain high standards.

### Ruff

Fast Python linter and formatter configured for automatic code quality enforcement.

**Run manually:**
```bash
ruff check .          # Lint
ruff check --fix .    # Lint with auto-fix
ruff format .         # Format code
```

### Pre-commit Hooks

Automatically runs on every commit to ensure code quality:
- **Ruff linting** - Auto-fixes common issues
- **Ruff formatting** - Ensures consistent code style
- **Pytest** - Runs all tests with 100% coverage requirement

**Setup:**
```bash
pre-commit install
```

**Run manually:**
```bash
pre-commit run --all-files
```

## Testing

Comprehensive test suite with 100% code coverage requirement.

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=domain --cov-report=term-missing

# Run specific test file
pytest tests/test_integration.py -v
```

### Test Coverage

The project maintains **100% code coverage** on the `domain` package, enforced by pre-commit hooks.

**Coverage Report:**
```
Name                                           Stmts   Miss  Cover
------------------------------------------------------------------
domain/entities/discount.py                       30      0   100%
domain/entities/discount_condition.py             16      0   100%
domain/services/calculator_service.py              9      0   100%
domain/services/discount_resolver_service.py      20      0   100%
domain/value_objects.py                           45      0   100%
------------------------------------------------------------------
TOTAL                                            120      0   100%
```

**Test Suite:** 72 tests across unit and integration test suites

### Test Structure

```
tests/
├── conftest.py                          # Shared pytest fixtures
├── test_integration.py                  # End-to-end integration tests (10 tests)
├── test_value_objects.py                # Value object unit tests (12 tests)
├── entities/
│   ├── test_discount.py                 # Discount entity tests (19 tests)
│   └── test_discount_condition.py       # Condition tests (9 tests)
└── services/
    ├── test_discount_calculator_service.py  # Calculator tests (9 tests)
    └── test_discount_resolver_service.py    # Resolver tests (13 tests)
```

### Test Approach

The test suite includes both **unit tests** and **integration tests**:

- **Unit Tests** (62 tests) - Test individual components in isolation, ensuring each class and method works correctly on its own. These tests focus on value objects, entities, and services independently.

- **Integration Tests** (10 tests) - Test the complete discount calculation workflow end-to-end with real objects. These verify that all components work together correctly for real-world scenarios like applying multiple discounts, volume discounts, and product-specific rules.
