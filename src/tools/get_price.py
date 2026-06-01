PRICE_DB = {
    "iphone": {"name": "iPhone 15", "price_usd": 999},
    "iphone 15": {"name": "iPhone 15", "price_usd": 999},
    "iphone15": {"name": "iPhone 15", "price_usd": 999},
    "samsung": {"name": "Samsung Galaxy S24", "price_usd": 799},
    "samsung galaxy s24": {"name": "Samsung Galaxy S24", "price_usd": 799},
    "macbook": {"name": "MacBook Air M3", "price_usd": 1299},
    "macbook air": {"name": "MacBook Air M3", "price_usd": 1299},
    "airpods": {"name": "AirPods Pro 2", "price_usd": 249},
    "airpods pro": {"name": "AirPods Pro 2", "price_usd": 249},
    "ipad": {"name": "iPad Pro 11", "price_usd": 1099},
}


def get_price(args: str) -> str:
    """
    Get the current price of an item.
    Args: item name (string)
    Returns: price in USD.
    Example Action: get_price(iPhone)
    """
    item = args.strip().strip('"').strip("'").lower()
    info = PRICE_DB.get(item)

    if info is None:
        available = ", ".join(PRICE_DB.keys())
        return f"Item '{item}' not found. Available items: {available}"

    return f"{info['name']} costs ${info['price_usd']} USD per unit"
