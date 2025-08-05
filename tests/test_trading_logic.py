import unittest
import pandas as pd
from src.trading_logic.signal_generator import SignalGenerator

class TestSignalGenerator(unittest.TestCase):

    def setUp(self):
        self.signal_generator = SignalGenerator()
        self.test_data = pd.DataFrame({
            'title': ['Article 1', 'Article 2'],
            'description': ['Description 1', 'Description 2'],
            'publication_date': ['2023-01-01', '2023-01-02'],
            'sentiment_score': [0.5, -0.2]  # Example sentiment scores
        })

    def test_generate_signals(self):
        signals = self.signal_generator.generate_signals(self.test_data)
        expected_signals = ['Buy', 'Sell']  # Example expected signals based on sentiment
        self.assertEqual(signals.tolist(), expected_signals)

if __name__ == '__main__':
    unittest.main()