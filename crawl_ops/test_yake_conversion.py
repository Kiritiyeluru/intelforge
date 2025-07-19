#!/usr/bin/env python3
"""
Quick test to compare YAKE vs KeyBERT keyword extraction quality
"""

import yake

# Test sample content
test_content = """
Technical analysis is essential for algorithmic trading strategies. 
RSI (Relative Strength Index) and MACD are popular momentum indicators. 
Bollinger Bands help identify overbought and oversold conditions.
Moving average crossovers generate buy and sell signals.
Risk management through position sizing and stop losses is crucial.
Backtesting validates strategy performance using historical data.
"""

# YAKE extractor
kw_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.7, top=5)

def test_yake_extraction():
    keywords = kw_extractor.extract_keywords(test_content)
    print("YAKE Keywords:")
    print(f"Raw output: {keywords}")
    for kw in keywords:
        print(f"  {kw}")
    
    # Extract just the keyword strings (first element is keyword, second is score)
    keyword_strings = [kw[0] for kw in keywords]
    print(f"\nExtracted keywords: {keyword_strings}")
    
    return keyword_strings

if __name__ == "__main__":
    test_yake_extraction()