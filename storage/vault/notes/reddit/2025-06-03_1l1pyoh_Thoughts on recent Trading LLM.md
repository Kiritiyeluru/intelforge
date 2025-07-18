---
source: reddit
subreddit: algotrading
date: 2025-06-03T00:10:31
tags: ['strategy', 'trading']
content_hash: f72980c52989f320
author: greyhairedcoder
score: 10
url: https://reddit.com/r/algotrading/comments/1l1pyoh/thoughts_on_recent_trading_llm/
post_id: 1l1pyoh
---

# Thoughts on recent Trading LLM?

An LLM has been created and taunted as a winning strategy.

Original paper:

https://arxiv.org/abs/2411.00782

Any quants / traders using this? Curious on what you think 🤔


## Comments

### Comment 1 (Score: 48)

**Author:** u/Exarctus

Probably bullshit. None of these results are easily verifiable since no code and poor description of architecture. Shitty paper.

### Comment 2 (Score: 8)

**Author:** u/Yocurt

This approach does seem to have some potential, at least compared to the other methods people typically try to use LLM’s for.

Their method is no different than giving an expert all of the available information about macro economic data, company fundamentals, news articles, and market data, and that human expert making an educated guess. (Except it’s spitting out what it THINKS an expert would say, *just to cover my butt for the replies*).

However, this would only work (I think, I only read the abstract) for more long term investing strategies. It’s more like investing in “good” businesses at good times in a macro sense.

I would definitely take the paper with a grain of salt, since 99% of papers like this are complete BS, I’m just saying the general idea makes sense.

Getting an LLM to discover an edge for a scalping/short term swings/daytrading strategy from pure market data, price action, is a whole different application, which absolutely no LLM can do yet (for now).

### Comment 3 (Score: 3)

**Author:** u/kokanee-fish

There's not enough detail here to know if their stated results are compelling. It's surprisingly difficult to create a backtesting process that doesn't introduce overfitting, lookahead bias, or optimistic executions. Usually, great test results are caused by an oversight in the testing process. But not always.

At a high level, though, the idea of assigning an LLM to each trading signal, and using another LLM to synthesize the signals into a decision, seems reasonable. I'm sure we'll see a lot of progress in this area.

### Comment 4 (Score: 3)

**Author:** u/v3ritas1989

I don't think LLMs are the right model for this.

### Comment 5 (Score: 7)

**Author:** u/nhcrawler1

People LLM  are LARGE LANGUAGE MODEL not data processing models.... LLM are not designed to proceed data just LANGUAGE

### Comment 6 (Score: 2)

**Author:** u/WhiskyWithRocks

So I have trying something similar and getting somewhat ok results. Somedays it gives me great trades and some days are flat to low negative.

I will post an earlier version of my prompt. If any one wants to play around with this can try it out, my current version is quite different from this but this could be a great starting point for someone.

I collect all relevant data and have a script that creates this prompt calls the open AI api every minute. Costs about $10-12ish a day in api costs.

Mid post edit : I got this error "This field must be under 10000 characters" so I'm forced to truncate the prompt. I'm redacting some market data to be under the limit.

Disclaimer: There is a lot more going on apart from just prompting, this alone will not suffice. I consider it like a final go / no go signal on my core signal. Sort of like removing myself from giving the green light and getting chatGPT to do so in order to be wholly automated. Still working on it, ping me in 15-30 days for an update if you want one.

**SORRY, CAN'T GET THE CODE BLOCK TO WORK PROPERLY. COPY PASTE IN A TEXT EDITOR TO READ PROPERLY**



⠀⠀⠀⠀⠀⠀⠀⠀You are an expert NIFTY intraday scalping assistant.
⠀⠀⠀⠀⠀⠀⠀⠀    Think deeply about what you recommend and recheck your conclusions.
⠀⠀⠀⠀⠀⠀⠀⠀Your job: recommend high-conviction, data-backed scalping trades for NIFTY (target: 7–10 trades per day of 30-100 points on NIFTY, win rate >60%). Only advise a trade if one direction is clearly dominant. All fields (option, index, SL, tgt) must be filled using the below data.

⠀⠀⠀⠀⠀⠀⠀⠀DATE: 2025-05-29
⠀⠀⠀⠀⠀⠀⠀⠀Current Index: 24759.55
⠀⠀⠀⠀⠀⠀⠀⠀India VIX: 16.8

⠀⠀⠀⠀⠀⠀⠀⠀-- LATEST 1m BARS (last 40) --
⠀⠀⠀⠀⠀⠀⠀⠀[1] t:2025-05-29 12:31, o:24750.75, h:24753.3, l:24748.65, c:24749.75, v:10125, ema20:24742.56, vwap:24786.44, ...
⠀⠀⠀⠀⠀⠀⠀⠀[40] t:2025-05-29 13:16, o:24756.0, h:24760.05, l:24748.5, c:24759.55, v:3375, ema20:24749.43, vwap:24777.03, ...

⠀⠀⠀⠀⠀⠀⠀⠀-- LATEST 15m BARS (last 10) --
⠀⠀⠀⠀⠀⠀⠀⠀[1] t:2025-05-29 11:00, o:24745.8, h:24756.5, l:24714.65, c:24723.55, ...
⠀⠀⠀⠀⠀⠀⠀⠀[10] t:2025-05-29 13:15, o:24760.35, h:24761.65, l:24748.5, c:24759.55, ...

⠀⠀⠀⠀⠀⠀⠀⠀-- LATEST 2h BARS (last 4) --
⠀⠀⠀⠀⠀⠀⠀⠀[1] t:2025-05-28 15:15, o:24749.5, h:24757.45, l:24740.05, c:24757.15, ...
⠀⠀⠀⠀⠀⠀⠀⠀[4] t:2025-05-29 13:15, o:24760.35, h:24761.65, l:24748.5, c:24759.55, ...

⠀⠀⠀⠀⠀⠀⠀⠀-- VOLUME PROFILE --
⠀⠀⠀⠀⠀⠀⠀⠀POC: 24755.6, VAH: 24886.2, VAL: 24717.6
⠀⠀⠀⠀⠀⠀⠀⠀Volume Profile (top 10 levels):
⠀⠀⠀⠀⠀⠀⠀⠀Price 24755.6: Vol 194775.0
⠀⠀⠀⠀⠀⠀⠀⠀...

⠀⠀⠀⠀⠀⠀⠀⠀-- OPTION CHAIN (summary, ATM, OI, key strikes) --
⠀⠀⠀⠀⠀⠀⠀⠀spot_price: 24759.05
⠀⠀⠀⠀⠀⠀⠀⠀total_call_open_interest: 295827600
⠀⠀⠀⠀⠀⠀⠀⠀total_put_open_interest: 181084350
⠀⠀⠀⠀⠀⠀⠀⠀open_interest_pcr: 0.61
⠀⠀⠀⠀⠀⠀⠀⠀avg_iv: 214.0
⠀⠀⠀⠀⠀⠀⠀⠀atm_strikes: call(24750.0, ltp:32.1, oi:17902425.0) | put(24750.0, ltp:34.9, oi:9150825.0)
⠀⠀⠀⠀⠀⠀⠀⠀...

⠀⠀⠀⠀⠀⠀⠀⠀-- STRUCTURE & LEVELS --
⠀⠀⠀⠀⠀⠀⠀⠀- Today's open: 24844.4
⠀⠀⠀⠀⠀⠀⠀⠀- Today's high: 24888.3
⠀⠀⠀⠀⠀⠀⠀⠀- Today's low: 24677.6
⠀⠀⠀⠀⠀⠀⠀⠀- Previous close: 24757.15
⠀⠀⠀⠀⠀⠀⠀⠀- VWAP: 24777.03
⠀⠀⠀⠀⠀⠀⠀⠀- Day summary:

⠀⠀⠀⠀⠀⠀⠀⠀Analyze all this data (1m, 15m, 2h, volume, regression values, VWAP, pivots, option chain, OI, VIX, structure, volume profile) and return ONLY ONE trade idea in this JSON:
⠀⠀⠀⠀⠀⠀⠀⠀[{"dir":"LONG|SHORT|WAIT", "entry":float, "sl":float, "tg":float, "why":string, "instrument":"NIFTY", "strike":int, "right":"CE|PE", "option_entry":float, "option_sl":float, "option_tg":float}]

⠀⠀⠀⠀⠀⠀⠀⠀REQUIREMENTS:
⠀⠀⠀⠀⠀⠀⠀⠀- Use [40] as latest bar for decision making.
⠀⠀⠀⠀⠀⠀⠀⠀- Think contextually with previous/next higher TFs.
⠀⠀⠀⠀⠀⠀⠀⠀- Use RSI (14), MACD (12,26,9), BB (20,2) in your judgment.
⠀⠀⠀⠀⠀⠀⠀⠀- Use >70% confidence trades only. If not confident, return WAIT.
⠀⠀⠀⠀⠀⠀⠀⠀- Consider mean reversion if RSI<32 or RSI>68 and supported.
⠀⠀⠀⠀⠀⠀⠀⠀- No trade unless you see alignment across factors.
⠀⠀⠀⠀⠀⠀⠀⠀- Option entry/SL/tgt from LTPs only, not assumptions.

⠀⠀⠀⠀⠀⠀⠀⠀You must also reply with a second JSON array called "summary_lines" exactly in this format:
⠀⠀⠀⠀⠀⠀⠀⠀"summary_lines": [
⠀⠀⠀⠀⠀⠀⠀⠀  {"dir": "LONG", "summary_line": "<40-char summary>", "confidence": <float 0-1>},
⠀⠀⠀⠀⠀⠀⠀⠀  {"dir": "SHORT", "summary_line": "<40-char summary>", "confidence": <float 0-1>},
⠀⠀⠀⠀⠀⠀⠀⠀  {"dir": "WAIT", "summary_line": "<40-char summary>", "confidence": <float 0-1>}
⠀⠀⠀⠀⠀⠀⠀⠀]

### Comment 7 (Score: 4)

**Author:** u/thegratefulshread

These papers make me realize fuck ai and llms. Literally pulling the fun out of finance.

## Source

- **Reddit Post:** [Thoughts on recent Trading LLM?](https://reddit.com/r/algotrading/comments/1l1pyoh/thoughts_on_recent_trading_llm/)
- **Subreddit:** r/algotrading
- **Author:** u/greyhairedcoder
- **Score:** 10 upvotes
