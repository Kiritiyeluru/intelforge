---
source: reddit
subreddit: algotrading
date: 2025-06-05T06:40:21
tags: ['strategy', 'backtest']
content_hash: 3ff2f973dced992f
author: blacklagoon7
score: 28
url: https://reddit.com/r/algotrading/comments/1l3mism/where_can_i_get_highres_historical_tick_data_for/
post_id: 1l3mism
---

# Where can I get high-res historical tick data for major stock index CFD's ?

Hi all,

I'm optimising a breakout strategy using an MT5 EA and need to do extensive backtesting on multiple stock indices like US500 (S&P500) and USTEC. It has a very aggressive trailing stop so I need high res tick data to backtest. My broker (IC Markets) only has a few months of high res data at any one time. I've tried downloading Dukascopy tick data from QuantDataManager for free but I have not found it to be reliable when comparing with the recent ICM broker supplied data.

I'm prepared to pay for the data if it's reliable, any recommendations?

## Comments

### Comment 1 (Score: 10)

**Author:** u/thegratefulshread

Okay good. 199 a month gets you databento data.  No cap onto the amount of tickers.  I personally am using it for analyzing over 9k stocks

### Comment 2 (Score: 4)

**Author:** u/Living-Ring2700

Databento

### Comment 3 (Score: 4)

**Author:** u/alphaQ314

If i understand correctly, CFDs are an OTC product, provided by your broker. They're the only ones who would have that data.

The recommendations in this thread point to data for the underlying, not the CFD itself.

### Comment 4 (Score: 3)

**Author:** u/meilaina

When in doubt, straight from the broker is king—CFDs are OTC anyway, so their data is the only “truth” for backtesting

### Comment 5 (Score: 2)

**Author:** u/Nydewien

Tick data is the lifeblood of algotrading; without it, strategies are just empty vessels

### Comment 6 (Score: 2)

**Author:** u/Mitbadak

not sure about CFDs, but you can get NQ/ES futures tick data from PortaraCQG going all the way back to inception, I believe.

If you don't need to go as far back, databento data starts at 2010-ish.

BTW, aren't CFD prices different from broker to broker?

## Source

- **Reddit Post:** [Where can I get high-res historical tick data for major stock index CFD's ?](https://reddit.com/r/algotrading/comments/1l3mism/where_can_i_get_highres_historical_tick_data_for/)
- **Subreddit:** r/algotrading
- **Author:** u/blacklagoon7
- **Score:** 28 upvotes
