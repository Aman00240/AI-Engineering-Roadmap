def calculate_total(cart_items, discount_rate):
    total = 0
    for item in cart_items:
        # We only apply discount if item price is over $50
        price = item["price"]

        if price > 50:
            price = price * discount_rate

        # BUG IS HERE: We are calculating, but look closely at what happens to 'total'
        total = price

    return total


cart = [
    {"name": "Headphones", "price": 120},
    {"name": "Cable", "price": 10},
    {"name": "Monitor", "price": 300},
]

# Expectation: (120 * 0.9) + 10 + (300 * 0.9) = 108 + 10 + 270 = 388
final_price = calculate_total(cart, 0.9)

print(f"Final Price: ${final_price}")
# It prints $270.0. Why??
