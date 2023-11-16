from math import exp, sqrt
from time import time
from typing import Any, Callable


# We compute the discount value of a given value at a given date
def discount_value(
    value_to_discount: float, interest_rates: float, delta_t: float
) -> float:
    return value_to_discount * calculate_discount_factor(
        interest_rates, delta_t
    )  # = S_0 * exp(-r * delta_t)


# we compute the discount factor
def calculate_discount_factor(interest_rate: float, delta_t: float) -> float:
    return exp(-interest_rate * delta_t)


# we compute the forward price
def calculate_forward_price(
    spot_price: float, interest_rates: float, delta_t: float
) -> float:
    return spot_price * exp(interest_rates * delta_t)  # = S_0 * exp(r * delta_t)


# we compute the alpha using a factor
def calculate_alpha(volatility: float, delta_t: float, factor: int = 3) -> float:
    return exp(volatility * sqrt(factor * delta_t))


# calculate the variance
def calculate_variance(
    spot_price: float, interest_rate: float, volatility: float, delta_t: float
) -> float:
    return (
        (spot_price**2)
        * exp(2 * interest_rate * delta_t)
        * (exp((volatility**2) * delta_t) - 1)
    )


# Calculate the down probability
def calculate_down_probability(
    esperance: float, forward_price: float, variance: float, alpha: float
) -> float:
    return (
        (esperance ** (-2)) * (variance + forward_price**2)
        - 1
        - (alpha + 1) * ((esperance ** (-1)) * forward_price - 1)
    ) / ((1 - alpha) * ((alpha ** (-2)) - 1))


# calculate the up probability w/o dividend
def calculate_up_probability(down_probability: float, alpha: float) -> float:
    return down_probability / alpha


# calculate the up probability w/ dividend
def calculate_up_probability_w_dividend(
    down_probability: float,
    alpha: float,
    esperance: float,
    forward_price: float,
) -> float:
    return ((alpha - 1) ** (-1)) * (
        (esperance ** (-1)) * forward_price
        - 1
        - ((alpha ** (-1)) - 1) * down_probability
    )


# calculate the mid probability
def calculate_mid_probability(up_probability: float, down_probability: float) -> float:
    return 1 - (down_probability + up_probability)


# utility function that measures the execution time of a function
def measure_time(func: Callable) -> Callable:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(
            f"Elapsed time of the {func.__name__} function: {end_time - start_time:.2f} seconds"
        )
        return result

    return wrapper
