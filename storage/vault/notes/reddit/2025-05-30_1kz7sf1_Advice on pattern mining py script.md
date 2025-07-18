---
source: reddit
subreddit: algotrading
date: 2025-05-30T21:24:56
tags: ['strategy', 'indicator']
content_hash: c6a3d9dbd14628bf
author: XtianS
score: 6
url: https://reddit.com/r/algotrading/comments/1kz7sf1/advice_on_pattern_mining_py_script/
post_id: 1kz7sf1
---

# Advice on pattern mining py script

I'm not sure if this is the right place for this. I'm looking for advice on the general approach of this type of scan/search. I've built a number of code blocks that look at relatively simple aspects like price changes over time, volatility, volume, various technical indicators. It scans historical price activity looking for statistically meaningful patterns, comparing the agnostic mean return over defined horizons against the identified "signal." Output example below.

https://preview.redd.it/anerltcfxx3f1.png?width=1304&format=png&auto=webp&s=ead4c297493f05fccce57cb005a6218e26cdf63e

These aren't meant to be tradeable signals in and of themselves, but I'm looking at accumulating dozens or hundreds of high quality patterns that might inform a broader strategy.

In this specific example, this is looking at yang-zhang volatility changes in the underlying over specific time frames.

Looking for specifics on how the specific metrics I'm looking at might be flawed or if I'm missing something that should be factored in. For example, Is there an assessment metric that I should include here? Is there a fundamental flaw in this approach? Are there metrics I'm looking at that are meaningless in this context?

I can provide any actual py logic as needed.

## Comments

### Comment 1 (Score: 2)

**Author:** u/thenoisemanthenoise

I don't think any of those assessments are useless or wrong, I just can't put together what's your end goal here.  You want to create a custom indicator to signal a LONG buy?

### Comment 2 (Score: 2)

**Author:** u/Automatic_Ad_4667

Your challenge will be discerning signal from noise - you need some out of sample element 

### Comment 3 (Score: 2)

**Author:** u/XtianS

I'm looking for relatively simple patterns that might provide some statistical edge over the average. Its something I could potentially train a more complex model with later, but just trying to keep it really simple for now.

### Comment 4 (Score: 2)

**Author:** u/Automatic_Ad_4667

Probably won't save you. Try data mining candle stick patterns you'll be amazed at what you can find 

### Comment 5 (Score: 2)

**Author:** u/Automatic_Ad_4667

Use large language models like everyone else 

## Source

- **Reddit Post:** [Advice on pattern mining py script](https://reddit.com/r/algotrading/comments/1kz7sf1/advice_on_pattern_mining_py_script/)
- **Subreddit:** r/algotrading
- **Author:** u/XtianS
- **Score:** 6 upvotes
