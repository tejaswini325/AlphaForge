# Research methodology

## Returns and features

Simple return is \(r_t=P_t/P_{t-1}-1\). Log return is \(\log(P_t/P_{t-1})\). Features include 1-day return, momentum \(P_t/P_{t-k}-1\), rolling return volatility, and price-to-moving-average gap. Features at date t use prices through the close of t. The prediction target is the next observed row's return, \(y_t=P_{t+1}/P_t-1\).

Missing values at rolling-window boundaries remain missing; they are not backfilled from future data. Model imputation is fitted only on training observations.

## Chronological evaluation

Distinct dates are sorted and partitioned into 60% training, 20% validation, and 20% test. No random shuffling is performed. The current baselines are a zero-return forecast, Ridge, Random Forest and histogram gradient boosting. The test set is not used to fit preprocessing or model parameters. Validation is reserved but not used for automated hyperparameter selection. MAE and RMSE assess forecast error; directional accuracy assesses sign agreement. Daily cross-sectional IC is the Pearson correlation between Ridge predictions and realized next-row returns for each test date with at least three assets. Predictive accuracy does not imply a profitable strategy.

## Portfolio construction

Equal-weight assigns \(w_i=1/N\). Inverse volatility uses weights proportional to \(1/\hat\sigma_i\). Minimum variance minimizes \(w^	op\Sigma w\); mean-variance minimizes \(\gamma w^	op\Sigma w-\mu^	op w\), subject to sum-to-one and configured bounds. Sample means and covariances are annualized using 252 trading days and a small diagonal regularizer is added to covariance. Estimates are noisy and sensitive to the window and universe.

## Backtest timing and costs

At rebalance point i, weights are calculated from returns ending at i-1; they then earn return i. This avoids using the return being earned to set weights. The simplified simulator applies a cost once at rebalancing. One-way turnover is \(TO_t=rac12\sum_i|w_{i,t}-w_{i,t-1}|\). Cost fraction is \(TO_t(c+s)/10000\), where c and s are cost and slippage basis points. Net return is \((1+r_{gross})(1-cost)-1\). This is a simplified proportional cost model; it does not model market impact, spread variation, taxes, minimum fees or execution delay.

## Metrics

We use 252 trading days/year and a default 2% annual risk-free rate. Annualized volatility is daily standard deviation times \(\sqrt{252}\). Sharpe is annualized mean daily excess return divided by daily standard deviation. Sortino uses downside deviation of daily excess returns. Maximum drawdown is the minimum of wealth divided by its running maximum minus one. Annualized return uses observed compounded wealth raised to \(252/n\). Information Ratio uses active portfolio returns divided by tracking error where benchmark observations align.

## Statistical tests

The Augmented Dickey-Fuller test's null hypothesis is that a series has a unit root. Tests are run on returns, not price levels, and are skipped for short or constant samples. A single p-value is not proof of stationarity and test power depends on specification and sample.

## Bias and limitations

Fixed universes may have survivorship bias; adjusted close treatment depends on provider methodology. Missing price rows are not fabricated, but returns may be missing where observations are absent. This implementation does not provide point-in-time constituents, sector constraints, bootstrap intervals, or next-open execution. Backtest estimates are not forecasts of future returns.
