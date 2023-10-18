from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass
class Option:
    """
    Attributes:
    ----
        option_type (Literal[&quot;call&quot;, &quot;put&quot;]): The type of the option call or put.
        exercise_type (Literal[&quot;am&quot;, &quot;eu&quot;]): The type of the exercise american or european.
        strike_price (float): The strike price of the option.
        maturity_date (datetime): The maturity date of the option.
    """

    option_type: Literal["call", "put"]
    exercise_type: Literal["us", "eu"]
    strike_price: float
    maturity_date: datetime

    def payoff(self, spot) -> float:
        if self.option_type == "call":
            return max(spot - self.strike_price, 0)
        else:
            return max(self.strike_price - spot, 0)
