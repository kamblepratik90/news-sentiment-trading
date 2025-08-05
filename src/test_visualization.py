import pandas as pd
from visualization.sentiment_charts import SentimentVisualizer
import numpy as np

def create_test_data():
    """Create test data for visualization"""
    np.random.seed(42)
    
    # Create sample data
    n_articles = 50
    sentiments = np.random.choice(['positive', 'negative', 'neutral'], 
                                 size=n_articles, 
                                 p=[0.4, 0.3, 0.3])
    
    test_data = {
        'title': [f'Test Article {i+1}' for i in range(n_articles)],
        'description': [f'Description for article {i+1}' for i in range(n_articles)],
        'title_sentiment_label': sentiments,
        'published_at': pd.date_range('2024-01-01', periods=n_articles, freq='D')
    }
    
    return pd.DataFrame(test_data)

def main():
    """Test the visualization functionality"""
    print("🧪 Testing Sentiment Visualization...")
    
    try:
        # Create test data
        df = create_test_data()
        print(f"Created test dataset with {len(df)} articles")
        
        # Create visualizer
        visualizer = SentimentVisualizer()
        
        # Test simple bar chart
        print("\n📊 Creating simple sentiment bar chart...")
        chart_path = visualizer.create_sentiment_bar_chart(
            df, 
            'title_sentiment_label',
            title='Test Sentiment Distribution'
        )
        
        print(f"✅ Chart created successfully: {chart_path}")
        
        # Display sentiment distribution
        sentiment_counts = df['title_sentiment_label'].value_counts()
        print(f"\n📈 Test Data Sentiment Distribution:")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()