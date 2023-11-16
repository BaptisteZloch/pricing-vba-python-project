from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional
from math import log10
from pricing_library.option import Option
from pricing_library.utils import (
    calculate_down_probability,
    calculate_forward_price,
    calculate_mid_probability,
    calculate_up_probability,
    calculate_up_probability_w_dividend,
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

    # constructor
    def __init__(
        self,
        spot_price: float,
        tree,
        time_step: Optional[datetime] = None,
    ) -> None:
        type(self).nb_nodes = type(self).nb_nodes + 1
        self.time_step = time_step
        self.tree = tree
        self.spot_price = spot_price
        self.forward_price: float = calculate_forward_price(
            self.spot_price, tree.market.interest_rate, self.tree.delta_t
        )
        # check for a dividend date
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
            self.__calculate_probabilities()
        else:
            self.esperance = self.forward_price
            self.__calculate_probabilities()
        # compute the next up and down price from the forward mid price using alpha
        self.up_price: float = self.tree.alpha * self.forward_price
        self.down_price: float = self.forward_price / self.tree.alpha

    def __calculate_probabilities(
        self, with_dividend: bool = False, force_check: bool = False
    ) -> None:
        """Function that calculates the probabilities (for the next up down and mid nodes) of the current node. Note that this function also compute the variance of the current node price. This function MUST be called directly in the constructor and after the forward price has been calculated

        Args:
            with_dividend (bool, optional): If there is a dividend the up probability calculation is different. Defaults to False.
            force_check (bool, optional): Whether you want to check the conditions on the probabilities, the esperance and the variance. Defaults to False.
        """
        self.variance = calculate_variance(
            self.spot_price,
            self.tree.market.interest_rate,
            self.tree.market.volatility,
            self.tree.delta_t,
        )
        self.p_down = calculate_down_probability(
            self.esperance, self.forward_price, self.variance, self.tree.alpha
        )
        # if there is a dividend the up probability is calculated differently
        if with_dividend is True:
            self.p_up = calculate_up_probability_w_dividend(
                self.p_down,
                self.tree.alpha,
                self.esperance,
                self.forward_price,
            )
        else:
            self.p_up = calculate_up_probability(self.p_down, self.tree.alpha)
        # solve for the mid probability to get the probabilities sum to 1
        self.p_mid = calculate_mid_probability(self.p_up, self.p_down)
        if force_check is True:
            self.__check_conditions()

    # main pricing function
    def price(self, opt: Option) -> float:
        """This function will recursively compute the price of the option at the current node. If the option is a european option, the price will be computed only once. If the option is an american option, the price will be computed at each node and the payoff will be taken into account

        Args:
            opt (Option): The option to price.

        Returns:
            float: The price of the option at the current node
        """
        if self.next_mid_node is None:  # End of tree -> leaf
            self.option_price = opt.payoff(self.spot_price)
        elif self.option_price is None:
            # compute the price of the option at the current node from the next nodes
            self.option_price = self.tree.discount_factor * (
                self.p_up * self.next_upper_node.price(opt)
                + self.p_mid * self.next_mid_node.price(opt)
                + self.p_down * self.next_lower_node.price(opt)
            )
        # whether it is an american option or not the payoff is calculated differently
        if opt.exercise_type == "us":
            self.option_price = max(self.option_price, opt.payoff(self.spot_price))
        return self.option_price  # type: ignore

    # sanity check
    def __check_conditions(self, tolerance: float = 1e-4) -> None:
        assert (
            tolerance > 0 and tolerance < 1
        ), "Tolerance must be strictly positive and strictly inferior to 1"
        rounding_factor = int(log10(tolerance))
        proba_total = self.p_down + self.p_up + self.p_mid
        assert (
            proba_total == 1
        ), f"Generation {self.time_step} | Probabilities must sum to 1 | probabilities sum: {proba_total}"
        expected_price = (
            self.down_price * self.p_down
            + self.forward_price * self.p_mid
            + self.up_price * self.p_up
        )
        assert round(expected_price, rounding_factor) == round(
            self.forward_price, rounding_factor
        ), f"Generation {self.time_step} | Prices first order moment must be the forward price | Expected price: {expected_price} forward price: {self.forward_price}"
        second_moment = (
            self.p_down * self.down_price**2
            + self.p_mid * self.forward_price**2
            + self.p_up * self.up_price**2
        )
        assert round(
            second_moment,
            rounding_factor,
        ) == round(
            self.variance + self.esperance**2, rounding_factor
        ), f"Generation {self.time_step} | Prices second order must be the variance | second_moment: {second_moment} variance: {self.variance+ self.forward_price**2}"

    def __str__(self) -> str:
        return f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, current date: {self.time_step}, option value: {self.option_price:.2f}>"

    def __repr__(self) -> str:
        return f"Node<spot price: {self.spot_price:.2f}, next mid price: : {self.forward_price:.2f}, next up price: {self.up_price:.2f}, next down price: {self.down_price:.2f}, variance: {self.variance:.2f}, p down: {self.p_down:.2f}, p mid: {self.p_mid:.2f}, p up: {self.p_up:.2f}, current date: {self.time_step}, option value: {self.option_price:.2f}>"
