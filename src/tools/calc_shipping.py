SHIPPING_RATES = {
    "hanoi": {"rate_per_kg": 2.5, "base_fee": 5.0, "city": "Hanoi"},
    "hà nội": {"rate_per_kg": 2.5, "base_fee": 5.0, "city": "Hanoi"},
    "ha noi": {"rate_per_kg": 2.5, "base_fee": 5.0, "city": "Hanoi"},
    "hcmc": {"rate_per_kg": 2.0, "base_fee": 4.0, "city": "Ho Chi Minh City"},
    "ho chi minh": {"rate_per_kg": 2.0, "base_fee": 4.0, "city": "Ho Chi Minh City"},
    "saigon": {"rate_per_kg": 2.0, "base_fee": 4.0, "city": "Ho Chi Minh City"},
    "danang": {"rate_per_kg": 3.0, "base_fee": 6.0, "city": "Da Nang"},
    "da nang": {"rate_per_kg": 3.0, "base_fee": 6.0, "city": "Da Nang"},
    "singapore": {"rate_per_kg": 8.0, "base_fee": 15.0, "city": "Singapore"},
    "bangkok": {"rate_per_kg": 6.0, "base_fee": 12.0, "city": "Bangkok"},
    "tokyo": {"rate_per_kg": 10.0, "base_fee": 20.0, "city": "Tokyo"},
    "new york": {"rate_per_kg": 15.0, "base_fee": 30.0, "city": "New York"},
}


def calc_shipping(args: str) -> str:
    """
    Calculate shipping cost based on total weight and destination city.
    Args: "weight_kg, destination" (e.g., "0.8, Hanoi" or "1.5, Singapore")
    Returns: shipping cost in USD.
    Example Action: calc_shipping(0.8, Hanoi)
    """
    parts = args.split(",", 1)
    if len(parts) != 2:
        return (
            "Error: provide both weight and destination. "
            "Format: calc_shipping(weight_kg, destination). "
            "Example: calc_shipping(0.8, Hanoi)"
        )

    try:
        weight_kg = float(parts[0].strip().strip('"').strip("'"))
    except ValueError:
        return f"Error: '{parts[0].strip()}' is not a valid weight number."

    destination = parts[1].strip().strip('"').strip("'").lower()
    rate_info = SHIPPING_RATES.get(destination)

    if rate_info is None:
        available = ", ".join({v["city"] for v in SHIPPING_RATES.values()})
        return (
            f"Destination '{destination}' not supported. "
            f"Available cities: {available}"
        )

    cost = rate_info["base_fee"] + rate_info["rate_per_kg"] * weight_kg
    return (
        f"Shipping {weight_kg} kg to {rate_info['city']}: "
        f"${cost:.2f} USD "
        f"(base ${rate_info['base_fee']} + ${rate_info['rate_per_kg']}/kg)"
    )
