import functools
import inspect
import numpy as np
from scipy.optimize import root


def validate(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound_args = inspect.signature(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        inputs = bound_args.arguments
        p = inputs["p"]
        # Check probabilty is valid
        if p < 0 or p > 1:
            raise ValueError(f"{p=} but probability must be between zero and one.")
        # Check we can lose money with nonzero probability
        if p == 1 and inputs["alpha"] <= inputs["b"]:
            raise ValueError(f"Alpha must exceed b if there is to be any way of losing money when p=1.")
        return func(*args, **kwargs)
    return wrapper


@validate
def calc_discrete_kelly_bet(p, alpha, b=1):
    """
    Returns the growth-rate optimal bet size f* in a gambling scenario where,
    with probability p, we win (b-alpha)f* half the time and (b+alpha)f* half the time, and
    with probability 1-p we lose the entire wagered amount f*

    Parameters
    ----------
    p - probability of receiving a random abount, (1-p) is probability of losing whole bet
    alpha - length of the intervals to the left and right of b, also the standard deviation of the discrete RV
    b - the expected odds

    Returns
    -------
    growth-rate optimum bet amount, expressed as a fraction
    """

    if p == 1:

        return -b / (b**2 - alpha**2)

    if alpha == b:

        q = 1 - p
        standard_kelly = p - q / b

        return standard_kelly / (1 + q)

    else:

        v = b**2 - alpha**2

        a = -v
        b_ = p * v + b * (p - 2)
        c = p * (b + 1) - 1

        # this quadratic solution behaves as expected... the other does not
        radical = np.sqrt(b_**2 - 4 * a * c)
        good_root = (-b_ + radical) / (2 * a)

        return good_root


@validate
def calc_uniform_kelly_bet(p, alpha, b=1):
    """
    Similar to calc_discrete_kelly_bet except the odds draw from a uniform distribution.
    The solution is found numerically.

    Parameters
    ----------
    p - probability of receiving a random abount, (1-p) is probability of losing whole bet
    alpha - length of the intervals to the left and right of b
    b - the expected odds

    Returns
    -------
    growth-rate optimum bet amount, expressed as a fraction
    """

    def _formula(f):

        base = (
            p
            / (2 * alpha * f)
            * (2 * alpha - (1 / f) * np.log((1 + (b + alpha) * f) / (1 + (b - alpha) * f)))
        )

        if p == 1:
            return base
        else:
            return base - (1 - p) / (1 - f)

    standard_kelly = p - (1-p)/b

    return root(_formula, x0=standard_kelly).x[0]


def thorp1992(f):

    return (1 / f) * np.log((1 + f) / (1 - 7 * f / 10)) - 17 / 10


if __name__ == "__main__":

    a = calc_uniform_kelly_bet(p=1, alpha=17/20, b=1.5/10)

    mu = 0.058
    sigma = 0.2160

    solution1 = root(
        fun=partial(calc_uniform_kelly_bet, a=sigma * np.sqrt(3), b=mu, p=1), x0=1
    )
    solution2 = root(fun=partial(calc_uniform_kelly_bet, a=sigma * 3, b=mu, p=1), x0=1)

    print(f"Uniform with same variance: {solution1.x[0]}")
    print(f"Uniform with same endpoints: {solution2.x[0]}")
    print(
        f"Binary with same variance: {calc_discrete_kelly_bet(p=1, alpha=sigma, b=mu)}"
    )
    print(
        f"Binary with same endpoints: {calc_discrete_kelly_bet(p=1, alpha=sigma*3, b=mu)}"
    )

    print("OK")

    # print(
    #     calc_kelly_bet(p=0.75, alpha=1, b=1),
    #     calc_kelly_bet(p=0.9, alpha=4, b=.3)
    # )
