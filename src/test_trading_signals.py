import pandas as pd
from trading_logic.signal_generator import TradingSignalGenerator, generate_trading_signal
import numpy as np

def create_test_scenarios():
    """Create different test scenarios for trading signals"""
    
    scenarios = {
        'strong_buy': {
            'positive': 15,
            'negative': 3,
            'neutral': 2,
            'expected': 'BUY'
        },
        'strong_sell': {
            'positive': 2,
            'negative': 14,
            'neutral': 4,
            'expected': 'SELL'
        },
        'mixed_hold': {
            'positive': 8,
            'negative': 7,
            'neutral': 5,
            'expected': 'HOLD'
        },
        'insufficient_data': {
            'positive': 1,
            'negative': 1,
            'neutral': 1,
            'expected': 'INSUFFICIENT_DATA'
        }
    }
    
    test_datasets = {}
    
    for scenario_name, counts in scenarios.items():
        # Create test data
        sentiments = (['positive'] * counts['positive'] + 
                     ['negative'] * counts['negative'] + 
                     ['neutral'] * counts['neutral'])
        
        total_articles = len(sentiments)
        
        test_data = {
            'title': [f'Test Article {i+1}' for i in range(total_articles)],
            'combined_sentiment_label': sentiments,
            'combined_sentiment_confidence': np.random.uniform(0.6, 0.9, total_articles),
            'published_at': pd.date_range('2024-01-01', periods=total_articles, freq='D')
        }
        
        test_datasets[scenario_name] = {
            'df': pd.DataFrame(test_data),
            'expected': counts['expected']
        }
    
    return test_datasets

def main():
    """Test the trading signal generation"""
    print("🧪 TESTING TRADING SIGNAL GENERATOR")
    print("=" * 60)
    
    # Create test scenarios
    test_scenarios = create_test_scenarios()
    
    # Initialize signal generator
    signal_generator = TradingSignalGenerator()
    
    for scenario_name, scenario_data in test_scenarios.items():
        df = scenario_data['df']
        expected_signal = scenario_data['expected']
        
        print(f"\n🔍 Testing Scenario: {scenario_name.upper().replace('_', ' ')}")
        print("-" * 40)
        
        # Test basic signal
        basic_signal = signal_generator.generate_basic_signal(df)
        
        print(f"Expected Signal: {expected_signal}")
        print(f"Generated Signal: {basic_signal['signal']}")
        print(f"Confidence: {basic_signal['confidence']:.1%}")
        print(f"Reason: {basic_signal['reason']}")
        
        # Check if test passed
        if basic_signal['signal'] == expected_signal:
            print("✅ Test PASSED")
        else:
            print("❌ Test FAILED")
        
        # Show sentiment distribution
        sentiment_counts = df['combined_sentiment_label'].value_counts()
        print(f"Sentiment Distribution: {dict(sentiment_counts)}")
    
    # Test the convenience function
    print(f"\n🔧 Testing Convenience Function")
    print("-" * 40)
    
    test_df = test_scenarios['strong_buy']['df']
    quick_signal = generate_trading_signal(test_df, method='basic')
    print(f"Quick Signal: {quick_signal['signal']} (Confidence: {quick_signal['confidence']:.1%})")
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    main()