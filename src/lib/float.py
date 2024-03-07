# 1/256 to match Color Ramp resolution
FLOAT_MARGIN_OF_ERROR = 0.00390625


def equal(a: float, b: float) -> bool:
    # Within 1/255, which matches Color Ramp resolution
    return abs(a - b) < FLOAT_MARGIN_OF_ERROR


def lte(a: float, b: float) -> bool:
    return equal(a, b) or a < b


def gte(a: float, b: float) -> bool:
    return equal(a, b) or a > b
