from datetime import datetime
from math import exp, sqrt
from pricing_library.node import Node
from pricing_library.market import MarketData
from pricing_library.option import Option


class TrinomialTree:
    n_days = 365

    def __init__(
        self,
        market: MarketData,
        option: Option,
        pricing_date: datetime,
        n_steps: int,
    ) -> None:
        """_summary_

        Args:
        ----
            market (MarketData): The MarketData object containing market informations.
            option (Option): The option associated with the trinomial tree.
            pricing_date (datetime): Pricing date of the option, could be today but must be before maturity_date.
            n_steps (int): The number of steps in the trinomial tree.
        """
        self.option = option
        self.market = market

        # calculate delta t and alpha
        assert (
            pricing_date < self.option.maturity_date
        ), "Pricing date must be before maturity date."
        self.n_steps = n_steps
        self.pricing_date = pricing_date
        self.delta_t = abs(
            ((self.option.maturity_date - pricing_date).days / n_steps) / self.n_days
        )
        self.alpha = self.calculate_alpha()
        self.root = Node(market.spot_price, self)  # S_0...
        self.root.add_child_node()

    # def _init_nodes(self)->None:
    #     while self.root.next_mid_node is None:
    #         self.root.add_child_node()

    def calculate_alpha(self) -> float:
        return exp(self.market.volatility * sqrt(3 * self.delta_t))  # type: ignore
