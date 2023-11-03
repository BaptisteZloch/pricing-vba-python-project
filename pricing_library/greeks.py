from datetime import datetime
from pricing_library.market import Market
from pricing_library.option import Option
from pricing_library.trinomial_tree import TrinomialTree


def delta(
    mkt: Market,
    n_steps: int,
    pricing_date: datetime,
    opt: Option,
    h: float = 0.01,
)->float:
    """_summary_

    Args:
        mkt (Market): _description_
        n_steps (int): _description_
        pricing_date (datetime): _description_
        opt (Option): _description_
        h (float, optional): The step used to discretize the volatility to compute the vega in percent i.e. : 0.01 => +/- 1%. Defaults to 0.01.

    Returns:
        float: _description_
    """
    mkt_spot_up, mkt_spot_down = mkt.spot_price * (1 + h), mkt.spot_price * (1 - h)

    price_up = TrinomialTree(
        Market(
            mkt.interest_rate,
            mkt.volatility,
            mkt_spot_up,
            mkt.dividend_price,
            mkt.dividend_ex_date,
        ),
        pricing_date,
        n_steps,
    ).price(opt)
    price_down = TrinomialTree(
        Market(
            mkt.interest_rate,
            mkt.volatility,
            mkt_spot_down,
            mkt.dividend_price,
            mkt.dividend_ex_date,
        ),
        pricing_date,
        n_steps,
    ).price(opt)

    return (price_up - price_down) / (mkt_spot_up - mkt_spot_down)


# def gamma(opt: Option, mkt: Market, h: float = 0.01):
#     """_summary_

#     Args:
#         opt (Option): _description_
#         mkt (Market): _description_
#         h (float): The step used to compute the delta in percent i.e. : 0.01=> +/- 1%. Defaults to 0.01.
#     """
#     mkt_spot_up, mkt_spot_down = mkt.spot_price * (1 + h), mkt.spot_price * (1 - h)
#     pass


def vega(
    mkt: Market,
    n_steps: int,
    pricing_date: datetime,
    opt: Option,
    h: float = 0.01,
):
    """_summary_

    Args:
        mkt (Market): _description_
        n_steps (int): _description_
        pricing_date (datetime): _description_
        opt (Option): _description_
        h (float, optional): The step used to discretize the volatility to compute the vega in percent i.e. : 0.01 => +/- 1%. Defaults to 0.01.

    Returns:
        float: _description_
    """
    mkt_vol_up, mkt_vol_down = mkt.volatility * (1 + h), mkt.volatility * (1 - h)

    price_up = TrinomialTree(
        Market(
            mkt.interest_rate,
            mkt_vol_up,
            mkt.spot_price,
            mkt.dividend_price,
            mkt.dividend_ex_date,
        ),
        pricing_date,
        n_steps,
    ).price(opt)
    price_down = TrinomialTree(
        Market(
            mkt.interest_rate,
            mkt_vol_down,
            mkt.spot_price,
            mkt.dividend_price,
            mkt.dividend_ex_date,
        ),
        pricing_date,
        n_steps,
    ).price(opt)

    return (price_up - price_down) / (mkt_vol_up - mkt_vol_down)
