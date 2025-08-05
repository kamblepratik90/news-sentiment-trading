import pandas as pd
from data_fetcher.news_api import NewsAPIFetcher
import os
from dotenv import load_dotenv

def main():
    """
    Main function to fetch news data for a company
    """
    load_dotenv()
    
    # Get configuration from environment variables
    company_name = os.getenv('COMPANY_NAME', 'Reliance Industries')
    
    try:
        # Initialize the news fetcher
        news_fetcher = NewsAPIFetcher()
        
        print(f"Fetching news articles for: {company_name}")
        
        # Fetch articles
        df = news_fetcher.fetch_company_news(
            company_name=company_name,
            max_articles=100,
            days_back=30  # Look back 30 days for more articles
        )
        
        if not df.empty:
            # Display basic statistics
            print(f"\nArticles fetched: {len(df)}")
            print(f"Date range: {df['published_at'].min()} to {df['published_at'].max()}")
            print(f"Unique sources: {df['source'].nunique()}")
            
            # Display first few articles
            print("\nFirst 3 articles:")
            for idx, row in df.head(3).iterrows():
                print(f"\n{idx + 1}. {row['title']}")
                print(f"   Source: {row['source']}")
                print(f"   Date: {row['published_at']}")
                print(f"   Description: {row['description'][:100]}...")
            
            # Save to CSV
            filepath = news_fetcher.save_to_csv(df)
            print(f"\nData saved successfully to {filepath}")
            
        else:
            print("No articles found for the specified company.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()