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


def calculate_mid_probability(up_probability: float, down_probability: float) -> float:
    return 1 - (down_probability + up_probability)


def measure_time(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        print(
            f"Elapsed time the {func.__name__} function: {end_time - start_time:.2f} seconds"
        )
        return result

    return wrapper


def display_tree(node, graph: Optional[nx.Graph] = None) -> nx.Graph:
    """_summary_

    Args:
        node (Node): The root node of the tree to display.
        graph (Optional[nx.Graph], optional): The current graph. Defaults to None.

    Returns:
        nx.Graph: The final graph.
    """
    if graph is None:
        graph = nx.Graph()

    for child in [
        node.next_lower_node,
        node.next_mid_node,
        node.next_upper_node,
    ]:
        if child is not None:
            graph.add_edge(node, child.spot_price)
            display_tree(child, graph)

    return graph


# from pricing_library.market import Market
# from pricing_library.option import Option
# class BS:
#     nb_days = 365

#     def __init__(self, option: Option, market: Market):
#         self.market = market
#         self.option = option

#         self.time_to_maturity = (
#             self.option.maturity_date - self.tree.pricing_date
#         ) / self.nb_days  # pour avoir en fraction

#     def calculate_d1_d2(self) -> None:
#         self.d1 = (
#             1
#             / (self.market.volatility * sqrt(self.time_to_maturity))
#             * (
#                 log(self.market.spot_price / self.option.strike_price)
#                 + (self.market.interest_rate + (self.market.volatility**2) / 2)
#                 * self.time_to_maturity
#             )
#         )
#         self.d2 = self.d1 - self.market.volatility * sqrt(self.time_to_maturity)

#     def calculate_option_price(self) -> float:
#         if self.option.option_type == "call":
#             option_price_BS = self.market.spot_price * calculate_norm(
#                 self.d1
#             ) - self.option.strike_price * calculate_norm(self.d2) * exp(
#                 -self.market.interest_rate * self.time_to_maturity
#             )
#         if self.option.option_type == "put":
#             option_price_BS = self.option.strike_price * calculate_norm(-self.d2) * exp(
#                 -self.market.interest_rate * self.time_to_maturity
#             ) - self.market.spot_price * calculate_norm(-self.d1)
#         else:
#             raise ValueError("Option type does not exist, please select call or put")

#         return option_price_BS

#     def calculate_check_BS(self):
#         if self.market.spot_price * calculate_norm(
#             self.d1
#         ) - self.option.strike_price * calculate_norm(self.d2) * exp(
#             -self.market.interest_rate * self.time_to_maturity
#         ) - self.option.strike_price * calculate_norm(
#             -self.d2
#         ) * exp(
#             -self.market.interest_rate * self.time_to_maturity
#         ) - self.market.spot_price * calculate_norm(
#             -self.d1
#         ) != self.market.spot_price - self.option.strike_price * exp(
#             -self.market.interest_rate * self.tree.delta_t
#         ):
#             raise ValueError("Problem about BS")
