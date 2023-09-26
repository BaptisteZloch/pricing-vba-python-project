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
    exercise_type: Literal["am", "eu"]
    strike_price: float
    maturity_date: datetime
