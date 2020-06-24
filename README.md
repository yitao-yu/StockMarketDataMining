# StockMarketDataMining
China stock market data mining. Used stocks Data in 2018-2019. Explored several signals based on Moving Average and the idea of Order Flow. 

ShangHai-Shenzhen 300 Index is an Index that covers 300 stocks in China, whose total Market Cap is roughly 80% of the Shanghai-Shenzhen Market. 

To clarify, the components and weight of component of HS-300 I'm using is 2020-6 HS300 stocks, which is the only version I can find(even in tushare Pro). The HS300 stocks' component only changes twice a year and doesn't change its component too much. 

During 2018-2019, the HS300 Index in general experienced a decline, followed by a rise, then after April 2020, the Index experienced some tumbling. The experts claims that at the end of 2019, the market was ready to embrace a new round of rise, however the COVID-19 outbreak in Januaray,2020 changed that. Covering all three forms of trend, the time period is quite typical. (The fall, the rise, and the tumbling before another rise/fall)

# Data Dependency
I used several open data sources.

TuShare http://tushare.org/index.html

BaoStock www.baostock.com

AKShare https://www.akshare.xyz/zh_CN/latest/index.html

# Data Processing Tools
I definitely made use of popular libraries such as pandas, numpy and matplotlib.

I also used some library popular for stock market data.

TA-lib http://mrjbq7.github.io/ta-lib/

FPGrowth is performed using mlxtend implementation http://rasbt.github.io/mlxtend/user_guide/frequent_patterns/fpgrowth/

# FPMiningSignals
I made used of severl data dimensions from TA-lib, including several types of signals(EMA, DEMA) based on moving averages using different combination of Parameters(fast: 4,6,9; slow: 12, 26); Momentem Signals such as MACD(which is actually also based on Moving Average),STOCH and SAR. All was calculated using TA-lib. 

Of course all of those signals were designed to capture some trends, and most of them only were triggered when a rise or bounce is already happening. But will those trends lasts for a longer period, say 5 or 20 days, producing enough profit that is significantly different from tumbling of the market? Are they robust against tumbling(Noise in the price)? 

I performed FPGrowth(A Frequent Pattern Mining algorithm) on dataset(in forms of itemset data) of signals on those that has a future 5 day profit larger than 8 percent(which accounts for 6 percent of total data); dataset of signals that has a future 20 day gain larger than 20 percent; and data with no significant future gain in both period(That says, it includes those that have a lose). 

FPMining on NoGain dataset is performed with a lower frequent threshold, 0.1, while on Gain5 or Gain20 datasets, 0.3. 

All of those Frequent Itemsets(signals and combination of signals) in gain are Frequent on NoGain datasets. However, after I sorted the patterns using Precision, the top ten patterns improved accuracy by at least 2 percent(8%) than random guess(2%), which is bad, but not terrible if you assume the rest of the stocks are random walking. 

Precision is defined: 
Precision = TP/(TP+FP)

Are they Random walking though(Will the selection actually increase the frequency of significant loss?)? I later made a significant loss(5 day loss > 0.08) dataset and perform.

I find that all of the moving average signals from the pattern we mined above has a frequency difference larger than 5% in the loss5 itemset dataset than in the gain5 dataset. This apply to SAR as well, but not STOCH. The frequency difference is in favor of us if we use those signals to profit. 

This is not a complete justification but can give us some taste. It might suggests that we should make use of those signals and they might help us identify trends that will last for some period(5 days). 

Why is there such a high False Positive rate(FP) though? It might be that the signals based on moving average was triggered a lot in their most powerless situation: the tumbling. 

# Signals that were mined useful, consider use them together on stocks with clear trends.

EMA4-EMA12; EMA6-EMA12; EMA9-EMA12;EMA9-EMA26;SAR

# ExamineOrderFlow

The Idea of Order Flow is examined. 
I only have access to 2019(actually after 2018-12-12) tick data so that's all I used. 
The plan was to make a plot using hs300 data throughout 2019(x-axis is the porportion of days in a month that has a positive comittee; while y-axis is the percentage of increase in the next month)

The function took forever to run so I manually interrupt it after it finished roughly 15 stocks. The graph was not satisfying: No correlation at all. It is just two independent normal distributions. 

I later tried the 15 stocks that is currently weighted the most in HS300, each of them have a weight larger than 1%. The pattern shown was the same, two independent normal distribution.

This Data Dimension will not help us to capture a one month trend in the future. How much people are willing to bid in this month will not affect how the price will behave in the future month. 

Be aware that there's a sharp increase of the HS300 Index before April in 2019, while for the rest of year a tumbling. So that's the reason why the mean of increase is larger than 0, it's because the stock market throughout 2019 is not weak. 

# Done
I'm wrote a strategy on JoinQuant that will make use of those findings. I explored another use of Order Flow: Identify the prices where people bid the most in the last month, that's usually where most people find the price too low and see an opportunity. We might be able to find stocks that's more likely to rise by looking at current relative position of stock prices to those prices.

Results:(The blue line is the profit of my strategy, while the red one Index)

2018-2020.6: https://www.joinquant.com/view/community/detail/e2657a1cb8813f35b594965d7aca2f4f

2015-2017: https://www.joinquant.com/view/community/detail/2e25a9233015320e99b334e15fe86d26

Another Strategy(Strategy v2##THIS ONE BEATS THE INDEX！！):

2018.11-2020: https://www.joinquant.com/view/community/detail/526a35f9ef9bf0a9b05336d11b986dd3

# Claim
I'm not responsible for ANY loss caused by operation in any market according to any mined results that was mentioned here. 
This is a personal project a college student DID FOR FUN and NOT ANY guidance to ANY exchanger.

# License
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without rest riction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
