from __future__ import annotations
from types import NoneType
from typing import Optional
from math import exp
import numpy as np
from pricing_library.utils import discount_value, calculate_forward_price


class Node:
    node_up: Optional[Node] = None
    node_down: Optional[Node] = None
    next_lower_node: Optional[Node] = None
    next_upper_node: Optional[Node] = None
    next_mid_node: Optional[Node] = None

    def __init__(
        self,
        spot_price: float,
        tree,
        proba_total: Optional[float] = None,
    ) -> None:
        self.tree = tree
        self.spot_price: float = spot_price
        self.forward_price: float = calculate_forward_price(
            self.spot_price, tree.market.interest_rate, self.tree.delta_t
        )
        self.up_price: float = self.tree.alpha * self.forward_price
        self.down_price: float = self.forward_price / self.tree.alpha

        self.variance: float = self.calculate_variance()

        self.p_down: float = self.calculate_p_down()
        self.p_up: float = self.calculate_p_up()
        self.p_mid: float = self.calculate_p_mid()

        self.option_value = self.calculate_option_value()
        self.proba_total = 0

    def compute_next_nodes(self) -> Node:
        n = Node(self.forward_price, self.tree)
        self.next_mid_node = n

        if isinstance(self.next_upper_node, NoneType):
            n_up = Node(self.up_price, self.tree)
        else:
            n_up = self.next_upper_node

        self.next_upper_node = n_up

        self.next_upper_node.node_down = n
        n.node_up = n_up

        if isinstance(self.next_lower_node, NoneType):
            n_down = Node(self.down_price, self.tree)
        else:
            n_down = self.next_lower_node
        self.next_lower_node = n_down

        self.next_lower_node.node_up = n
        n.node_down = n_down

        return self.next_mid_node

    # def compute_upper_generation(self):
    #     n = Node(self.up_price, self.tree)
    #     self.next_upper_node = n
    #     n.node_up = self.node_up.next_upper_node
    #     n.node_down = self.next_mid_node.next_upper_node
    #     n.node_up.next_lower_node = n
    #     n.node_down.next_lower_node = n

    def calculate_option_value(
        self,
    ) -> float:
        if self.tree.option.option_type == "call":
            option_value = float(
                np.array(
                    [
                        max(self.tree.option.strike_price - self.up_price, 0),
                        max(self.tree.option.strike_price - self.forward_price, 0),
                        max(self.tree.option.strike_price - self.down_price, 0),
                    ]
                )
                @ np.array([self.p_up, self.p_mid, self.p_down])
            )
        elif self.tree.option.option_type == "put":
            option_value = float(
                np.array(
                    [
                        max(self.up_price - self.tree.option.strike_price, 0),
                        max(self.forward_price - self.tree.option.strike_price, 0),
                        max(self.down_price - self.tree.option.strike_price, 0),
                    ]
                )
                @ np.array([self.p_up, self.p_mid, self.p_down])
            )
        else:
            raise ValueError(f"option_type must be either 'call' or 'put' only.")
        return discount_value(
            option_value, self.tree.market.interest_rate, self.tree.delta_t
        )

    def calculate_variance(self) -> float:
        return (
            (self.spot_price**2)
            * exp(2 * self.tree.market.interest_rate * self.tree.delta_t)
            * (exp(self.tree.market.volatility**2 * self.tree.delta_t) - 1)
        )

    def calculate_p_up(
        self,
    ) -> float:
        return self.p_down / self.tree.alpha

    def calculate_p_mid(self) -> float:
        return 1 - (self.p_down + self.p_up)

    def calculate_p_down(self) -> float:
        return (
            self.forward_price ** (-2) * (self.variance + self.forward_price**2)
            - 1
            - (self.tree.alpha + 1)
            * (self.forward_price ** (-1) * self.forward_price - 1)
        ) / ((1 - self.tree.alpha) * (self.tree.alpha ** (-1) - 1))

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

    def __str__(self) -> str:
        result_str = f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, option value: {self.option_value:.2f}"
        if self.next_mid_node is not None:
            result_str += f",\n next mid node: {self.next_mid_node}"
        if self.next_lower_node is not None:
            result_str += f",\n next lower node: {self.next_lower_node}"
        if self.next_upper_node is not None:
            result_str += f",\n next upper node: {self.next_upper_node}"
        result_str += ">"
        return result_str

    def __repr__(self) -> str:
        return f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, option value: {self.option_value:.2f}>"
