from pricing_library.black_scholes import BlackScholesOptionPricing
from pricing_library.market import Market
from pricing_library.option import Option
from pricing_library.trinomial_tree import TrinomialTree

from datetime import datetime
opt=Option(
        option_type="call",
        exercise_type="eu",
        strike_price=102,
        maturity_date=datetime(2024, 9, 19),
    )
mkt=Market(
        interest_rate=0.04,
        volatility=0.25,
        spot_price=100,
        dividend_price=0,
        dividend_ex_date=datetime(2024, 5, 24),
    )
pricing_date=datetime(2023, 9, 20)

t = TrinomialTree(
    market=mkt,
    pricing_date=pricing_date,
    n_steps=100,
)

price = t.price(
    opt=opt,
    draw_tree=False
)
print(f"Trinomial price : {price} vs BS price : {BlackScholesOptionPricing(opt,pricing_date,mkt).calculate_option_price()}")
