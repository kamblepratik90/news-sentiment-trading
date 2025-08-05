import unittest
from src.sentiment_analysis.analyzer import SentimentAnalyzer

class TestSentimentAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SentimentAnalyzer()

    def test_analyze_sentiment_positive(self):
        article_text = "The company has shown remarkable growth and innovation."
        sentiment_score = self.analyzer.analyze_sentiment(article_text)
        self.assertGreater(sentiment_score, 0, "Sentiment score should be positive for positive text.")

    def test_analyze_sentiment_negative(self):
        article_text = "The company is facing severe challenges and losses."
        sentiment_score = self.analyzer.analyze_sentiment(article_text)
        self.assertLess(sentiment_score, 0, "Sentiment score should be negative for negative text.")

    def test_analyze_sentiment_neutral(self):
        article_text = "The company has released its quarterly report."
        sentiment_score = self.analyzer.analyze_sentiment(article_text)
        self.assertEqual(sentiment_score, 0, "Sentiment score should be neutral for neutral text.")

if __name__ == '__main__':
    unittest.main()