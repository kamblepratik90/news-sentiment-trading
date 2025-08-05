from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
from typing import Union, List, Dict
import warnings
warnings.filterwarnings("ignore")

class SentimentAnalyzer:
    """
    A class to analyze sentiment of news articles using pre-trained models
    """
    
    def __init__(self, model_name="distilbert-base-uncased-finetuned-sst-2-english"):
        """
        Initialize the sentiment analyzer with a pre-trained model
        
        Args:
            model_name (str): Hugging Face model name for sentiment analysis
        """
        self.model_name = model_name
        print(f"Loading sentiment analysis model: {model_name}")
        
        try:
            # Initialize the sentiment analysis pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                return_all_scores=True
            )
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("Falling back to default model...")
            self.sentiment_pipeline = pipeline("sentiment-analysis", return_all_scores=True)
    
    def analyze_text(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text string
        
        Args:
            text (str): Text to analyze
            
        Returns:
            dict: Dictionary containing sentiment label, confidence, and scores
        """
        if not text or text.strip() == "":
            return {
                'label': 'neutral',
                'confidence': 0.0,
                'positive_score': 0.0,
                'negative_score': 0.0
            }
        
        try:
            # Truncate text if too long (BERT models have token limits)
            text = text[:512]
            
            # Get sentiment scores
            results = self.sentiment_pipeline(text)[0]
            
            # Extract scores
            positive_score = 0.0
            negative_score = 0.0
            
            for result in results:
                if result['label'].upper() in ['POSITIVE', 'POS']:
                    positive_score = result['score']
                elif result['label'].upper() in ['NEGATIVE', 'NEG']:
                    negative_score = result['score']
            
            # Determine primary sentiment
            if positive_score > negative_score:
                if positive_score > 0.6:  # Strong positive
                    label = 'positive'
                    confidence = positive_score
                else:  # Weak positive, classify as neutral
                    label = 'neutral'
                    confidence = max(positive_score, negative_score)
            elif negative_score > positive_score:
                if negative_score > 0.6:  # Strong negative
                    label = 'negative'
                    confidence = negative_score
                else:  # Weak negative, classify as neutral
                    label = 'neutral'
                    confidence = max(positive_score, negative_score)
            else:
                label = 'neutral'
                confidence = max(positive_score, negative_score)
            
            return {
                'label': label,
                'confidence': confidence,
                'positive_score': positive_score,
                'negative_score': negative_score
            }
            
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {
                'label': 'neutral',
                'confidence': 0.0,
                'positive_score': 0.0,
                'negative_score': 0.0
            }
    
    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = 'title') -> pd.DataFrame:
        """
        Analyze sentiment for all texts in a DataFrame
        
        Args:
            df (pd.DataFrame): DataFrame containing text data
            text_column (str): Name of the column containing text to analyze
            
        Returns:
            pd.DataFrame: DataFrame with added sentiment columns
        """
        print(f"Analyzing sentiment for {len(df)} articles...")
        
        if text_column not in df.columns:
            print(f"Error: Column '{text_column}' not found in DataFrame")
            return df
        
        # Create a copy to avoid modifying original
        df_sentiment = df.copy()
        
        # Initialize sentiment columns
        df_sentiment['sentiment_label'] = ''
        df_sentiment['sentiment_confidence'] = 0.0
        df_sentiment['positive_score'] = 0.0
        df_sentiment['negative_score'] = 0.0
        
        # Analyze each text
        for idx, row in df_sentiment.iterrows():
            if idx % 10 == 0:  # Progress indicator
                print(f"Processing article {idx + 1}/{len(df_sentiment)}")
            
            text = str(row[text_column])
            sentiment_result = self.analyze_text(text)
            
            df_sentiment.at[idx, 'sentiment_label'] = sentiment_result['label']
            df_sentiment.at[idx, 'sentiment_confidence'] = sentiment_result['confidence']
            df_sentiment.at[idx, 'positive_score'] = sentiment_result['positive_score']
            df_sentiment.at[idx, 'negative_score'] = sentiment_result['negative_score']
        
        print("✅ Sentiment analysis completed!")
        return df_sentiment
    
    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate a summary of sentiment analysis results
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis results
            
        Returns:
            dict: Summary statistics
        """
        if 'sentiment_label' not in df.columns:
            print("No sentiment analysis found in DataFrame")
            return {}
        
        sentiment_counts = df['sentiment_label'].value_counts()
        total_articles = len(df)
        
        summary = {
            'total_articles': total_articles,
            'positive_count': sentiment_counts.get('positive', 0),
            'negative_count': sentiment_counts.get('negative', 0),
            'neutral_count': sentiment_counts.get('neutral', 0),
            'positive_percentage': (sentiment_counts.get('positive', 0) / total_articles) * 100,
            'negative_percentage': (sentiment_counts.get('negative', 0) / total_articles) * 100,
            'neutral_percentage': (sentiment_counts.get('neutral', 0) / total_articles) * 100,
            'average_confidence': df['sentiment_confidence'].mean(),
            'average_positive_score': df['positive_score'].mean(),
            'average_negative_score': df['negative_score'].mean()
        }
        
        return summary
    
    def analyze_combined_text(self, df: pd.DataFrame) -> Dict:
        """
        Analyze sentiment using both title and description
        
        Args:
            df (pd.DataFrame): DataFrame with title and description columns
            
        Returns:
            dict: Combined sentiment analysis
        """
        print("Analyzing combined sentiment (title + description)...")
        
        # Combine title and description
        df_combined = df.copy()
        df_combined['combined_text'] = df_combined['title'].fillna('') + ' ' + df_combined['description'].fillna('')
        
        # Analyze combined text
        df_combined = self.analyze_dataframe(df_combined, 'combined_text')
        
        # Rename columns to indicate combined analysis
        df_combined = df_combined.rename(columns={
            'sentiment_label': 'combined_sentiment_label',
            'sentiment_confidence': 'combined_sentiment_confidence',
            'positive_score': 'combined_positive_score',
            'negative_score': 'combined_negative_score'
        })
        
        return df_combined
    
    def analyze_dataframe_comprehensive(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive sentiment analysis for both title and description columns
        
        Args:
            df (pd.DataFrame): DataFrame containing news articles
            
        Returns:
            pd.DataFrame: DataFrame with sentiment analysis for title, description, and combined
        """
        print(f"Starting comprehensive sentiment analysis for {len(df)} articles...")
        
        # Create a copy to avoid modifying original
        df_sentiment = df.copy()
        
        # Initialize all sentiment columns
        columns_to_add = [
            'title_sentiment_label', 'title_sentiment_confidence', 'title_positive_score', 'title_negative_score',
            'description_sentiment_label', 'description_sentiment_confidence', 'description_positive_score', 'description_negative_score',
            'combined_sentiment_label', 'combined_sentiment_confidence', 'combined_positive_score', 'combined_negative_score'
        ]
        
        for col in columns_to_add:
            df_sentiment[col] = 0.0 if 'score' in col or 'confidence' in col else 'neutral'
        
        # Analyze each article
        for idx, row in df_sentiment.iterrows():
            if idx % 5 == 0:  # Progress indicator every 5 articles
                print(f"Processing article {idx + 1}/{len(df_sentiment)}")
            
            # 1. Analyze Title
            title = str(row.get('title', ''))
            title_sentiment = self.analyze_text(title)
            
            df_sentiment.at[idx, 'title_sentiment_label'] = title_sentiment['label']
            df_sentiment.at[idx, 'title_sentiment_confidence'] = title_sentiment['confidence']
            df_sentiment.at[idx, 'title_positive_score'] = title_sentiment['positive_score']
            df_sentiment.at[idx, 'title_negative_score'] = title_sentiment['negative_score']
            
            # 2. Analyze Description
            description = str(row.get('description', ''))
            desc_sentiment = self.analyze_text(description)
            
            df_sentiment.at[idx, 'description_sentiment_label'] = desc_sentiment['label']
            df_sentiment.at[idx, 'description_sentiment_confidence'] = desc_sentiment['confidence']
            df_sentiment.at[idx, 'description_positive_score'] = desc_sentiment['positive_score']
            df_sentiment.at[idx, 'description_negative_score'] = desc_sentiment['negative_score']
            
            # 3. Analyze Combined Text
            combined_text = f"{title} {description}".strip()
            combined_sentiment = self.analyze_text(combined_text)
            
            df_sentiment.at[idx, 'combined_sentiment_label'] = combined_sentiment['label']
            df_sentiment.at[idx, 'combined_sentiment_confidence'] = combined_sentiment['confidence']
            df_sentiment.at[idx, 'combined_positive_score'] = combined_sentiment['positive_score']
            df_sentiment.at[idx, 'combined_negative_score'] = combined_sentiment['negative_score']
        
        print("✅ Comprehensive sentiment analysis completed!")
        return df_sentiment
    
    def get_comprehensive_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive summary for title, description, and combined sentiment
        
        Args:
            df (pd.DataFrame): DataFrame with comprehensive sentiment analysis
            
        Returns:
            dict: Comprehensive summary statistics
        """
        def get_sentiment_stats(df, prefix):
            """Helper function to get sentiment stats for a specific analysis type"""
            label_col = f'{prefix}_sentiment_label'
            confidence_col = f'{prefix}_sentiment_confidence'
            pos_score_col = f'{prefix}_positive_score'
            neg_score_col = f'{prefix}_negative_score'
            
            if label_col not in df.columns:
                return {}
                
            sentiment_counts = df[label_col].value_counts()
            total = len(df)
            
            # Convert numpy types to native Python types
            return {
                f'{prefix}_positive_count': int(sentiment_counts.get('positive', 0)),
                f'{prefix}_negative_count': int(sentiment_counts.get('negative', 0)),
                f'{prefix}_neutral_count': int(sentiment_counts.get('neutral', 0)),
                f'{prefix}_positive_percentage': float((sentiment_counts.get('positive', 0) / total) * 100),
                f'{prefix}_negative_percentage': float((sentiment_counts.get('negative', 0) / total) * 100),
                f'{prefix}_neutral_percentage': float((sentiment_counts.get('neutral', 0) / total) * 100),
                f'{prefix}_avg_confidence': float(df[confidence_col].mean()) if confidence_col in df.columns else 0.0,
                f'{prefix}_avg_positive_score': float(df[pos_score_col].mean()) if pos_score_col in df.columns else 0.0,
                f'{prefix}_avg_negative_score': float(df[neg_score_col].mean()) if neg_score_col in df.columns else 0.0
            }
        
        summary = {'total_articles': int(len(df))}
        
        # Get stats for each analysis type
        summary.update(get_sentiment_stats(df, 'title'))
        summary.update(get_sentiment_stats(df, 'description'))
        summary.update(get_sentiment_stats(df, 'combined'))
        
        return summary