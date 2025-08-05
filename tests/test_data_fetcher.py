import unittest
from src.data_fetcher.news_api import NewsAPIFetcher
import pandas as pd

class TestNewsAPIFetcher(unittest.TestCase):

    def setUp(self):
        self.fetcher = NewsAPIFetcher()
        self.company_name = 'Reliance Industries'

    def test_fetch_articles(self):
        articles_df = self.fetcher.fetch_articles(self.company_name)
        self.assertIsInstance(articles_df, pd.DataFrame)
        self.assertEqual(len(articles_df), 100)
        self.assertIn('title', articles_df.columns)
        self.assertIn('description', articles_df.columns)
        self.assertIn('publishedAt', articles_df.columns)

if __name__ == '__main__':
    unittest.main()