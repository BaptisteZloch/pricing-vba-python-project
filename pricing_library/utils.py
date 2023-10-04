from math import exp, sqrt


def discount_value(
    value_to_discount: float, interest_rates: float, delta_t: float
) -> float:
    return value_to_discount * calculate_discount_factor(
        interest_rates, delta_t
    )  # = S_0 * exp(-r * delta_t)


def calculate_discount_factor(interest_rate: float, delta_t: float) -> float:
    return exp(-interest_rate * delta_t)


def calculate_forward_price(
    spot_price: float, interest_rates: float, delta_t: float
) -> float:
    return spot_price * exp(interest_rates * delta_t)  # = S_0 * exp(r * delta_t)


def calculate_alpha(volatility: float, delta_t: float, factor: int = 3) -> float:
    return exp(volatility * sqrt(factor * delta_t))  # type: ignore
