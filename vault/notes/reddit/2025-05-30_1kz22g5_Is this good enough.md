---
source: reddit
subreddit: algotrading
date: 2025-05-30T17:11:28
tags: ['strategy']
content_hash: e9c3c3135c57ec29
author: Accurate-Dinner53
score: 77
url: https://reddit.com/r/algotrading/comments/1kz22g5/is_this_good_enough/
post_id: 1kz22g5
---

# Is this good enough?

I tested my strategy on 500 stocks and I want to deploy it. The results seem good enough for me. Are there some details I missed here? How can I find out if I was just lucky?

The strategy basically just uses linear regression with a few very special features to predict price movement. I ran this test on a 80-20 split.

## Comments

### Comment 1 (Score: 19)

**Author:** u/diige

Add fee + slippage

### Comment 2 (Score: 11)

**Author:** u/JamesAQuintero

Did you develop this strategy while looking at 100% of the timeframe and then ran it on 20% of the stocks? Or did you develop this looking at 80% of the timeframe of 100% of the stocks, and then ran this analysis on the remaining 20% timeframe on 100% of the stocks? Plus how many trades is this?

### Comment 3 (Score: 7)

**Author:** u/Mitbadak

Need the duration, total returns and drawdown related metrics to see if the rewards are good enough.

And you need to check robustness which is far more important than performance stats.

### Comment 4 (Score: 7)

**Author:** u/Mistermeanour105

“Good enough” is subjective, you need to define how you’re going to apply this model, to which instruments, over what time horizon and for what desired annualised rate of RAR. Also what is the Sharpe/Sortino?

### Comment 5 (Score: 3)

**Author:** u/krymski

Meaningless. Just show the PnL curve vs benchmark plot on the test set only, and state the Sharpe of your strat Vs buy and hold sharpe

### Comment 6 (Score: 2)

**Author:** u/RadicalAlchemist

No, but it’s a great effort. You’re missing volatility and adjusted risk metrics. Get back to work.

### Comment 7 (Score: 2)

**Author:** u/kingvt

I think the strategy itself needs some work, I wouldn't really be comfortable with a marginal edge that might die to slippage

## Source

- **Reddit Post:** [Is this good enough?](https://reddit.com/r/algotrading/comments/1kz22g5/is_this_good_enough/)
- **Subreddit:** r/algotrading
- **Author:** u/Accurate-Dinner53
- **Score:** 77 upvotes
