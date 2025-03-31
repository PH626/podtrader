### Overlap Studies (叠加研究)

#### BBANDS: Bollinger Bands.

**Description**

Bollinger Bands consist of a middle band (SMA) and two outer bands that are typically set 2 standard deviations above and below the middle band. It measures price volatility.

**Inputs**

- close: Close prices.
- timeperiod: Number of periods (default: 20).
- nbdevup: Number of standard deviations above the SMA (default: 2.0).
- nbdevdn: Number of standard deviations below the SMA (default: 2.0).

**Formula**

- Middle Band = SMA(close, timeperiod=20)
- Upper Band = Middle Band + nbdevup * StdDev(close, timeperiod=20)
- Lower Band = Middle Band - nbdevdn * StdDev(close, timeperiod=20)

#### DEMA: Double Exponential Moving Average.

**Description**

DEMA is a fast-acting moving average that is more responsive to price changes than a simple moving average.

**Inputs**

- close: Close prices.
- timeperiod: Number of periods (default: 30).
- matype: Type of moving average (default: 0).

**Formula**

- DEMA = 2 * EMA(close, timeperiod) - EMA(EMA(close, timeperiod), timeperiod)

#### EMA: Exponential Moving Average.

**Description**

EMA is a type of moving average that gives more weight to recent prices.

**Inputs**

- close: Close prices.
- timeperiod: Number of periods (default: 30).
- matype: Type of moving average (default: 0).

**Formula**

- EMA[t] = α * close + (1 - α) * EMA[t-1]
- α = 2 / (timeperiod + 1)


#### HT_TRENDLINE: Hilbert Transform - Instantaneous Trendline.

**Description**


**Inputs**


**Formula**



#### KAMA: Kaufman Adaptive Moving Average.

**Description**


**Inputs**


**Formula**



#### MA: Moving Average. Averages prices over a specified period.

**Description**


**Inputs**


**Formula**



#### MAMA: MESA Adaptive Moving Average.

**Description**


**Inputs**


**Formula**



#### MIDPOINT: Midpoint over period.

**Description**


**Inputs**


**Formula**



#### MIDPRICE: Midpoint Price.

**Description**


**Inputs**


**Formula**



#### SAR: Parabolic SAR.

**Description**


**Inputs**


**Formula**



#### SMA: Simple Moving Average.

**Description**


**Inputs**


**Formula**



#### T3: Triple Exponential Moving Average (T3).

**Description**


**Inputs**


**Formula**



#### TEMA: Triple Exponential Moving Average.

**Description**


**Inputs**


**Formula**



#### TRIMA: Triangular Moving Average.

**Description**


**Inputs**


**Formula**



#### WMA: Weighted Moving Average.

**Description**


**Inputs**


**Formula**



---

### Momentum Indicators (动量指标)

#### ADX: Average Directional Index.

**Description**


**Inputs**


**Formula**



#### ADXR: Average Directional Movement Rating.

**Description**


**Inputs**


**Formula**



#### APO: Absolute Price Oscillator.

**Description**


**Inputs**


**Formula**



#### AROON: Aroon.

**Description**


**Inputs**


**Formula**



#### AROONOSC: Aroon Oscillator.

**Description**


**Inputs**


**Formula**



#### BOP: Balance of Power.

**Description**


**Inputs**


**Formula**



#### CCI: Commodity Channel Index.

**Description**


**Inputs**


**Formula**



#### CMO: Chande Momentum Oscillator.

**Description**


**Inputs**


**Formula**



#### DX: Directional Movement Index.

**Description**


**Inputs**


**Formula**



#### MACD: Moving Average Convergence Divergence.

**Description**


**Inputs**


**Formula**



#### MACDEXT: Extended MACD.

**Description**


**Inputs**


**Formula**



#### MFI: Money Flow Index.

**Description**


**Inputs**


**Formula**



#### MINUS_DI: Minus Directional Indicator.

**Description**


**Inputs**


**Formula**



#### MINUS_DM: Minus Directional Movement.

**Description**


**Inputs**


**Formula**



#### MOM: Momentum. Measures price changes over time.

**Description**


**Inputs**


**Formula**



#### PLUS_DI: Plus Directional Indicator.

**Description**


**Inputs**


**Formula**



#### PLUS_DM: Plus Directional Movement.

**Description**


**Inputs**


**Formula**



#### PPO: Percentage Price Oscillator.

**Description**


**Inputs**


**Formula**



#### ROC: Rate of Change.

**Description**


**Inputs**


**Formula**



#### ROCP: Rate of Change Percentage.

**Description**


**Inputs**


**Formula**



#### RSI: Relative Strength Index.

**Description**


**Inputs**


**Formula**



#### STOCH: Stochastic Oscillator.

**Description**


**Inputs**


**Formula**



#### STOCHF: Fast Stochastic Oscillator.

**Description**


**Inputs**


**Formula**



#### STOCHRSI: Stochastic Relative Strength Index.

**Description**


**Inputs**


**Formula**



#### TRIX: Triple Exponential Average.

**Description**


**Inputs**


**Formula**



#### ULTOSC: Ultimate Oscillator.

**Description**


**Inputs**


**Formula**



#### WILLR: Williams %R.

**Description**


**Inputs**


**Formula**




---

### Volume Indicators (成交量指标)

#### AD: Chaikin A/D Line.

**Description**


**Inputs**


**Formula**



#### ADOSC: Chaikin A/D Oscillator.

**Description**


**Inputs**


**Formula**



#### OBV: On Balance Volume.

**Description**


**Inputs**


**Formula**




---

### Volatility Indicators (波动率指标)

#### ATR: Average True Range.

**Description**


**Inputs**


**Formula**



#### NATR: Normalized ATR.

**Description**


**Inputs**


**Formula**



#### TRANGE: True Range.

**Description**


**Inputs**


**Formula**




---

### Price Transform (价格变换)

#### AVGPRICE: Average Price.

**Description**


**Inputs**


**Formula**



#### MEDPRICE: Median Price.

**Description**


**Inputs**


**Formula**



#### TYPPRICE: Typical Price.

**Description**


**Inputs**


**Formula**



#### WCLPRICE: Weighted Close Price.

**Description**


**Inputs**


**Formula**




---

### Cycle Indicators (周期指标)

#### HT_DCPERIOD: Hilbert Transform - Dominant Cycle Period.

**Description**


**Inputs**


**Formula**



#### HT_DCPHASE: Hilbert Transform - Dominant Cycle Phase.

**Description**


**Inputs**


**Formula**



#### HT_PHASOR: Hilbert Transform - Phasor Components.

**Description**


**Inputs**


**Formula**



#### HT_SINE: Hilbert Transform - SineWave.

**Description**


**Inputs**


**Formula**



#### HT_TRENDMODE: Hilbert Transform - Trend vs. Cycle Mode.

**Description**


**Inputs**


**Formula**




---

### Pattern Recognition (图形识别)

#### CDL2CROWS: Two Crows. A bearish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3BLACKCROWS: Three Black Crows. A bearish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3INSIDE: Three Inside Up/Down. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3LINESTRIKE: Three-Line Strike. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3OUTSIDE: Three Outside Up/Down. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3STARSINSOUTH: Three Stars In The South. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDL3WHITESOLDIERS: Three Advancing White Soldiers. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**



#### CDLABANDONEDBABY: Abandoned Baby. A bullish reversal pattern.

**Description**


**Inputs**


**Formula**




---

### Statistic Functions (统计函数)

#### BETA: Beta Coefficient.

**Description**


**Inputs**


**Formula**



#### CORREL: Pearson Correlation.

**Description**


**Inputs**


**Formula**



#### LINEARREG: Linear Regression.

**Description**


**Inputs**


**Formula**



#### LINEARREG_ANGLE: Linear Regression Angle.

**Description**


**Inputs**


**Formula**



#### LINEARREG_INTERCEPT: Linear Regression Intercept.

**Description**


**Inputs**


**Formula**



#### LINEARREG_SLOPE: Linear Regression Slope.

**Description**


**Inputs**


**Formula**



#### STDDEV: Standard Deviation.

**Description**


**Inputs**


**Formula**



#### TSF: Time Series Forecast.

**Description**


**Inputs**


**Formula**



#### VAR: Variance.

**Description**


**Inputs**


**Formula**



