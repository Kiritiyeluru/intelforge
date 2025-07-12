---
source: reddit
subreddit: algotrading
date: 2025-06-03T04:06:49
tags: ['algorithm']
content_hash: 97b0540d152a1b5b
author: M4RZ4L
score: 16
url: https://reddit.com/r/algotrading/comments/1l1vwkf/multiple_strategies_in_a_single_algorithm/
post_id: 1l1vwkf
---

# Multiple strategies in a single algorithm

I don't have much experience in this and just yesterday reading a post I realised that in the same algorithm there are people who have several strategies.

I have done some research on this but I still have some doubts.

If there are buy and sell trades at the same time you can go over the rules of a firm and get your account removed, right? The solution is to put together buy and sell strategies?

Do the signatures prohibit this? Do they limit the number of strategies?

I was thinking of compiling 50 gold buying strategies with an annual % higher than 2% and a DD lower than 0.5%, I think it would not cost me much work and less if I divide it between two with a friend. 
Do you think this is feasible?

Thank you all, I would appreciate an explanation of your answer, it would help me to learn more and faster.

## Comments

### Comment 1 (Score: 16)

**Author:** u/Glst0rm

My approach is to have every variation of my strategy in the same script (NinjaTrader file) to ease development. I have dozens of parameters and a careful structure to allow me to enable each strategy with settings for each future I trade. This is a joy for backtesting as I can create dozens of variations and work within one simple-ish script.

I run each strategy separately, long and short, for each future, and use separate sim accounts within my platform. This is done for easy stats gathering (I upload everything into tradersync and can run reports based on the portfolio.

For strategies that are running live (versus sim, or paper trade) I use a trade copier to copy the entry and exit orders from the sim "leader" accounts. This lets me decide and control sizing and scaling in a more controlled way (I might trade copy 3 micros for 1 mini to my cash account).

This "single script, separate bots" approach \*has\* created challenges  
\- Overleverage ... I might be long NQ, ES, and RTY off the same pullback entry.  
\- Long/Short the same symbol - this will wind up closing the prior trade, leaving me with jagged orders or a partial trade. I have a tool that flattens trades with mismatching targets/stops that cleans these up. This sucks, but the "leader" account still gets the trade so I can track metrics. I just miss the actual trade in my live account.

The trade copying and auto-flatten features of my platform prevent me form being long and short at the same time, breaking my broker's rules.

Bonus tip ... you can be long NQ and short MNQ and not break rules.

### Comment 2 (Score: 3)

**Author:** u/thelucky10079

Has a friend that did this.  Ran multiple strategies with the end result being if 5 go long and 12 go short he only sells 7.

End result being positive slippage on the net position vs the individual strategies execution.

### Comment 3 (Score: 2)

**Author:** u/na85

>If there are buy and sell trades at the same time you can go over the rules of a firm and get your account removed, right?

I'm not sure what you're describing but generally brokers make their money on commissions and fees, so they don't usually care how often you trade.  There are limits though:

1.  Broker APIs have pacing limitations, like 10 requests/second for a particular endpoint.  Going over this limit will not cause your account to be removed.
2.  Regulatory limits depending on jurisdiction, for example US Pattern Day Trader limits.  Exceeding this limit might get your account frozen but will not cause it to be removed.

>I was thinking of compiling 50 gold buying strategies with an annual % higher than 2% and a DD lower than 0.5%, I think it would not cost me much work and less if I divide it between two with a friend. Do you think this is feasible?

You have 50 different strategies to buy gold?

I think there's a terminology mismatch.  What do you mean when you write "strategy"?

### Comment 4 (Score: 2)

**Author:** u/Phunk_Nugget

I combine multiple signal models into one running strategy.  The strategy level sees all the signals at a point in time and exits the market if the signals are mixed sides and chooses which model to trade if multiple signals in the same direction.  Ideally you choose uncorrelated signals, but that can also lead to uncorrelated drawdowns.  So while you might increase your profits you can also easily increase your losses if not careful when running multiple strategies./models.

### Comment 5 (Score: 2)

**Author:** u/Skytwins14

When you have buy and sell orders at the same time make sure that they are limit orders where the price of the sell is higher than the price of the buy. Otherwise this can result in Wash Trading where you could end up with problems.

How to manage different strategies at the same time? There are few ways to incorporate them.

1. Lock an asset so when a position is open only the strategy that opened it can close it again.
2. When two or more strategies contradict each other then cancel all orders and close the position.
3. Have weights for each strategy and calculate a position size from the score generated.

I personally use option 3 that my algorithm uses to determine the amount to buy or sell for each stock.

### Comment 6 (Score: 2)

**Author:** u/LowBetaBeaver

You’re concern seems to be related to self tradinng; your broker should prevent this, but you don’t want to do it anyway because you incur fees.  What you want to do is called internalization:

Strat 1 is long 3, strat 2 want to short 1, so you want your portfolio to be long 2.  

What you want to do is add a layer between your strategies and the broker that takes signals and keeps track of your net portfolio (net of trades), and have it adjust your actual position based on where you theoretically want to be.  This will help keep your trade costs down while getting the exposure you mean to have.  You should still keep track of your strategy-level performance on your side though.

### Comment 7 (Score: 2)

**Author:** u/jawanda

Super interesting strategy, appreciate you sharing it.

## Source

- **Reddit Post:** [Multiple strategies in a single algorithm](https://reddit.com/r/algotrading/comments/1l1vwkf/multiple_strategies_in_a_single_algorithm/)
- **Subreddit:** r/algotrading
- **Author:** u/M4RZ4L
- **Score:** 16 upvotes
