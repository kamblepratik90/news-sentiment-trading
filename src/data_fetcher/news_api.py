import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import time

class NewsAPIFetcher:
    """
    A class to fetch news articles from NewsAPI for a specific company
    """
    
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv('API_KEY')
        self.base_url = "https://newsapi.org/v2/everything"
        
        if not self.api_key:
            raise ValueError("API key is required. Set it in .env file or pass it directly.")
    
    def fetch_company_news(self, company_name, max_articles=100, days_back=7, clean_data=True):
        """
        Fetch news articles for a specific company
        
        Args:
            company_name (str): Name of the company to search for
            max_articles (int): Maximum number of articles to fetch
            days_back (int): Number of days to look back for articles
            clean_data (bool): Whether to clean the data after fetching
        
        Returns:
            pd.DataFrame: DataFrame containing article data
        """
        
        # Calculate date range
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        params = {
            'q': f'"{company_name}"',
            'apiKey': self.api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'pageSize': min(100, max_articles),  # NewsAPI max is 100 per request
            'page': 1
        }
        
        articles_data = []
        articles_fetched = 0
        
        try:
            while articles_fetched < max_articles:
                print(f"Fetching page {params['page']}...")
                
                response = requests.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data['status'] != 'ok':
                    print(f"API Error: {data.get('message', 'Unknown error')}")
                    break
                
                articles = data['articles']
                
                if not articles:
                    print("No more articles found.")
                    break
                
                # Process articles
                for article in articles:
                    if articles_fetched >= max_articles:
                        break
                    
                    article_data = {
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'url': article.get('url', ''),
                        'source': article.get('source', {}).get('name', ''),
                        'author': article.get('author', ''),
                        'published_at': article.get('publishedAt', ''),
                        'url_to_image': article.get('urlToImage', ''),
                        'company_searched': company_name
                    }
                    
                    articles_data.append(article_data)
                    articles_fetched += 1
                
                # Check if we need to fetch more pages
                total_results = data.get('totalResults', 0)
                if articles_fetched >= total_results or len(articles) < params['pageSize']:
                    break
                
                params['page'] += 1
                time.sleep(0.1)  # Small delay to respect rate limits
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        # Convert to DataFrame
        df = pd.DataFrame(articles_data)
        
        if not df.empty:
            # Convert published_at to datetime
            df['published_at'] = pd.to_datetime(df['published_at'])
            # Sort by publication date (newest first)
            df = df.sort_values('published_at', ascending=False).reset_index(drop=True)
            
            print(f"Successfully fetched {len(df)} raw articles for {company_name}")
            
            # Clean the data if requested
            if clean_data:
                df = self.clean_data(df)
        
        return df
    
    def save_to_csv(self, df, filename=None):
        """
        Save DataFrame to CSV file
        
        Args:
            df (pd.DataFrame): DataFrame to save
            filename (str): Optional filename, uses env var if not provided
        """
        if filename is None:
            filename = os.getenv('OUTPUT_CSV', 'articles.csv')
        
        # Get the project root directory (go up 3 levels from this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        data_dir = os.path.join(project_root, 'data', 'raw')
        
        # Ensure data directory exists - with better error handling
        try:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"Created directory: {data_dir}")
            else:
                print(f"Directory already exists: {data_dir}")
        except OSError as e:
            print(f"Error creating directory {data_dir}: {e}")
            # Fallback to current directory
            data_dir = os.getcwd()
            print(f"Saving to current directory instead: {data_dir}")
        
        filepath = os.path.join(data_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath
    
    def clean_data(self, df):
        """
        Clean the fetched news data
        
        Args:
            df (pd.DataFrame): Raw DataFrame from news API
            
        Returns:
            pd.DataFrame: Cleaned DataFrame
        """
        print("Starting data cleaning...")
        initial_count = len(df)
        
        if df.empty:
            print("No data to clean.")
            return df
        
        # 1. Remove entries with missing titles or descriptions
        print("Removing entries with missing titles or descriptions...")
        df_cleaned = df.dropna(subset=['title', 'description'])
        
        # Also remove entries where title or description are empty strings
        df_cleaned = df_cleaned[
            (df_cleaned['title'].str.strip() != '') & 
            (df_cleaned['description'].str.strip() != '')
        ]
        
        missing_removed = initial_count - len(df_cleaned)
        print(f"Removed {missing_removed} entries with missing title/description")
        
        # 2. Handle duplicate articles
        print("Removing duplicate articles...")
        before_dedup = len(df_cleaned)
        
        # Remove duplicates based on title and url (keep first occurrence)
        df_cleaned = df_cleaned.drop_duplicates(subset=['title', 'url'], keep='first')
        
        # Also check for similar titles (case-insensitive)
        df_cleaned = df_cleaned.drop_duplicates(subset=['title'], keep='first')
        
        duplicates_removed = before_dedup - len(df_cleaned)
        print(f"Removed {duplicates_removed} duplicate articles")
        
        # 3. Standardize publication date format
        print("Standardizing publication date format...")
        try:
            # Convert to datetime if not already done
            df_cleaned['published_at'] = pd.to_datetime(df_cleaned['published_at'])
            
            # Create additional date columns for analysis
            df_cleaned['date'] = df_cleaned['published_at'].dt.date
            df_cleaned['year'] = df_cleaned['published_at'].dt.year
            df_cleaned['month'] = df_cleaned['published_at'].dt.month
            df_cleaned['day'] = df_cleaned['published_at'].dt.day
            df_cleaned['hour'] = df_cleaned['published_at'].dt.hour
            
        except Exception as e:
            print(f"Warning: Error processing dates: {e}")
        
        # 4. Clean text fields
        print("Cleaning text fields...")
        
        # Remove extra whitespace and newlines from title and description
        df_cleaned['title'] = df_cleaned['title'].str.strip().str.replace('\n', ' ').str.replace('\r', ' ')
        df_cleaned['description'] = df_cleaned['description'].str.strip().str.replace('\n', ' ').str.replace('\r', ' ')
        
        # Remove entries where title is just "[Removed]" (common in NewsAPI)
        df_cleaned = df_cleaned[df_cleaned['title'] != '[Removed]']
        df_cleaned = df_cleaned[df_cleaned['description'] != '[Removed]']
        
        # 5. Filter out non-relevant articles (optional - can be customized)
        print("Filtering relevant articles...")
        
        # Remove articles that are clearly not about the company
        # This is a basic filter - can be enhanced based on requirements
        company_keywords = df_cleaned['company_searched'].iloc[0].lower().split()
        
        def is_relevant(row):
            title_lower = row['title'].lower()
            desc_lower = row['description'].lower()
            
            # Check if any company keyword appears in title or description
            for keyword in company_keywords:
                if len(keyword) > 2 and (keyword in title_lower or keyword in desc_lower):
                    return True
            return False
        
        df_cleaned['is_relevant'] = df_cleaned.apply(is_relevant, axis=1)
        relevant_articles = df_cleaned[df_cleaned['is_relevant']].copy()
        irrelevant_removed = len(df_cleaned) - len(relevant_articles)
        
        print(f"Removed {irrelevant_removed} potentially irrelevant articles")
        
        # Drop the helper column
        relevant_articles = relevant_articles.drop('is_relevant', axis=1)
        
        # 6. Reset index
        relevant_articles = relevant_articles.reset_index(drop=True)
        
        # 7. Sort by publication date (newest first)
        relevant_articles = relevant_articles.sort_values('published_at', ascending=False)
        
        final_count = len(relevant_articles)
        total_removed = initial_count - final_count
        
        print(f"\nData cleaning completed!")
        print(f"Initial articles: {initial_count}")
        print(f"Final articles: {final_count}")
        print(f"Total removed: {total_removed}")
        print(f"Retention rate: {(final_count/initial_count)*100:.1f}%")
        
        return relevant_articles