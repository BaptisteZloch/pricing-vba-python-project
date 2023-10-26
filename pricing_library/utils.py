from math import exp, sqrt, log
from time import time
from typing import Callable, Optional
import networkx as nx


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


def calculate_variance(
    spot_price: float, interest_rate: float, volatility: float, delta_t: float
) -> float:
    return (
        (spot_price**2)
        * exp(2 * interest_rate * delta_t)
        * (exp((volatility**2) * delta_t) - 1)
    )


def calculate_down_probability(
    forward_price: float, esperance: float, variance: float, alpha: float
) -> float:
    return (
        (forward_price ** (-2)) * (variance + esperance**2)
        - 1
        - (alpha + 1) * ((forward_price ** (-1)) * esperance - 1)
    ) / ((1 - alpha) * ((alpha ** (-2)) - 1))


def calculate_up_probability(down_probability: float, alpha: float) -> float:
    return down_probability / alpha


def calculate_up_probability_w_dividend(
    down_probability: float, alpha: float, forward_price: float, esperance: float
) -> float:
    return ((1 - alpha) ** (-1)) * (
        (forward_price ^ (-1)) * esperance - 1 - ((alpha ^ (-1)) + 1) * down_probability
    )  # down_probability / alpha


def calculate_mid_probability(up_probability: float, down_probability: float) -> float:
    return 1 - (down_probability + up_probability)


def measure_time(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(
            f"Elapsed time of the {func.__name__} function: {end_time - start_time:.2f} seconds"
        )
        return result

    return wrapper
