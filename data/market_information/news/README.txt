# Market News Data Directory

This directory contains financial news data, press releases, and other text-based market information that can be used for sentiment analysis and event-driven trading strategies.

## Contents

- Financial news articles
- Company press releases
- Earnings announcements
- Economic indicators news
- Market commentary

## File Naming Convention

Files are named according to the following patterns:

1. General news collections:
   - news_{DATE}.json
   - Example: news_20230315.json

2. Company-specific news:
   - news_{SYMBOL}_{DATE}.json
   - Example: news_AAPL_20230315.json

3. Earnings announcements:
   - earnings_{SYMBOL}_{QUARTER}_{YEAR}.json
   - Example: earnings_AAPL_Q1_2023.json

4. Economic indicators:
   - economic_{INDICATOR_TYPE}_{DATE}.json
   - Example: economic_CPI_20230315.json

## Data Format

News data is typically stored in JSON format with the following structure:

```json
[
  {
    "id": "unique_news_id",
    "title": "News headline",
    "source": "News source (e.g., Reuters, Bloomberg)",
    "url": "Original news URL",
    "published_at": "2023-03-15T14:30:00Z",
    "content": "Full news article text",
    "summary": "Brief summary of the article",
    "symbols": ["AAPL", "MSFT"],  // Related stock symbols
    "categories": ["Technology", "Earnings"],
    "sentiment": {
      "score": 0.75,  // -1 to 1 scale
      "label": "positive"
    }
  },
  // More news items...
]
```

## Processing Operations

News data may undergo the following processing:
- Text cleaning and normalization
- Entity extraction (company names, people, locations)
- Sentiment analysis
- Topic modeling
- Keyword extraction
- Relevance scoring

## Notes

- News data is typically collected from various sources via APIs or web scraping
- Sentiment analysis may be performed using NLP models
- News data can be linked to market movements for event studies
- Consider storage requirements as news data can grow large over time