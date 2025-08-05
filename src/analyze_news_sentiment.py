import pandas as pd
from data_fetcher.news_api import NewsAPIFetcher
from sentiment_analysis.analyzer import SentimentAnalyzer
from visualization.sentiment_charts import SentimentVisualizer
import os
from dotenv import load_dotenv

def main():
    """
    Main function to fetch news, analyze sentiment, and create visualizations
    """
    load_dotenv()
    
    # Get configuration
    company_name = os.getenv('COMPANY_NAME', 'Reliance Industries')
    
    try:
        # Step 1: Fetch news data
        print("=" * 70)
        print("STEP 1: FETCHING NEWS DATA")
        print("=" * 70)
        
        news_fetcher = NewsAPIFetcher()
        df = news_fetcher.fetch_company_news(
            company_name=company_name,
            max_articles=30,
            days_back=30
        )
        
        if df.empty:
            print("No articles found. Exiting...")
            return
        
        # Step 2: Comprehensive Sentiment Analysis
        print("\n" + "=" * 70)
        print("STEP 2: COMPREHENSIVE SENTIMENT ANALYSIS")
        print("=" * 70)
        
        sentiment_analyzer = SentimentAnalyzer()
        df_with_sentiment = sentiment_analyzer.analyze_dataframe_comprehensive(df)
        
        # Step 3: Create Visualizations
        print("\n" + "=" * 70)
        print("STEP 3: CREATING SENTIMENT VISUALIZATIONS")
        print("=" * 70)
        
        visualizer = SentimentVisualizer()
        
        # Create individual charts - let the visualizer handle the paths
        title_chart = visualizer.create_sentiment_bar_chart(
            df_with_sentiment, 
            'title_sentiment_label', 
            title=f'Title Sentiment Distribution - {company_name}'
        )
        
        if 'description_sentiment_label' in df_with_sentiment.columns:
            desc_chart = visualizer.create_sentiment_bar_chart(
                df_with_sentiment, 
                'description_sentiment_label', 
                title=f'Description Sentiment Distribution - {company_name}'
            )
        
        if 'combined_sentiment_label' in df_with_sentiment.columns:
            combined_chart = visualizer.create_sentiment_bar_chart(
                df_with_sentiment, 
                'combined_sentiment_label', 
                title=f'Combined Sentiment Distribution - {company_name}'
            )
        
        # Create comprehensive comparison chart
        comp_chart = visualizer.create_comprehensive_sentiment_chart(df_with_sentiment)
        
        # Create timeline chart if we have enough data points
        if len(df_with_sentiment) > 5:
            timeline_chart = visualizer.create_sentiment_timeline(
                df_with_sentiment,
                'combined_sentiment_label'
            )
        
        # Step 4: Display Results Summary
        print("\n" + "=" * 70)
        print("STEP 4: RESULTS SUMMARY")
        print("=" * 70)
        
        summary = sentiment_analyzer.get_comprehensive_summary(df_with_sentiment)
        
        print(f"\n📊 SENTIMENT ANALYSIS SUMMARY FOR {company_name.upper()}")
        print("-" * 50)
        print(f"Total Articles: {summary['total_articles']}")
        
        # Combined sentiment summary
        combined_pos = summary.get('combined_positive_percentage', 0)
        combined_neg = summary.get('combined_negative_percentage', 0)
        combined_neu = summary.get('combined_neutral_percentage', 0)
        
        print(f"\nCombined Sentiment Distribution:")
        print(f"  Positive: {summary.get('combined_positive_count', 0)} ({combined_pos:.1f}%)")
        print(f"  Negative: {summary.get('combined_negative_count', 0)} ({combined_neg:.1f}%)")
        print(f"  Neutral:  {summary.get('combined_neutral_count', 0)} ({combined_neu:.1f}%)")
        
        # Step 5: Save Data
        sentiment_filename = f"comprehensive_sentiment_{company_name.replace(' ', '_').lower()}.csv"
        filepath = news_fetcher.save_to_csv(df_with_sentiment, sentiment_filename)
        
        print(f"\n✅ Data saved to: {filepath}")
        print(f"📊 Charts saved to: data/charts/")
        
        # Final sentiment assessment
        if combined_pos > combined_neg:
            overall_sentiment = "POSITIVE 📈"
        elif combined_neg > combined_pos:
            overall_sentiment = "NEGATIVE 📉"
        else:
            overall_sentiment = "NEUTRAL ➡️"
        
        print(f"\n🎯 OVERALL SENTIMENT: {overall_sentiment}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()