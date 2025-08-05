from visualization.sentiment_charts import SentimentVisualizer, create_simple_sentiment_chart
import pandas as pd
import os

def main():
    """
    Create sentiment visualization charts from existing CSV data
    """
    # Look for CSV files with sentiment data
    data_dir = "data/raw"
    
    if not os.path.exists(data_dir):
        print("data/raw directory not found")
        return
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    if not csv_files:
        print("No CSV files found in data/raw directory")
        return
    
    print("Found CSV files:")
    for i, file in enumerate(csv_files, 1):
        print(f"  {i}. {file}")
    
    # Process each CSV file
    for csv_file in csv_files:
        csv_path = os.path.join(data_dir, csv_file)
        
        try:
            print(f"\n📊 Processing: {csv_file}")
            df = pd.read_csv(csv_path)
            
            # Check what sentiment columns are available
            sentiment_columns = [col for col in df.columns if 'sentiment_label' in col]
            
            if not sentiment_columns:
                print(f"No sentiment columns found in {csv_file}")
                continue
            
            visualizer = SentimentVisualizer()
            
            # Create charts for each sentiment column found
            for sentiment_col in sentiment_columns:
                print(f"Creating chart for: {sentiment_col}")
                
                # Generate appropriate title
                analysis_type = sentiment_col.replace('_sentiment_label', '').replace('_', ' ').title()
                title = f'{analysis_type} Sentiment Distribution'
                
                # Generate save path
                safe_filename = csv_file.replace('.csv', f'_{sentiment_col}_chart.png')
                save_path = os.path.join('data', 'charts', safe_filename)
                
                # Create chart
                chart_path = visualizer.create_sentiment_bar_chart(
                    df, sentiment_col, title=title, save_path=save_path
                )
            
            # If comprehensive data available, create comparison chart
            if len(sentiment_columns) > 1:
                comp_save_path = os.path.join('data', 'charts', 
                                            csv_file.replace('.csv', '_comprehensive_chart.png'))
                visualizer.create_comprehensive_sentiment_chart(df, comp_save_path)
            
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
    
    print(f"\n✅ All charts saved to: data/charts/")

if __name__ == "__main__":
    main()