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
) -> float:
    """Compute the delta of an option for a given market and a given pricing date.

    Args:
    -----
        mkt (Market): The market conditions used to price the option.
        n_steps (int): The number of steps used to discretize the trinomial tree.
        pricing_date (datetime): The date at which the option is priced.
        opt (Option): The option to price and compute the delta.
        h (float, optional): The step used to discretize the volatility to compute the vega in percent i.e. : 0.01 => +/- 1%. Defaults to 0.01.

    Returns:
    -----
        float: The delta of an option for the given market and pricing date.
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


def gamma(
    mkt: Market,
    n_steps: int,
    pricing_date: datetime,
    opt: Option,
    h: float = 0.01,
) -> float:
    """Compute the gamma of an option for a given market and a given pricing date.

    Args:
    -----
        mkt (Market): The market conditions used to price the option.
        n_steps (int): The number of steps used to discretize the trinomial tree.
        pricing_date (datetime): The date at which the option is priced.
        opt (Option): The option to price and compute the delta.
        h (float, optional): The step used to discretize the volatility to compute the vega in percent i.e. : 0.01 => +/- 1%. Defaults to 0.01.

    Returns:
    -----
        float: The gamma of an option for the given market and pricing date.
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
    price_mid = TrinomialTree(
        Market(
            mkt.interest_rate,
            mkt.volatility,
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
            mkt.volatility,
            mkt_spot_down,
            mkt.dividend_price,
            mkt.dividend_ex_date,
        ),
        pricing_date,
        n_steps,
    ).price(opt)
    delta_up = (price_up - price_mid) / (mkt_spot_up - mkt.spot_price)
    delta_down = (price_mid - price_down) / (mkt.spot_price - mkt_spot_down)

    return (delta_up - delta_down) / (mkt_spot_up - mkt_spot_down) ** 2


def vega(
    mkt: Market,
    n_steps: int,
    pricing_date: datetime,
    opt: Option,
    h: float = 0.01,
):
    """Compute the vega of an option for a given market and a given pricing date.

    Args:
    -----
        mkt (Market): The market conditions used to price the option.
        n_steps (int): The number of steps used to discretize the trinomial tree.
        pricing_date (datetime): The date at which the option is priced.
        opt (Option): The option to price and compute the delta.
        h (float, optional): The step used to discretize the volatility to compute the vega in percent i.e. : 0.01 => +/- 1%. Defaults to 0.01.

    Returns:
    -----
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
