from datetime import datetime
import numpy as np
from scipy.stats import norm
from pricing_library.market import Market
from pricing_library.option import Option

class BlackScholesOptionPricing:
    def __init__(self,opt:Option, pricing_date:datetime,market:Market):

        self.S = market.spot_price
        self.K = opt.strike_price
        self.T = ((opt.maturity_date - pricing_date).days) / 365
        self.r = market.interest_rate
        self.sigma = market.volatility
        self.option_type = opt.option_type

    def __d1(self):
        d1 = (np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T) / (self.sigma * np.sqrt(self.T))
        return d1

    def __d2(self):
        d2 = self.__d1() - self.sigma * np.sqrt(self.T)
        return d2

    def calculate_option_price(self):
        d1 = self.__d1()
        d2 = self.__d2()
        if self.option_type == 'call':
            call_price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
            return call_price
        elif self.option_type == 'put':
            put_price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
            return put_price
        else:
            raise ValueError("Option type not supported. Use 'call' or 'put'.")