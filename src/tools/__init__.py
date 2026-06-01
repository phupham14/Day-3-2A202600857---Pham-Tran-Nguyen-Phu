from src.tools.check_stock import check_stock
from src.tools.get_price import get_price
from src.tools.get_discount import get_discount
from src.tools.calc_shipping import calc_shipping
from src.tools.calculator import calculator

ALL_TOOLS = [
    {
        "name": "check_stock",
        "description": (
            "Check available stock quantity for a product. "
            "Input: item name (e.g. 'iPhone', 'MacBook'). "
            "Returns stock count and weight per unit."
        ),
        "function": check_stock,
    },
    {
        "name": "get_price",
        "description": (
            "Get the current price of a product in USD. "
            "Input: item name (e.g. 'iPhone', 'Samsung'). "
            "Returns price per unit."
        ),
        "function": get_price,
    },
    {
        "name": "get_discount",
        "description": (
            "Get the discount percentage for a coupon code. "
            "Input: coupon code string (e.g. 'WINNER', 'SALE20'). "
            "Returns discount percentage to subtract from total price."
        ),
        "function": get_discount,
    },
    {
        "name": "calc_shipping",
        "description": (
            "Calculate shipping cost based on total weight and destination city. "
            "Input format: 'weight_kg, destination' (e.g. '0.8, Hanoi' or '1.5, Singapore'). "
            "Returns shipping fee in USD."
        ),
        "function": calc_shipping,
    },
    {
        "name": "calculator",
        "description": (
            "Evaluate a math expression. "
            "Supports +, -, *, /, **, %. "
            "Input: math expression string (e.g. '999 * 2 * 0.9 + 7.8'). "
            "Use this to compute the final total price."
        ),
        "function": calculator,
    },
]
