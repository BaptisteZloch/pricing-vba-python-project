from datetime import datetime
import numpy as np
from scipy.stats import norm
from pricing_library.market import Market
from pricing_library.option import Option


class BlackScholesOptionPricing:
    # constructor
    def __init__(self, opt: Option, pricing_date: datetime, market: Market) -> None:
        self.S = market.spot_price
        self.K = opt.strike_price
        self.T = ((opt.maturity_date - pricing_date).days) / 365
        self.r = market.interest_rate
        self.sigma = market.volatility
        self.option_type = opt.option_type

    # we first calculate d1 and d2
    def __d1(self) -> float:
        """Compute d1 of the Black-Scholes formula.

        Returns:
            float: The value of d1.
        """
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        return d1

    def __d2(self) -> float:
        """Compute d2 of the Black-Scholes formula.

        Returns:
            float: The value of d2.
        """
        d2 = self.__d1() - self.sigma * np.sqrt(self.T)
        return d2

    # we then calculate the price of the option
    def calculate_option_price(self) -> float:
        """This function calculates the price of the option using the Black-Scholes formula.

        Raises:
            ValueError: The option type is not supported.

        Returns:
            float: The price of the option.
        """
        d1 = self.__d1()
        d2 = self.__d2()
        if self.option_type == "call":
            call_price = self.S * norm.cdf(d1) - self.K * np.exp(
                -self.r * self.T
            ) * norm.cdf(d2)
            return call_price
        elif self.option_type == "put":
            put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(
                -d2
            ) - self.S * norm.cdf(-d1)
            return put_price
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")

    # Greek calculations
    def calculate_delta(self) -> float:
        """Calculate delta of the option

        Raises:
            ValueError: When option type is not supported

        Returns:
            float: The delta of the option.
        """
        d1 = self.__d1()
        if self.option_type == "call":
            delta = norm.cdf(d1)
            return delta
        elif self.option_type == "put":
            delta = norm.cdf(d1) - 1
            return delta
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")

    def calculate_gamma(self) -> float:
        """Calculate gamma of the option

        Returns:
            float: The gamma of the option.
        """
        d1 = self.__d1()
        gamma = norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))
        return gamma

    def calculate_vega(self) -> float:
        """Calculate the vega of the option

        Returns:
            float: THe vega of the option.
        """
        d1 = self.__d1()
        vega = self.S * norm.pdf(d1) * np.sqrt(self.T)
        return vega
