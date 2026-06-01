COUPON_DB = {
    "WINNER": {"discount_pct": 10, "description": "10% off for winners"},
    "SALE20": {"discount_pct": 20, "description": "20% flash sale"},
    "VIP50": {"discount_pct": 50, "description": "50% VIP member discount"},
    "NEWUSER": {"discount_pct": 15, "description": "15% off for new users"},
    "SUMMER": {"discount_pct": 5, "description": "5% summer promotion"},
}


def get_discount(args: str) -> str:
    """
    Get the discount percentage for a coupon code.
    Args: coupon code (string, case-insensitive)
    Returns: discount percentage.
    Example Action: get_discount(WINNER)
    """
    code = args.strip().strip('"').strip("'").upper()
    info = COUPON_DB.get(code)

    if info is None:
        return f"Coupon code '{code}' is invalid or expired."

    return (
        f"Coupon '{code}' gives {info['discount_pct']}% discount "
        f"({info['description']})"
    )
