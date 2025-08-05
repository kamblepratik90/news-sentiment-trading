import pandas as pd
from data_fetcher.news_api import NewsAPIFetcher
from sentiment_analysis.analyzer import SentimentAnalyzer
from trading_logic.signal_generator import TradingSignalGenerator
from visualization.sentiment_charts import SentimentVisualizer
import os
from dotenv import load_dotenv

def main():
    """
    Complete analysis: Fetch news, analyze sentiment, generate trading signals, and create visualizations
    """
    load_dotenv()
    
    # Get configuration
    company_name = os.getenv('COMPANY_NAME', 'Reliance Industries')
    
    try:
        # Step 1: Fetch news data
        print("=" * 80)
        print("🗞️  STEP 1: FETCHING NEWS DATA")
        print("=" * 80)
        
        news_fetcher = NewsAPIFetcher()
        df = news_fetcher.fetch_company_news(
            company_name=company_name,
            max_articles=50,
            days_back=30
        )
        
        if df.empty:
            print("No articles found. Exiting...")
            return
        
        # Step 2: Sentiment Analysis
        print("\n" + "=" * 80)
        print("🧠 STEP 2: SENTIMENT ANALYSIS")
        print("=" * 80)
        
        sentiment_analyzer = SentimentAnalyzer()
        df_with_sentiment = sentiment_analyzer.analyze_dataframe_comprehensive(df)
        
        # Step 3: Trading Signal Generation
        print("\n" + "=" * 80)
        print("🚦 STEP 3: TRADING SIGNAL GENERATION")
        print("=" * 80)
        
        signal_generator = TradingSignalGenerator()
        
        # Generate different types of signals
        print("📊 Generating Basic Trading Signal...")
        basic_signal = signal_generator.generate_basic_signal(df_with_sentiment, 'combined_sentiment_label')
        
        print("📊 Generating Weighted Trading Signal...")
        weighted_signal = signal_generator.generate_weighted_signal(df_with_sentiment, 'combined_sentiment_label')
        
        print("📊 Generating Time-Weighted Trading Signal...")
        time_weighted_signal = signal_generator.generate_time_weighted_signal(df_with_sentiment, 'combined_sentiment_label')
        
        # Step 4: Display Trading Signals
        print("\n" + "=" * 80)
        print("📈 STEP 4: TRADING SIGNAL RESULTS")
        print("=" * 80)
        
        print("\n🔸 BASIC SIGNAL ANALYSIS:")
        print(signal_generator.get_signal_summary(basic_signal))
        
        print("\n🔹 WEIGHTED SIGNAL ANALYSIS:")
        print(signal_generator.get_signal_summary(weighted_signal))
        
        print("\n🔶 TIME-WEIGHTED SIGNAL ANALYSIS:")
        print(signal_generator.get_signal_summary(time_weighted_signal))
        
        # Step 5: Signal Comparison
        print("\n" + "=" * 80)
        print("⚖️  STEP 5: SIGNAL COMPARISON")
        print("=" * 80)
        
        signals_comparison = {
            'Basic': basic_signal['signal'],
            'Weighted': weighted_signal['signal'],
            'Time-Weighted': time_weighted_signal['signal']
        }
        
        print("📊 SIGNAL COMPARISON:")
        for method, signal in signals_comparison.items():
            confidence = locals()[f"{method.lower().replace('-', '_')}_signal"]['confidence']
            print(f"  {method:15}: {signal:20} (Confidence: {confidence:.1%})")
        
        # Consensus signal
        signal_votes = list(signals_comparison.values())
        if signal_votes.count('BUY') >= 2:
            consensus = 'BUY'
        elif signal_votes.count('SELL') >= 2:
            consensus = 'SELL'
        else:
            consensus = 'HOLD'
        
        consensus_confidence = sum([basic_signal['confidence'], weighted_signal['confidence'], time_weighted_signal['confidence']]) / 3
        
        print(f"\n🎯 CONSENSUS SIGNAL: {consensus} (Average Confidence: {consensus_confidence:.1%})")
        
        # Step 6: Create Visualizations
        print("\n" + "=" * 80)
        print("📊 STEP 6: CREATING VISUALIZATIONS")
        print("=" * 80)
        
        visualizer = SentimentVisualizer()
        
        # Create sentiment charts
        chart_path = visualizer.create_sentiment_bar_chart(
            df_with_sentiment, 
            'combined_sentiment_label',
            title=f'Sentiment Analysis for {company_name} - Trading Signal: {consensus}'
        )
        
        comp_chart = visualizer.create_comprehensive_sentiment_chart(df_with_sentiment)
        
        # Step 7: Save Results
        print("\n" + "=" * 80)
        print("💾 STEP 7: SAVING RESULTS")
        print("=" * 80)
        
        # Add trading signals to DataFrame
        df_with_sentiment['basic_signal'] = basic_signal['signal']
        df_with_sentiment['basic_signal_confidence'] = basic_signal['confidence']
        df_with_sentiment['weighted_signal'] = weighted_signal['signal']
        df_with_sentiment['weighted_signal_confidence'] = weighted_signal['confidence']
        df_with_sentiment['time_weighted_signal'] = time_weighted_signal['signal']
        df_with_sentiment['time_weighted_signal_confidence'] = time_weighted_signal['confidence']
        df_with_sentiment['consensus_signal'] = consensus
        df_with_sentiment['consensus_confidence'] = consensus_confidence
        
        # Save comprehensive results
        results_filename = f"complete_analysis_{company_name.replace(' ', '_').lower()}.csv"
        filepath = news_fetcher.save_to_csv(df_with_sentiment, results_filename)
        
        # Save signal summary
        signal_summary = {
            'company': company_name,
            'analysis_date': pd.Timestamp.now().isoformat(),
            'total_articles': len(df_with_sentiment),
            'basic_signal': basic_signal,
            'weighted_signal': weighted_signal,
            'time_weighted_signal': time_weighted_signal,
            'consensus_signal': consensus,
            'consensus_confidence': consensus_confidence
        }
        
        import json
        summary_filename = f"signal_summary_{company_name.replace(' ', '_').lower()}.json"
        summary_path = os.path.join('data', 'raw', summary_filename)
        
        with open(summary_path, 'w') as f:
            json.dump(signal_summary, f, indent=2, default=str)
        
        print(f"✅ Complete analysis saved to: {filepath}")
        print(f"✅ Signal summary saved to: {summary_path}")
        print(f"✅ Charts saved to: data/charts/")
        
        # Final Summary
        print("\n" + "=" * 80)
        print("🎯 FINAL INVESTMENT RECOMMENDATION")
        print("=" * 80)
        
        emoji_map = {
            'BUY': '🟢 📈 Strong Buy Signal',
            'SELL': '🔴 📉 Strong Sell Signal',
            'HOLD': '🟡 ➡️ Hold Position',
            'INSUFFICIENT_DATA': '⚪ ❓ Insufficient Data'
        }
        
        print(f"\nCompany: {company_name}")
        print(f"Analysis Period: Last 30 days ({len(df_with_sentiment)} articles)")
        print(f"Recommendation: {emoji_map.get(consensus, consensus)}")
        print(f"Confidence Level: {consensus_confidence:.1%}")
        
        # Risk assessment
        if consensus_confidence > 0.8:
            risk_level = "LOW RISK"
        elif consensus_confidence > 0.6:
            risk_level = "MEDIUM RISK"
        else:
            risk_level = "HIGH RISK"
        
        print(f"Risk Assessment: {risk_level}")
        print(f"\n⚠️  Disclaimer: This is based on news sentiment analysis only.")
        print(f"   Always consult financial advisors and consider other factors before trading.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()