import pandas as pd
from sentiment_analysis.analyzer import SentimentAnalyzer
from sentiment_analysis.quick_analyzer import analyze_sentiment
import os

def apply_sentiment_simple(csv_filepath: str):
    """
    Apply sentiment analysis to an existing CSV file with news data
    
    Args:
        csv_filepath (str): Path to the CSV file containing news data
    """
    print(f"Loading data from: {csv_filepath}")
    
    try:
        # Load the data
        df = pd.read_csv(csv_filepath)
        print(f"Loaded {len(df)} articles")
        
        # Check required columns
        if 'title' not in df.columns:
            print("Error: 'title' column not found in the data")
            return
        
        # Initialize sentiment analyzer
        sentiment_analyzer = SentimentAnalyzer()
        
        print("Applying sentiment analysis to titles...")
        
        # Method 1: Using the quick analyzer function
        df['title_sentiment'] = df['title'].apply(lambda x: analyze_sentiment(str(x)))
        
        # Method 2: Using the comprehensive analyzer for more detailed results
        if 'description' in df.columns:
            print("Applying sentiment analysis to descriptions...")
            df['description_sentiment'] = df['description'].apply(lambda x: analyze_sentiment(str(x)))
            
            # Combined sentiment
            print("Analyzing combined title + description sentiment...")
            df['combined_text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')
            df['combined_sentiment'] = df['combined_text'].apply(lambda x: analyze_sentiment(str(x)))
        
        # Show results
        print(f"\n📊 SENTIMENT ANALYSIS RESULTS:")
        print("-" * 50)
        
        title_sentiment_counts = df['title_sentiment'].value_counts()
        print("Title Sentiment Distribution:")
        for sentiment, count in title_sentiment_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        if 'description_sentiment' in df.columns:
            print("\nDescription Sentiment Distribution:")
            desc_sentiment_counts = df['description_sentiment'].value_counts()
            for sentiment, count in desc_sentiment_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
        # Save results
        output_filename = csv_filepath.replace('.csv', '_with_sentiment.csv')
        df.to_csv(output_filename, index=False)
        print(f"\n✅ Results saved to: {output_filename}")
        
        # Show sample results
        print(f"\n📰 SAMPLE RESULTS:")
        print("-" * 80)
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx + 1}. {row['title']}")
            print(f"   Title Sentiment: {row['title_sentiment'].upper()}")
            if 'description_sentiment' in df.columns:
                print(f"   Description Sentiment: {row['description_sentiment'].upper()}")
                print(f"   Combined Sentiment: {row['combined_sentiment'].upper()}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """
    Main function to apply sentiment to existing data
    """
    # Look for CSV files in the data directory
    data_dir = "data/raw"
    
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        
        if csv_files:
            print("Found CSV files:")
            for i, file in enumerate(csv_files, 1):
                print(f"  {i}. {file}")
            
            # Use the first CSV file or let user choose
            csv_file = csv_files[0]
            csv_path = os.path.join(data_dir, csv_file)
            
            print(f"\nProcessing: {csv_file}")
            apply_sentiment_simple(csv_path)
        else:
            print("No CSV files found in data/raw directory")
    else:
        print("data/raw directory not found")

if __name__ == "__main__":
    main()