from flask import Flask, render_template, jsonify, request
import os
import sys
from pathlib import Path
import json
import numpy as np

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from data_fetcher.news_api import NewsAPIFetcher
from sentiment_analysis.analyzer import SentimentAnalyzer
from trading_logic.signal_generator import TradingSignalGenerator
import pandas as pd
from dotenv import load_dotenv
import traceback
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

def convert_to_serializable(obj):
    """
    Convert numpy/pandas types to JSON serializable types
    """
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    return obj

class TradingAnalysisService:
    """Service class to handle the complete trading analysis pipeline"""
    
    def __init__(self):
        self.news_fetcher = None
        self.sentiment_analyzer = None
        self.signal_generator = None
        self.default_company = os.getenv('COMPANY_NAME', 'Apple Inc')
    
    def run_complete_analysis(self, company_name: str = None, max_articles: int = 30, days_back: int = 30):
        """Run the complete analysis pipeline and return results"""
        try:
            # Use provided company name or default
            if not company_name or company_name.strip() == "":
                company_name = self.default_company
            
            company_name = company_name.strip()
            
            # Step 1: Initialize components
            print(f"Initializing components for {company_name}...")
            self.news_fetcher = NewsAPIFetcher()
            self.sentiment_analyzer = SentimentAnalyzer()
            self.signal_generator = TradingSignalGenerator()
            
            # Step 2: Fetch news data
            print(f"Fetching news for {company_name}...")
            df = self.news_fetcher.fetch_company_news(
                company_name=company_name,
                max_articles=max_articles,
                days_back=days_back
            )
            
            if df.empty:
                return {
                    'success': False,
                    'error': f'No news articles found for "{company_name}". Try a different company name or check spelling.',
                    'signal': 'NO_DATA',
                    'confidence': 0.0,
                    'company': company_name
                }
            
            # Step 3: Sentiment Analysis
            print("Analyzing sentiment...")
            df_with_sentiment = self.sentiment_analyzer.analyze_dataframe_comprehensive(df)
            
            # Step 4: Generate Trading Signals
            print("Generating trading signals...")
            basic_signal = self.signal_generator.generate_basic_signal(df_with_sentiment, 'combined_sentiment_label')
            weighted_signal = self.signal_generator.generate_weighted_signal(df_with_sentiment, 'combined_sentiment_label')
            time_weighted_signal = self.signal_generator.generate_time_weighted_signal(df_with_sentiment, 'combined_sentiment_label')
            
            # Determine consensus signal
            signals = [basic_signal['signal'], weighted_signal['signal'], time_weighted_signal['signal']]
            
            if signals.count('BUY') >= 2:
                consensus = 'BUY'
            elif signals.count('SELL') >= 2:
                consensus = 'SELL'
            else:
                consensus = 'HOLD'
            
            # Calculate average confidence
            avg_confidence = (basic_signal['confidence'] + weighted_signal['confidence'] + time_weighted_signal['confidence']) / 3
            
            # Get sentiment summary
            sentiment_summary = self.sentiment_analyzer.get_comprehensive_summary(df_with_sentiment)
            
            # Prepare result with explicit type conversion
            result = {
                'success': True,
                'signal': str(consensus),
                'confidence': float(avg_confidence),
                'company': str(company_name),
                'analysis_timestamp': datetime.now().isoformat(),
                'total_articles': int(len(df_with_sentiment)),
                'search_parameters': {
                    'max_articles': int(max_articles),
                    'days_back': int(days_back)
                },
                'sentiment_breakdown': {
                    'positive_count': int(sentiment_summary.get('combined_positive_count', 0)),
                    'negative_count': int(sentiment_summary.get('combined_negative_count', 0)),
                    'neutral_count': int(sentiment_summary.get('combined_neutral_count', 0)),
                    'positive_percentage': float(sentiment_summary.get('combined_positive_percentage', 0)),
                    'negative_percentage': float(sentiment_summary.get('combined_negative_percentage', 0)),
                    'neutral_percentage': float(sentiment_summary.get('combined_neutral_percentage', 0))
                },
                'signal_details': {
                    'basic_signal': str(basic_signal['signal']),
                    'weighted_signal': str(weighted_signal['signal']),
                    'time_weighted_signal': str(time_weighted_signal['signal']),
                    'basic_confidence': float(basic_signal['confidence']),
                    'weighted_confidence': float(weighted_signal['confidence']),
                    'time_weighted_confidence': float(time_weighted_signal['confidence'])
                },
                'reasoning': str(weighted_signal.get('reason', 'Signal generated based on sentiment analysis'))
            }
            
            # Convert any remaining numpy types to JSON serializable types
            result = convert_to_serializable(result)
            
            return result
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            return {
                'success': False,
                'error': error_msg,
                'signal': 'ERROR',
                'confidence': 0.0,
                'company': company_name if 'company_name' in locals() else 'Unknown'
            }

# Initialize the service
analysis_service = TradingAnalysisService()

@app.route('/')
def index():
    """Main page with the analysis form"""
    return render_template('index.html', default_company=analysis_service.default_company)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Run the complete analysis and return results"""
    try:
        # Get form data
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        max_articles = int(data.get('max_articles', 30))
        days_back = int(data.get('days_back', 30))
        
        # Validate inputs
        if not company_name:
            return jsonify({
                'success': False,
                'error': 'Please enter a company name',
                'signal': 'ERROR',
                'confidence': 0.0
            }), 400
        
        if max_articles < 5 or max_articles > 100:
            max_articles = 30
            
        if days_back < 1 or days_back > 90:
            days_back = 30
        
        result = analysis_service.run_complete_analysis(company_name, max_articles, days_back)
        
        # Ensure the result is JSON serializable
        result = convert_to_serializable(result)
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = f"Error in analysis endpoint: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'signal': 'ERROR',
            'confidence': 0.0
        }), 500

@app.route('/suggestions')
def get_company_suggestions():
    """Get popular company suggestions"""
    popular_companies = [
        "Apple Inc", "Microsoft Corporation", "Amazon.com Inc", "Alphabet Inc", "Tesla Inc",
        "Meta Platforms Inc", "NVIDIA Corporation", "Berkshire Hathaway", "JPMorgan Chase",
        "Johnson & Johnson", "Procter & Gamble", "Visa Inc", "Mastercard Inc", "Coca-Cola",
        "McDonald's Corporation", "Nike Inc", "Intel Corporation", "IBM", "Oracle Corporation",
        "Salesforce Inc", "Netflix Inc", "Disney", "Boeing", "General Electric",
        "Reliance Industries", "Tata Consultancy Services", "Infosys", "HDFC Bank", "ICICI Bank"
    ]
    
    return jsonify({'suggestions': popular_companies})

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Trading Signal Web App...")
    print(f"📊 Default Company: {analysis_service.default_company}")
    print("🌐 Open http://localhost:5001 in your browser")
    
    # Disable reloader to prevent the restart issue
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)