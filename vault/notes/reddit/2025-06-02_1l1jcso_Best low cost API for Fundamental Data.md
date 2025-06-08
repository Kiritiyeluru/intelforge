---
source: reddit
subreddit: algotrading
date: 2025-06-02T19:54:19
tags: ['trading']
content_hash: d153a765a29a4cc2
author: DustinKli
score: 34
url: https://reddit.com/r/algotrading/comments/1l1jcso/best_low_cost_api_for_fundamental_data/
post_id: 1l1jcso
---

# Best low cost API for Fundamental Data

I used to use Financial Modeling Prep (FMP) but cancelled my subscription when they decided to rise the price of the data I was using and made many data points part of a higher cost subscription.

I am looking for a reliable alternative to FMP that has all of the same data as FMP. Ideally I would like to pay no more than $50 a month for the data.

I use the API in Google Sheets so it would need to be something that could integrate with Sheets.

The data I need is normalized fundamental data going back at least 10 years (earnings reports, etc.), historic price and volume data, insider trading data, news mentions, options data would be nice, ideally basic economic data, etc.

Does anyone have any suggestions that you have used and can personally vouch for?

## Comments

### Comment 1 (Score: 10)

**Author:** u/na85

Can't you get all the fundamentals for free from scraping EDGAR and then computing the ratios yourself?

### Comment 2 (Score: 4)

**Author:** u/heyjagoff

If you're worried about small increase in 50 per month data cost, you're in the wrong business

### Comment 3 (Score: 2)

**Author:** u/funkinaround

[https://www.dolthub.com/repositories/post-no-preference/earnings](https://www.dolthub.com/repositories/post-no-preference/earnings) has 10 years ish of data for annual and quarterly financial statements. It also has earnings calendar info and analyst estimates.

[https://www.dolthub.com/repositories/post-no-preference/stocks](https://www.dolthub.com/repositories/post-no-preference/stocks) has 10+ years of data for EOD stock prices and volumes. It also has dividends and splits.

[https://www.dolthub.com/repositories/post-no-preference/options](https://www.dolthub.com/repositories/post-no-preference/options) has 5 ish years of data for options with varying EOD frequencies (older data once a week. newer data daily). It also has historcial variance vs implied vol data.

Here's an article about integrating dolt in Google Sheets: [https://www.dolthub.com/blog/2023-09-15-dolt-google-sheets/](https://www.dolthub.com/blog/2023-09-15-dolt-google-sheets/)

## Source

- **Reddit Post:** [Best low cost API for Fundamental Data](https://reddit.com/r/algotrading/comments/1l1jcso/best_low_cost_api_for_fundamental_data/)
- **Subreddit:** r/algotrading
- **Author:** u/DustinKli
- **Score:** 34 upvotes
