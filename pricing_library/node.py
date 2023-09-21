from __future__ import annotations
from typing import Literal, Optional
from math import exp
import numpy as np
from pricing_library.utils import discount_value, calculate_forward_price
from pricing_library.trinomial_tree import TrinomialTree


class Node:
    node_up: Optional[Node] = None
    node_down: Optional[Node] = None

    def __init__(
        self,
        spot_price: float,
        tree: TrinomialTree,
        # interest_rates: float,
        # delta_t: float,
        # alpha: float,
        # volatility: float,
        # option_strike_price: float,
        # option_type: Literal["call", "put"],
    ) -> None:
        self.tree = tree

        self.spot_price = spot_price

        self.forward_price = calculate_forward_price(
            self.spot_price, interest_rates, delta_t
        )
        self.up_price = alpha * self.forward_price
        self.down_price = self.forward_price / alpha

        n = Node(self.forward_price)
        self.next_mid_node = n
        n_up = Node(self.up_price)
        self.next_upper_node = n_up
        n.node_up = n_up

        n_down = Node(self.down_price)
        self.next_lower_node = n_down
        n.node_down = n_up

        self.variance = self.calculate_variance(volatility, delta_t, interest_rates)

        self.p_down = self.calculate_p_down(alpha)
        self.p_up = self.calculate_p_up(alpha)
        self.p_mid = self.calculate_p_mid()

        self.option_value = self.calculate_option_value(
            option_strike_price, interest_rates, delta_t, option_type
        )

    def calculate_option_value(
        self,
        option_strike_price: float,
        interest_rates: float,
        delta_t: float,
        option_type: Literal["put", "call"],
    ) -> float:
        if option_type == "call":
            option_value = float(
                np.array(
                    [
                        max(option_strike_price - self.up_price, 0),
                        max(option_strike_price - self.forward_price, 0),
                        max(option_strike_price - self.down_price, 0),
                    ]
                )
                @ np.array([self.p_up, self.p_mid, self.p_down])
            )
        elif option_type == "put":
            option_value = float(
                np.array(
                    [
                        max(self.up_price - option_strike_price, 0),
                        max(self.forward_price - option_strike_price, 0),
                        max(self.down_price - option_strike_price, 0),
                    ]
                )
                @ np.array([self.p_up, self.p_mid, self.p_down])
            )
        else:
            raise ValueError(
                f"option_type must be either 'call' or 'put', not {option_type}."
            )
        return discount_value(option_value, interest_rates, delta_t)

    def calculate_variance(
        self, volatility: float, delta_t: float, interest_rates: float
    ) -> float:
        return (
            (self.spot_price**2)
            * exp(2 * interest_rates * delta_t)
            * (exp(volatility**2 * delta_t) - 1)
        )

    def calculate_p_up(self, alpha) -> float:
        return self.p_down / alpha

    def calculate_p_mid(self) -> float:
        return 1 - (self.p_down + self.p_up)

    def calculate_p_down(self, alpha) -> float:
        return (
            self.forward_price ** (-2) * (self.variance + self.forward_price**2)
            - 1
            - (alpha + 1) * (self.forward_price ** (-1) * self.forward_price - 1)
        ) / ((1 - alpha) * (alpha ** (-1) - 1))

    def check_conditions(self):
        assert self.p_down + self.p_up + self.p_mid == 1, "Probabilities must sum to 1."
        assert (
            np.array([self.down_price, self.forward_price, self.up_price])
            @ np.array(
                [
                    self.p_down,
                    self.p_mid,
                    self.p_up,
                ]
            )
            == self.forward_price
        ), "Prices first order moment must be the forward price."
        assert (
            np.array(
                [self.down_price**2, self.forward_price**2, self.up_price**2]
            )
            @ np.array(
                [
                    self.p_down,
                    self.p_mid,
                    self.p_up,
                ]
            )
            == self.variance + self.forward_price**2
        ), "Prices second order must be the variance."
