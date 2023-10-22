from time import time
from tqdm import tqdm
from pricing_library.black_scholes import BlackScholesOptionPricing
from pricing_library.market import Market
from pricing_library.option import Option
from pricing_library.trinomial_tree import TrinomialTree

from datetime import datetime
import sys 

sys.setrecursionlimit(10**6) 


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
bs_price = BlackScholesOptionPricing(opt,pricing_date,mkt).calculate_option_price()
with open(f"./result_gap_convergence_{mkt.spot_price}_{mkt.volatility}_{mkt.interest_rate}_{mkt.dividend_price}_{opt.option_type}_{opt.exercise_type}_{opt.strike_price}.csv",mode="w") as f:
    f.write('steps,time,bs_price,price\n')


for step in tqdm(range(1,100,10),desc="Computing convergence and GAP"):
    t = TrinomialTree(
        market=mkt,
        pricing_date=pricing_date,
        n_steps=step,
    )
    start_time = time()
    price = t.price(
        opt=opt,
        draw_tree=False
    )
    end_time = time()
    with open(f"./result_gap_convergence_{mkt.spot_price}_{mkt.volatility}_{mkt.interest_rate}_{mkt.dividend_price}_{opt.option_type}_{opt.exercise_type}_{opt.strike_price}.csv",mode="a") as f:
        f.write(f"{step},{price},{bs_price},{end_time-start_time}\n")
    del t


for step in tqdm(range(100,2500,20),desc="Computing convergence and GAP"):
    t = TrinomialTree(
        market=mkt,
        pricing_date=pricing_date,
        n_steps=step,
    )
    start_time = time()
    price = t.price(
        opt=opt,
        draw_tree=False
    )
    end_time = time()
    with open(f"./result_gap_convergence_{mkt.spot_price}_{mkt.volatility}_{mkt.interest_rate}_{mkt.dividend_price}_{opt.option_type}_{opt.exercise_type}_{opt.strike_price}.csv",mode="a") as f:
        f.write(f"{step},{price},{bs_price},{end_time-start_time}\n")
    del t
