from math import exp, sqrt


def discount_value(
    value_to_discount: float, interest_rates: float, delta_t: float
) -> float:
    return value_to_discount * exp(
        -interest_rates * delta_t
    )  # = S_0 * exp(-r * delta_t)


def calculate_forward_price(
    spot_price: float, interest_rates: float, delta_t: float
) -> float:
    return spot_price * exp(interest_rates * delta_t)  # = S_0 * exp(r * delta_t)


def calculate_alpha(volatility: float, delta_t: float) -> float:
    return exp(volatility * sqrt(3 * delta_t))  # type: ignore
