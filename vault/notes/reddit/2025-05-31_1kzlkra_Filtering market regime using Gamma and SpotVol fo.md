---
source: reddit
subreddit: algotrading
date: 2025-05-31T07:18:43
tags: ['strategy']
content_hash: 7bd7493537275ff8
author: RedditLovingSun
score: 70
url: https://reddit.com/r/algotrading/comments/1kzlkra/filtering_market_regime_using_gamma_and_spotvol/
post_id: 1kzlkra
---

# Filtering market regime using Gamma and SpotVol for Mean Reversion

I'm working on a scalping strategy and finding that works well most days but performs so poorly on those relentless rally/crash days that it wipes out the profits. So in attempting to learn about and filter those regimes I tried a few things and thought i'd share for any thoughts.

\- Looking at QQQ dataset 5min candles from the last year, with gamma and spotvol index values  
\- [CBOE:GAMMA](https://cdn.cboe.com/resources/indices/documents/GAMMA_Methodology.pdf) index: "is a total return index designed to express the performance of a delta hedged portfolio of the five shortest-dated SP500 Index weekly straddles (SPXW) established daily and held to maturity."

\- [CBOE:SPOTVOL](https://cdn.cboe.com/api/global/us_indices/governance/Cboe_SnP_500_Spot_Volatility_Index_Methodology.pdf) index: "aims to provide a jump-robust, unbiased estimator of S&P 500 spot volatility. The Index attempts to minimize the upward bias in the Black-Scholes implied volatility (BSIV) and Cboe Volatility Index (VIX) that is attributable to the volatility risk premium"

\- Classifying High vs Low Gamma/Spotvol by measuring if the average value in the first 30min is above or below the median (of previous days avg first 30min)

Testing a basic ema crossover (trend following) stategy vs a basic RSI (mean reversion):

Return by Regime:

Regime	EMA	RSI

HH	0.3660	0.4800

HL	0.4048	0.4717

LH	0.3759	0.5000

LL	0.3818	0.4476



Win Rate by Regime:

Regime	EMA	RSI

HH	0.5118	0.5827

HL	0.5417	0.5227

LH	0.5000	0.5000

LL	0.5192	0.5435

Sample sizes are small so take with a grain of salt but this was confusing as i'd expect trend following to do better on high gamma volatile days and mean reversion better on low gamma calmer days. But adjusting my mean reversion strategy to only higher gamma days does slightly improve the WR and profit factor so seems promising but will keep exploring.

## Comments

### Comment 1 (Score: 7)

**Author:** u/smuhamm4

Geez! I wish I knew what I was looking at. I use spot gamma for intraday trading but what is this showing?

### Comment 2 (Score: 5)

**Author:** u/TheESportsGuy

Dealers hedge positive gamma by buying low and selling high*. Read about gamma scalping and try it yourself by buying a short dated straddle.

It's vol compressing...

### Comment 3 (Score: 2)

**Author:** u/blindsipher

This is the juicy data and back testing I love to see on this form

### Comment 4 (Score: 2)

**Author:** u/BrandNewYear

Very nice write up thanks for sharing

### Comment 5 (Score: 2)

**Author:** u/blasternaut007

Which computer are you using to run these? Windows or mac?

### Comment 6 (Score: 7)

**Author:** u/RedditLovingSun

I hear good things about spot gamma! this is slightly different but "GAMMA" and "SPOTVOL" are viewable on tradingview if you wanna take a look, they're indexes like the VIX.

If i was to oversimplify i'd say spotvol is like the VIX but for daily 0dte options and a much more short term measure of how "overpriced" options are.   
  
And gamma tracks how much buying a call and put at open would profit throughout the day (it's delta neutral so it would only profit off gamma if there's bigger moves than expected, or lose to theta if it's a calm day).

So i'm just seeing if their values from the first 30min of the day (compared to past day's first 30min) can tell me if the rest of the day will be calmer or crazier so I know when to avoid my mean reversion strategy.

### Comment 7 (Score: 4)

**Author:** u/RedditLovingSun

I see, so you're saying by the time i detect high gamma it's too late and it's already compressing? That would explain why i'm seeing mean reversion do better on days that start with high relative gamma.

### Comment 8 (Score: 2)

**Author:** u/The-Dumb-Questions

> It's vol compressing...

Or vol increasing :)

## Source

- **Reddit Post:** [Filtering market regime using Gamma and SpotVol for Mean Reversion](https://reddit.com/r/algotrading/comments/1kzlkra/filtering_market_regime_using_gamma_and_spotvol/)
- **Subreddit:** r/algotrading
- **Author:** u/RedditLovingSun
- **Score:** 70 upvotes
