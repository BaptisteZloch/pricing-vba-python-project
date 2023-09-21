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
        maturity_date: datetime,
        n_steps: int,
    ) -> None:
        """_summary_

        Args:
        ----
            market (MarketData): The MarketData object containing market informations.
            option (Option): The option associated with the trinomial tree.
            pricing_date (datetime): Pricing date of the option, could be today but must be before maturity_date.
            maturity_date (datetime): The maturity date of the option.
            n_steps (int): The number of steps in the trinomial tree.
        """
        self.option = option
        self.market = market
        self.root = Node(market.spot_price, self)  # S_0...
        # calculate delta t and alpha
        assert (
            pricing_date < maturity_date
        ), "Pricing date must be before maturity date."
        self.n_steps = n_steps
        self.pricing_date = pricing_date
        self.delta_t = abs(
            ((maturity_date - pricing_date).days / self.n_days) / n_steps
        )
        self.alpha = self.calculate_alpha()

    def calculate_alpha(self) -> float:
        return exp(self.market.volatility * sqrt(3 * self.delta_t))
