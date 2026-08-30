import pytest
from crypto_signals.quant_models import KellyCriterion, MonteCarloModel, QuantRiskModel

def test_kelly_is_capped_and_never_negative_size():
    result = KellyCriterion(.25).calculate(.6, 1.5)
    assert result.raw_fraction > 0
    assert result.capped_fraction <= .25
    assert KellyCriterion().calculate(.2, 1).capped_fraction == 0

def test_monte_carlo_is_deterministic_and_bounded():
    model = MonteCarloModel(200, 10, seed=4)
    a = model.simulate(.5, 1.5, .05)
    b = model.simulate(.5, 1.5, .05)
    assert a == b
    assert 0 <= a.ruin_probability <= 1
    assert a.p05_equity > 0

def test_quant_model_rejects_invalid_payoff():
    with pytest.raises(ValueError): QuantRiskModel().evaluate(0)

def test_bayesian_win_rate_adapts_with_bounded_interval():
    from crypto_signals.quant_models import BayesianWinRate
    result = BayesianWinRate().update(8, 2)
    assert .5 < result.posterior_mean < 1
    assert 0 <= result.lower_bound <= result.upper_bound <= 1

def test_ewma_var_and_bootstrap_are_lightweight():
    from crypto_signals.quant_models import EWMAVolatility, HistoricalVaR, BootstrapInterval
    returns = [-.02, .01] * 20
    assert EWMAVolatility().estimate(returns) > 0
    assert HistoricalVaR().loss(returns) >= 0
    low, high = BootstrapInterval(100).mean_interval(returns)
    assert low <= high
