---
source: reddit
subreddit: algotrading
date: 2025-06-03T14:21:35
tags: ['trading']
content_hash: 59554fb70d69efca
author: Throwaway-3720
score: 24
url: https://reddit.com/r/algotrading/comments/1l26ycd/getting_started_with_quantconnect/
post_id: 1l26ycd
---

# Getting started with QuantConnect

Hi, I'm a highschooler from the bay looking to get into algotrading this summer, I have a fair amount of experience in the math and physics olympiads (USAMO/USAPhO) and am particularly interested in Markov Models (specifically Hidden Markov Models) for price prediction. I'm looking to build on some previous research in that area.

Is there any solid free software for getting started with the programming aspect or should quantconnect be just fine (it seems to be a widely reccommended one)? Additionally, are there any other resources that would be good for getting started as a somewhat rookie.

Thanks.

## Comments

### Comment 1 (Score: 14)

**Author:** u/Tomoshen

I found QuantConnect to be a bit intense when I was just starteing out. I went that route at first but ended up switching to something more visual while learning. Stumbled on what seems like a well kept secret called Strategix Trading that lets you piece together strategies without code. You still get deep control over entry/exit logic, but it's just way more visual. It’s helped me wrap my head around how to structure ideas before writing actual scripts and was an instant dopamine hit because I could see performance metrics spelled out for me.

### Comment 2 (Score: 38)

**Author:** u/Epsilon_ride

You might get bad advice from this sub.

This sub is mostly unsuccessful hobbyists - people who cannot get professional jobs in the field and also generally can't make money solo.

r/quant is full of people who are successful and work in the field. If you are great at math and physics you could be on track for a quant career eventually (if that's what appeals to you).

Re quantconnect - Have a play around if you like, but some of the tutorials etc might be sending you down the wrong path. I'd look look at kaggle to see how machine learning models work and see if you can apply any of them to financial data, have a look at nautilus and hummingbot. Whatever you do - try to boost your skills and technical ability.

re markov models - just download crypto data and start coding up existing research in jupyter notebooks

### Comment 3 (Score: 3)

**Author:** u/StationImmediate530

Python is free - my recomendation is to try and replicate an article that you liked. Data is widely available (Yahoo Finance has got daily ohlc to download). If you re objective is to break in as a summer intern, expect a possibly different answer. Good luck

### Comment 4 (Score: 2)

**Author:** u/thegratefulshread

Lmao. Using hmm for price prediction not only introduces a huge black box issue but it’s a super noob method of using it.

We want to try to predict stationary data.  Not un stationary like price data.

Look into statistical arbitrage, correlation / cointegration test and try to make a trading script from that.

Trying to predict shit with a free easy to access library/ model like hmm will not generate alpha.

Research papers are just meant to show the theory not actual alpha generation methods.

At that point just replicate the papers from arxiv.org

## Source

- **Reddit Post:** [Getting started with QuantConnect](https://reddit.com/r/algotrading/comments/1l26ycd/getting_started_with_quantconnect/)
- **Subreddit:** r/algotrading
- **Author:** u/Throwaway-3720
- **Score:** 24 upvotes
