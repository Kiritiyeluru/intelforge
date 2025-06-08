---
source: reddit
subreddit: algotrading
date: 2025-06-06T15:05:12
tags: ['backtest', 'trading']
content_hash: d33808103e464982
author: ExcuseAccomplished97
score: 166
url: https://reddit.com/r/algotrading/comments/1l4o8jg/ive_built_a_backtesting_platform_for_myself_i/
post_id: 1l4o8jg
---

# I've built a backtesting platform for myself. I share now.

Hi there!

It's been a while since I [posted](https://www.reddit.com/r/algotrading/comments/1jkx0xi/im_making_a_backtesting_ide_extension_need_your/) about a private project, and many of you showed interest and gave me valuable feedback. It was incredibly helpful for organizing the project plan. Thanks! When I shared a preview, I promised that I would open source the project once it was finished. Now, I think I can finally share it! (Though it's still in the initial stage.)

This is a plugin that allows you to backtest directly in [Visual Studio Code](https://code.visualstudio.com/). You can write backtest strategies with full IDE support (IDE or not IDE, depends on you), download price data from various exchanges, easily adjust backtest settings through an arranged interface, and view backtest results in a concise, organized format.

[Backtest Setting](https://preview.redd.it/ifwu2gkmw95f1.png?width=2770&format=png&auto=webp&s=8f285c543881fe3badab145dd14dd9173f1d332c)

[Backtest Result ](https://preview.redd.it/tdz1xyznw95f1.png?width=2770&format=png&auto=webp&s=9598d434321059af9e61f722a4d74c517ae7ea19)

Currently, the plugin has integration with **Backtrader** and **VectorBT** for setting backtest options and recording results. Beyond these two engines, you can use any other Python backtesting engine by outputting results in our standardized format.

As someone who uses this tool extensively, I know there's still a lot to develop. I'm planning to expand support to more markets like stocks and forex, include additional backtesting engines based on further requests. If you have specific requests or suggestions, please leave a comment. Your feedback has been invaluable so far!

VSC MarketPlace: [https://marketplace.visualstudio.com/items?itemName=woung717.backtest-manager](https://marketplace.visualstudio.com/items?itemName=woung717.backtest-manager)

Github: [https://github.com/woung717/backtest-manager-vscode](https://github.com/woung717/backtest-manager-vscode)

Let's make some profit!

## Comments

### Comment 1 (Score: 15)

**Author:** u/1mmortalNPC

Great work bro, can it also plot things on chart like boxes, lines, etc?

### Comment 2 (Score: 5)

**Author:** u/omnibubra

Built-from-scratch backtesting is the only way to really trust your curve. Curious how you handle slippage and tick resolution?

### Comment 3 (Score: 5)

**Author:** u/Money_Horror_2899

Kudos on the open-source project :) Great value there!

### Comment 4 (Score: 3)

**Author:** u/Chance_Reputation895

Looks great, gonna check it out!

### Comment 5 (Score: 3)

**Author:** u/UL_Paper

That's awesome! For a long time I have dreamt of a backtesting setup (with graphs) directly in vscode! Do you have a feature to save backtest results as well?

### Comment 6 (Score: 6)

**Author:** u/growbell_social

Congrats on shipping! The hardest part is getting that last mile out the door.

### Comment 7 (Score: 2)

**Author:** u/Impressive-Ad-5892

Still learning 🙂 I hope I get something important from it 👌🏼

### Comment 8 (Score: 2)

**Author:** u/GrandSeperatedTheory

Are all of the backtests just time series analysis-based. With regards to TCA how do you handle commission, slipage, borrow rate, bid ask etc. With regards to risk management and port opt how do handle rebal, optimizers, vol targets. 

Does the backtester put more emphasis on the TSA played backed returns or the port stats, like orthogonalization of returns & risk factor loadings.

### Comment 9 (Score: 2)

**Author:** u/deeznutzgottemha

Good work

### Comment 10 (Score: 2)

**Author:** u/benevolent001

Is there example where I can use my own data from database ?

## Source

- **Reddit Post:** [I've built a backtesting platform for myself. I share now.](https://reddit.com/r/algotrading/comments/1l4o8jg/ive_built_a_backtesting_platform_for_myself_i/)
- **Subreddit:** r/algotrading
- **Author:** u/ExcuseAccomplished97
- **Score:** 166 upvotes
