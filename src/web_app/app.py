from flask import Flask, render_template, jsonify, request
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_fetcher.news_api import NewsAPIFetcher
from sentiment_analysis.analyzer import SentimentAnalyzer
from trading_logic.signal_generator import TradingSignalGenerator
import pandas as pd
from dotenv import load_dotenv
import traceback
from datetime import datetime
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

class TradingAnalysisService:
    """Service class to handle the complete trading analysis pipeline"""
    
    def __init__(self):
        self.news_fetcher = None
        self.sentiment_analyzer = None
        self.signal_generator = None
        self.company_name = os.getenv('COMPANY_NAME', 'Reliance Industries')
    
    def run_complete_analysis(self):
        """Run the complete analysis pipeline and return results"""
        try:
            # Step 1: Initialize components
            print("Initializing components...")
            self.news_fetcher = NewsAPIFetcher()
            self.sentiment_analyzer = SentimentAnalyzer()
            self.signal_generator = TradingSignalGenerator()
            
            # Step 2: Fetch news data
            print(f"Fetching news for {self.company_name}...")
            df = self.news_fetcher.fetch_company_news(
                company_name=self.company_name,
                max_articles=30,
                days_back=30
            )
            
            if df.empty:
                return {
                    'success': False,
                    'error': 'No news articles found for the specified company',
                    'signal': 'NO_DATA',
                    'confidence': 0.0
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
            
            # Prepare result
            result = {
                'success': True,
                'signal': consensus,
                'confidence': round(avg_confidence, 3),
                'company': self.company_name,
                'analysis_timestamp': datetime.now().isoformat(),
                'total_articles': len(df_with_sentiment),
                'sentiment_breakdown': {
                    'positive_count': sentiment_summary.get('combined_positive_count', 0),
                    'negative_count': sentiment_summary.get('combined_negative_count', 0),
                    'neutral_count': sentiment_summary.get('combined_neutral_count', 0),
                    'positive_percentage': sentiment_summary.get('combined_positive_percentage', 0),
                    'negative_percentage': sentiment_summary.get('combined_negative_percentage', 0),
                    'neutral_percentage': sentiment_summary.get('combined_neutral_percentage', 0)
                },
                'signal_details': {
                    'basic_signal': basic_signal['signal'],
                    'weighted_signal': weighted_signal['signal'],
                    'time_weighted_signal': time_weighted_signal['signal'],
                    'basic_confidence': basic_signal['confidence'],
                    'weighted_confidence': weighted_signal['confidence'],
                    'time_weighted_confidence': time_weighted_signal['confidence']
                },
                'reasoning': weighted_signal.get('reason', 'Signal generated based on sentiment analysis')
            }
            
            return result
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            
            return {
                'success': False,
                'error': error_msg,
                'signal': 'ERROR',
                'confidence': 0.0
            }

# Initialize the service
analysis_service = TradingAnalysisService()

@app.route('/')
def index():
    """Main page with the analysis button"""
    return render_template('index.html', company_name=analysis_service.company_name)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Run the complete analysis and return results"""
    try:
        result = analysis_service.run_complete_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'signal': 'ERROR',
            'confidence': 0.0
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting Trading Signal Web App...")
    print(f"📊 Company: {analysis_service.company_name}")
    print("🌐 Open http://localhost:5001 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5001)