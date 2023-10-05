from __future__ import annotations
from datetime import datetime, timedelta
from types import NoneType
from typing import Optional
from math import exp
import numpy as np
from pricing_library.option import Option
from pricing_library.utils import (
    calculate_down_probability,
    calculate_forward_price,
    calculate_mid_probability,
    calculate_up_probability,
    calculate_variance,
)


class Node:
    node_up: Optional[Node] = None
    node_down: Optional[Node] = None
    next_lower_node: Optional[Node] = None
    next_upper_node: Optional[Node] = None
    next_mid_node: Optional[Node] = None
    nb_nodes = 0  # Static variable to count the number of nodes created
    option_price: Optional[float] = None

    def __init__(
        self,
        spot_price: float,
        tree,
        time_step: Optional[datetime] = None,
        # proba_total: Optional[float] = None,
    ) -> None:
        self.time_step = time_step
        self.tree = tree
        self.spot_price = spot_price
        self.forward_price: float = calculate_forward_price(
            self.spot_price, tree.market.interest_rate, self.tree.delta_t
        )
        if (
            self.time_step is not None
            and self.time_step + timedelta(days=self.tree.delta_t * self.tree.n_days)
            >= self.tree.market.dividend_ex_date
            >= self.time_step
        ):
            self.esperance = self.forward_price
            self.forward_price: float = (
                self.forward_price - self.tree.market.dividend_price
            )
        else:
            self.esperance = self.forward_price

        self.up_price: float = self.tree.alpha * self.forward_price
        self.down_price: float = self.forward_price / self.tree.alpha

        self.__calculate_probabilities()

        # self.proba_total = 0
        type(self).nb_nodes = type(self).nb_nodes + 1

    def price(self, opt: Option) -> float:
        if self.next_mid_node is None:  # End of tree -> leaf
            self.option_price = opt.payoff(self.spot_price)
        elif self.option_price is None:
            self.option_price = self.tree.discount_factor * (
                self.p_up * self.next_upper_node.price(opt)
                + self.p_mid * self.next_mid_node.price(opt)
                + self.p_down * self.next_lower_node.price(opt)
            )

        if opt.exercise_type == "us":
            self.option_price = max(self.option_price, opt.payoff(self.spot_price))
        return self.option_price  # type: ignore

    def __calculate_variance(self) -> None:
        self.variance = calculate_variance(
            self.spot_price,
            self.tree.market.interest_rate,
            self.tree.market.volatility,
            self.tree.delta_t,
        )

    def __calculate_probabilities(self, force_check: bool = False) -> None:
        self.__calculate_variance()
        self.p_down = calculate_down_probability(
            self.forward_price, self.esperance, self.variance, self.tree.alpha
        )
        self.p_up = calculate_up_probability(self.p_down, self.tree.alpha)
        self.p_mid = calculate_mid_probability(self.p_down, self.p_up)
        if force_check is True:
            self.__check_conditions()

    def __check_conditions(self):
        assert self.p_down + self.p_up + self.p_mid == 1, "Probabilities must sum to 1."
        assert (
            self.down_price * self.p_down
            + self.forward_price * self.p_mid
            + self.up_price * self.p_up
            == self.forward_price
        ), "Prices first order moment must be the forward price."
        assert (
            self.p_down * self.down_price**2
            + self.p_mid * self.forward_price**2
            + self.p_up * self.up_price**2
            == self.variance + self.forward_price**2
        ), "Prices second order must be the variance."

    def __str__(self) -> str:
        result_str = f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, current date: {self.time_step}, option value: {self.option_price:.2f}"
        if self.next_mid_node is not None:
            result_str += f"\n next mid node: {self.next_mid_node}"
        if self.next_lower_node is not None:
            result_str += f"\n next lower node: {self.next_lower_node}"
        if self.next_upper_node is not None:
            result_str += f"\n next upper node: {self.next_upper_node}"
        result_str += ">"
        return result_str

    def __repr__(self) -> str:
        return f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, current date: {self.time_step}, option value: {self.option_price:.2f}>"
