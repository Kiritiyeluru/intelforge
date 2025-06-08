---
source: reddit
subreddit: algotrading
date: 2025-06-01T16:58:41
tags: ['strategy', 'trading', 'indicator']
content_hash: 422ad2b8e825b320
author: Old-Syllabub5927
score: 15
url: https://reddit.com/r/algotrading/comments/1l0mpga/i_need_your_opinion/
post_id: 1l0mpga
---

# I need your opinion

Hi, I have been trying with regular trading and I am loosing hope. Do you think algo trading is a better approach?

I am an engineer, with some experience in ML, but I am not sure about the real feasibility of the system. Is it actually possible to get some, even if small, positive returns completely automating? I was thinking of training an AI model to recognise patterns in the short time frame, just “predicting” the next candle based on N previous candles. Shouldn’t be hard to code but I feel like it won’t work. Any tips/experience?

Edit: If I am right, ML should be able to find patterns or high probability setups without any real inputted strategy. Instead of working with 103829 indicators, it should be able to build its own. I was thinking of VAE+regressor to order the latent space. And use the regressor to output a probability 0-1 for uptrend, downtrend and consolidation or sth similar.

No need to apply any strategy or think, like building and indicator on steroids.

## Comments

### Comment 1 (Score: 26)

**Author:** u/as0003

No

### Comment 2 (Score: 17)

**Author:** u/DenisWestVS

Listen to Dr. Ernest Chan  
He is a well-deserved specialist in machine learning and algotrader at the same time. His opinion is not, at present, AI is not able to predict moving of the price.

### Comment 3 (Score: 21)

**Author:** u/Yocurt

ML will not find patterns by itself from candlesticks (too much noise, can’t generalize well).


A much better approach for using ml is to have an underlying strategy that has an existing edge, and train a model on the results of that strategy. This means the labels you train on could be either the win / loss outcomes of each trade (binary classification, usually the easiest), the pnl distribution, or any metric you want, but some are definitely better. The goal is for the model to AMPLIFY that existing edge. 


Finding an edge -> ml bad

Improving an existing edge -> ml good


You need to use a robust cross validation method and be 100% sure your pipeline has zero data leakage, since you will be training and testing on your historical results. 


This method can improve your win rate (if that’s what you’re optimizing for) by a few %, which can be huge. And from my experience the risk adjusted returns get the biggest boost - it basically is attempting to filter out more bad trades than good trades which really helps reduce your drawdowns. 


It’s called meta labeling, the book Advances in Financial Machine Learning goes into more detail about all of this if you’re interested, I couldn’t possibly cover it all here but this is the idea.

### Comment 4 (Score: 7)

**Author:** u/SeagullMan2

You should try this. It won't work. But you might learn something that leads to a future algo that does work.

### Comment 5 (Score: 6)

**Author:** u/rodneyt314

I've been thinking of and working towards this way for about a year myself. I don't have the answer yet, but here's just some ramblings of what I've seen and been up to on this. I have a script running right now that is applying adjustments to minute level intraday historical data for the last 20 years that I got from Polygon dot io. I plan on using that in Amibroker to backtest some ideas I've gotten from Joe Rabil's Trend and Momentum course. He has a lot of YT videos, is on StockCharts YT, and has a pretty cheap, fairly short book to read on that which gives a fair amount of detail too. This is all manual, but the course covers trade and money management with recommendations on stops and exits and has a template worksheet to track everything. I really like the idea of multiple timeframes, but that seems like it's really hard to properly keep all that in your head unless you can fully focus on it even after a lot of practice. Which means it seems like a great use case for an algorithm, and hopefully ML. I did a good surface level learning of the course, but definitely want to do a deep study on it. I also have Jansen's Packt book "Machine Learning for Algorithmic Trading", which is all Python. I've read some parts in it about features and alpha factors and there's sections about backtesting and portfolio management, it seems pretty complete. Also, concretumgroup dot com slash papers has several thought provoking and really good sounding ideas. I also have MATLAB, the perpetual home license def isn't free but it's not so bad either, and it has good ML & AI packages that I want to use for this eventually. I didn't get it for just this, also want another tool on my resume. Search for the Mathworks blog "Deep Learning in Quantitative Finance: Transformer Networks for Time Series Prediction" (when the site is available again!). That's only a 'basic' example and just to demonstrate the workflow, but sure seems like a good base. It seems like it follows pretty well but doesn't predict well (I used real SPY data, and then duh! I said to myself). But it's also just using the previous 30 days of raw closing data at every step, I'd really like to see how it performs with several alpha factors included. And options' gamma exposure data may be good to look at, just found Geeks of Finance YT channel about that. And I'd think it's also a good idea to find a way to factor in macro level data in somehow, maybe lower stops and higher exits in a long term bull market, the opposite in higher volatility timeframes? I've been watching the Thoughtful Money, 42 Macro, and Joseph Wang on YT for macro. And then how can we incorporate sentiment analysis too? One of the reasons I'm subbed to Polygon dot io is it has news article summaries and sentiment scores in it's REST API. I used the advanced plan one month to get the data and have been on starter since. Can we feed the titles/summaries into ChatGPT's API and get a "this is likely positive/negative for the stock/market" response that's reasonably reliable? There's definitely a lot to all this. I wish you good luck!

### Comment 6 (Score: 3)

**Author:** u/Playful-Chef7492

If emotional trading is your Achilles heel then yes an ATS would help avoid all the timing and consistency aspects of a solid trading approach. If you’re new to the ATS space just get ready to dive down the rabbit hole. It’s very difficult (but not impossible) to get alpha from an ATS. If you are an engineer then you know about rigorous testing. I would recommend planning not just your approach but the different aspects of the system before coding anything. A system like this gets complex very quickly even without a complex trading strategy. Therefore I would start with a really simple strategy that you can build layers on top of. For example if you want to use predictive ML for entry signaling make sure you isolate that code in a module and do just that until you get it working well. Put indicators in another module. Exit signaling in another, etc. bottom line is planning and organization is key to a successful system. hope this helps.

### Comment 7 (Score: 4)

**Author:** u/YellowCroc999

Yes you definitely could compute that







If you had a quantum computer

### Comment 8 (Score: 5)

**Author:** u/FKaria

Whatever signal you predict it will be very, very short-term, and your biggest problem will be execution costs and latency. I'll be like trying to compete in Formula1 race with a bicycle.

### Comment 9 (Score: 3)

**Author:** u/drguid

I seem to be doing OK keeping things extremely simple. I use single indicators, no AI and fixed percentage exits. Really it's all you need, at least at first.

Single indicators are also extremely fast to process. I mostly trade weekly setups but my most lucrative signal catches oversoldness at market opens, so I need to be quick sometimes.

### Comment 10 (Score: 3)

**Author:** u/nanakoab

Don’t try to predict the market it’s random - manage risk. Focus on building a model that helps you reduce risk

## Source

- **Reddit Post:** [I need your opinion](https://reddit.com/r/algotrading/comments/1l0mpga/i_need_your_opinion/)
- **Subreddit:** r/algotrading
- **Author:** u/Old-Syllabub5927
- **Score:** 15 upvotes
