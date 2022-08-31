import os.path
import functools
import inspect
import numpy as np
from scipy.optimize import root
import matplotlib.pyplot as plt
import pandas as pd
import itertools
from dotenv import load_dotenv


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
            raise ValueError(
                f"Alpha must exceed b if there is to be any way of losing money when p=1."
            )
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

        standard_kelly = get_standard_kelly_bet(p=p, b=b)

        q = 1 - p

        return standard_kelly / (1 + q)

    else:

        v = b**2 - alpha**2

        a = -v
        b_ = p * v + b * (p - 2)
        c = p * (b + 1) - 1

        # this quadratic solution behaves as expected... the other does not
        radical = np.sqrt(b_**2 - 4 * a * c)
        good_root = (-b_ - radical) / (2 * a)

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
            * (
                2 * alpha
                - (1 / f) * np.log((1 + (b + alpha) * f) / (1 + (b - alpha) * f))
            )
        )

        if p == 1:
            return base
        else:
            return base - (1 - p) / (1 - f)

    standard_kelly = get_standard_kelly_bet(p=p, b=b)

    if alpha == 0:
        return standard_kelly
    else:
        return root(_formula, x0=0.75 * standard_kelly).x[0]


def get_standard_kelly_bet(p, b=1):

    edge = b * p - (1 - p)

    return edge / b


def create_kelly_plot(show=False, save=False):



    alphas = np.arange(0, 2 + 0.1, 0.1)
    probabilities = np.arange(0.55, 0.95 + 0.1, 0.1)

    # standard kelly dataframe
    df_standard = pd.DataFrame(index=alphas, columns=probabilities)
    df_standard.loc[:] = [get_standard_kelly_bet(p) for p in probabilities]

    # odds ~ continuous uniform random variable
    params = list(itertools.product(alphas, probabilities))
    dimensions = (len(alphas), len(probabilities))
    data = np.array(
        [calc_uniform_kelly_bet(p=y, alpha=x) for (x, y) in params]
    ).reshape(dimensions)
    df_uniform = pd.DataFrame(index=alphas, columns=probabilities, data=data)

    # odds ~ discrete (2-outcome) random variable
    data = np.array(
        [calc_discrete_kelly_bet(p=y, alpha=x) for (x, y) in params]
    ).reshape(dimensions)
    df_discrete = pd.DataFrame(index=alphas, columns=probabilities, data=data)

    fig, ax = plt.subplots()
    ax.plot(df_discrete, label=[f"{p=}" for p in probabilities])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        reversed(handles),
        reversed(labels),
        ncol=len(probabilities),
        bbox_to_anchor=(1.09, 1.14),
        frameon=False,
    )
    plt.subplots_adjust(top=0.8)
    ax.set_title(
        r"$\it{f^*}$ as a function of $\alpha$ when E(odds) = 1", pad=40, fontsize=14
    )
    ax.set_prop_cycle(None)
    ax.plot(df_uniform, linestyle="--")
    ax.set_xlim(alphas[0], alphas[-1])
    ax.set_ylim(0, 1)
    ax.set_xlabel(r"$\alpha$")
    ax.set_ylabel("Optimal bet size")

    ax.text(1.6, 0.87, "uniform")
    ax.text(1.33, 0.75, "discrete")

    plt.grid(axis="y", which="major", linestyle="--")

    if show:
        plt.show()
    if save:
        load_dotenv()
        fname = "bet_fraction_plot.png"
        fig.savefig(os.path.join(os.getenv('TEMP_FOLDER'), fname))


if __name__ == "__main__":

    create_kelly_plot(show=True, save=True)
