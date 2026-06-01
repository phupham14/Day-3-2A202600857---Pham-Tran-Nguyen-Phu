STOCK_DB = {
    "iphone": {"name": "iPhone 15", "stock": 5, "weight_kg": 0.4},
    "iphone 15": {"name": "iPhone 15", "stock": 5, "weight_kg": 0.4},
    "iphone15": {"name": "iPhone 15", "stock": 5, "weight_kg": 0.4},
    "samsung": {"name": "Samsung Galaxy S24", "stock": 12, "weight_kg": 0.5},
    "samsung galaxy s24": {"name": "Samsung Galaxy S24", "stock": 12, "weight_kg": 0.5},
    "macbook": {"name": "MacBook Air M3", "stock": 3, "weight_kg": 1.24},
    "macbook air": {"name": "MacBook Air M3", "stock": 3, "weight_kg": 1.24},
    "airpods": {"name": "AirPods Pro 2", "stock": 20, "weight_kg": 0.06},
    "airpods pro": {"name": "AirPods Pro 2", "stock": 20, "weight_kg": 0.06},
    "ipad": {"name": "iPad Pro 11", "stock": 0, "weight_kg": 0.47},
}


def check_stock(args: str) -> str:
    """
    Check available stock for an item.
    Args: item name (string)
    Returns: stock quantity and weight info.
    Example Action: check_stock(iPhone)
    """
    item = args.strip().strip('"').strip("'").lower()
    info = STOCK_DB.get(item)

    if info is None:
        available = ", ".join(STOCK_DB.keys())
        return f"Item '{item}' not found. Available items: {available}"

    if info["stock"] == 0:
        return f"{info['name']}: OUT OF STOCK"

    return (
        f"{info['name']}: {info['stock']} units in stock "
        f"(weight per unit: {info['weight_kg']} kg)"
    )
