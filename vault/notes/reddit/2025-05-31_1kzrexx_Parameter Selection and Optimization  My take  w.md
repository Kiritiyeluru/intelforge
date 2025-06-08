---
source: reddit
subreddit: algotrading
date: 2025-05-31T13:05:05
tags: ['strategy', 'backtest']
content_hash: 0dc4d580093baa15
author: SubjectFalse9166
score: 6
url: https://reddit.com/r/algotrading/comments/1kzrexx/parameter_selection_and_optimization_my_take/
post_id: 1kzrexx
---

# Parameter Selection and Optimization : My take , would love to hear yours as well.

To start of most of my strategies don't use parameters / overlays / filters they just run on their rules  
But some do - And i'd like to share the process of how i select which one's to use 

When i first started testing parameters i was completely lost , i wanted to test the ADX on my strategy what is the pNL on different ranges of the ADX and can i use the ADX to switch on and off the strategy 

The problem was there are so many time frames and so many look back periods   
I was at point where i have 50 backtests of 4 years each of different crypto coins on which i had to test at-least 5 time frames of ADX with like 3 different look back periods.   
50x4x5x3 = R.I.P  
My laptop and brain would get FRIED even thinking about this 

And over that i'd worry about overfitting and how to choose the right one. 

The ADX parameter later failed after lot of testing but i learnt some stuff   
By which i choose parameters in a much more efficient way for myself 

Since most of us just have one laptop and can't really run hardcore tests and optimize parameters.   
What i do is eyeball stuff. Just using my market knowledge

And how i see if parameters are right for my strategy or chuck them out is this :   
  
1. You form a base hypothesis of which parameter might work or why - can be done by looking a long periods of outperformance / underperformance/ flatlined on the equity curve   
OR studying the winners and losers from your backtest seeing what's common in them, write these points down  
  
2. If the parameter you choose is highly inconsistent throughout the backtest , i check 2-3 versions with varying TF and length and if the results are shit u throw them out  
  
3. If the parameter show's promise over the whole course of the backtest over different windows as mentioned in point 2 and ( is fractal )  
So suppose we're using a parameter of time frames 2H , 4H and 8H   
if over the whole course of the backtest each of the time frames has got similarities  then i arrive at a conclusion yeah something might be worth exploring here   
  
Another way i eyeball parameters windows to test is i check the average trade duration if my trades last for 12h in average in example and use's price data of only last few days suppose one week   
I test the parameters around that price data ( 3 days - 14 days )   
  
4. You walk forward with the parameters : suppose i've chosen a parameter which i right for my backtest and my in sample data is from 2000 to 2010 

4.1 : If one parameter shows significant results in all year's i just use them for my out of sample as well   
Suppose the parameter did good 8/10 years and is remaining fractal for all of those then i just run them with out of sample 

4.2 I use a rolling window , we test the results in 10 years , then we go from 2001 to 2011 and so on   
and i put a threshold on the parameter that its success rate has to be 7/10 years or so always 

If all the boxes tick and most importantly if i FEEL its right for my strategy i deploy them. 

  
This is how i do it 

I'd like to know how u all do it , or how i could make my approach better. 

## Comments

### Comment 1 (Score: 3)

**Author:** u/UL_Paper

What leads to the best results for me is:

1. Understanding your strategy and why it has edge
2. Define it's problems or areas of improvement
3. Research or resonate yourself to possible solutions
4. Visualize your solution using matplotlib and evaluate if the idea has any merit
5. If it shows merit, verify via backtests. 
6. With backtesting I usually run some optimization runs to crunch through a bunch of combos and visualize them. It can help, but I also test out things myself to learn better.

### Comment 2 (Score: 2)

**Author:** u/SubjectFalse9166

Didn’t u just summarise what I just said

## Source

- **Reddit Post:** [Parameter Selection and Optimization : My take , would love to hear yours as well.](https://reddit.com/r/algotrading/comments/1kzrexx/parameter_selection_and_optimization_my_take/)
- **Subreddit:** r/algotrading
- **Author:** u/SubjectFalse9166
- **Score:** 6 upvotes
