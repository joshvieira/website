from projects.kellybetting.kelly import calc_uniform_kelly_bet


def test_thorp_result_1992():

    b = (-7/10 + 1)/2
    alpha = 1-b

    f = calc_uniform_kelly_bet(p=1, alpha=alpha, b=b)

    assert round(f, 2) == 0.63
