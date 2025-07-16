---
source: reddit
subreddit: algotrading
date: 2025-06-03T17:43:46
tags: ['algorithm', 'trading']
content_hash: 29ae23859ce9ee80
author: M4TR1X_8
score: 16
url: https://reddit.com/r/algotrading/comments/1l2ab18/attempting_to_use_a_dynamic_fourier_series_like/
post_id: 1l2ab18
---

# Attempting to use a dynamic Fourier series like algorithm to model certain period of the stock market

Hey everyone, I am definitely a bit new to the aspect of trading as a whole, being mainly focused on pure mathematics. I am attempting to generate a way to model out certain smooth motions of the stock market, using a fourier series-like function which can adapt to dynamic changes.
It follows from using an FFT on a given time period on the market, creating a Discrete Fourier Series from it, with the Fourier coefficient weighted by e\^(alpha\*local drift) and the frequency component with a weightage incorporated of 1+local volatility\*beta, where alpha and beta are weights that can be optimised through learning. So far, I have tested it on Brownian motion sampling and will incorporate it to predict past financial data.
Is there any research that has been done on such models that utilise a weighted/modified discrete Fourier series? Do you recommend any adjustments to a beginner like me?
Where do you recommend I could go to learn more about trading from a pure mathematical perspective?
Any feedback and answers to the above is greatly appreciated


## Comments

### Comment 1 (Score: 9)

**Author:** u/Phunk_Nugget

John Ehler's did a lot of work with cycles in markets and applying DSP type of analysis to market data.  Cycle Analytics for Traders includes a chapter on Fourier transforms.  I would look to him for some ideas on applying the techniques to market data analysis.

### Comment 2 (Score: 2)

**Author:** u/starostise

I went on this path and found no useful publication.

What data are you using as input ?

A FFT is the very first step to build a machine learning algorithm and it won't work from candles or price data from aggregators. Use a list of transactions as input and find the right labelling to determine what was supplied and what was demanded.

Labelling is the trickiest part because it does not come from a mathematical formula. It will come from a deep conceptual thinking and intuition because there are flaws in how the law of supply and demand is commonly interpreted.

Then, you will have to explore the results by yourself. The finality being to track the shifts of the supply and the demand (there is an existing formula) because they are driving price movements.

Edit: few words

## Source

- **Reddit Post:** [Attempting to use a dynamic Fourier series like algorithm to model certain period of the stock market](https://reddit.com/r/algotrading/comments/1l2ab18/attempting_to_use_a_dynamic_fourier_series_like/)
- **Subreddit:** r/algotrading
- **Author:** u/M4TR1X_8
- **Score:** 16 upvotes
