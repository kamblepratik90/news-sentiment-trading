import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings

class TradingSignalGenerator:
    """
    A class to generate trading signals based on sentiment analysis
    """
    
    def __init__(self, 
                 positive_threshold: float = 2.0,
                 negative_threshold: float = 2.0,
                 min_articles: int = 5,
                 confidence_weight: float = 0.3):
        """
        Initialize the trading signal generator
        
        Args:
            positive_threshold (float): Ratio threshold for BUY signal (positive/negative)
            negative_threshold (float): Ratio threshold for SELL signal (negative/positive)
            min_articles (int): Minimum number of articles required for signal generation
            confidence_weight (float): Weight given to confidence scores (0-1)
        """
        self.positive_threshold = positive_threshold
        self.negative_threshold = negative_threshold
        self.min_articles = min_articles
        self.confidence_weight = confidence_weight
    
    def generate_basic_signal(self, df: pd.DataFrame, sentiment_column: str = 'combined_sentiment_label') -> Dict:
        """
        Generate basic trading signal based on sentiment counts
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis
            sentiment_column (str): Column containing sentiment labels
            
        Returns:
            dict: Trading signal with detailed analysis
        """
        if sentiment_column not in df.columns:
            raise ValueError(f"Column '{sentiment_column}' not found in DataFrame")
        
        if len(df) < self.min_articles:
            return {
                'signal': 'INSUFFICIENT_DATA',
                'confidence': 0.0,
                'reason': f'Insufficient articles. Need at least {self.min_articles}, got {len(df)}',
                'details': {}
            }
        
        # Count sentiment distribution
        sentiment_counts = df[sentiment_column].value_counts()
        positive_count = sentiment_counts.get('positive', 0)
        negative_count = sentiment_counts.get('negative', 0)
        neutral_count = sentiment_counts.get('neutral', 0)
        total_count = len(df)
        
        # Calculate percentages
        positive_pct = (positive_count / total_count) * 100
        negative_pct = (negative_count / total_count) * 100
        neutral_pct = (neutral_count / total_count) * 100
        
        # Generate signal based on basic logic
        signal = 'HOLD'
        reason = ''
        confidence = 0.5  # Default neutral confidence
        
        if negative_count == 0 and positive_count > 0:
            # No negative articles, some positive
            signal = 'BUY'
            reason = f'No negative sentiment detected, {positive_count} positive articles'
            confidence = min(0.9, 0.7 + (positive_count / total_count) * 0.2)
            
        elif positive_count == 0 and negative_count > 0:
            # No positive articles, some negative
            signal = 'SELL'
            reason = f'No positive sentiment detected, {negative_count} negative articles'
            confidence = min(0.9, 0.7 + (negative_count / total_count) * 0.2)
            
        elif positive_count > 0 and negative_count > 0:
            # Both positive and negative articles exist
            positive_ratio = positive_count / negative_count
            negative_ratio = negative_count / positive_count
            
            if positive_ratio >= self.positive_threshold:
                signal = 'BUY'
                reason = f'Positive articles ({positive_count}) are {positive_ratio:.1f}x more than negative ({negative_count})'
                confidence = min(0.9, 0.6 + (positive_ratio / self.positive_threshold) * 0.3)
                
            elif negative_ratio >= self.negative_threshold:
                signal = 'SELL'
                reason = f'Negative articles ({negative_count}) are {negative_ratio:.1f}x more than positive ({positive_count})'
                confidence = min(0.9, 0.6 + (negative_ratio / self.negative_threshold) * 0.3)
                
            else:
                signal = 'HOLD'
                reason = f'Sentiment is mixed - positive: {positive_count}, negative: {negative_count} (ratio: {positive_ratio:.1f})'
                confidence = 0.5 - abs(positive_ratio - 1.0) * 0.1  # Lower confidence for mixed signals
        
        else:
            # All neutral or no clear sentiment
            signal = 'HOLD'
            reason = f'No clear sentiment direction detected'
            confidence = 0.4
        
        # Prepare detailed analysis
        details = {
            'total_articles': total_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'positive_percentage': positive_pct,
            'negative_percentage': negative_pct,
            'neutral_percentage': neutral_pct,
            'positive_to_negative_ratio': positive_count / max(negative_count, 1),
            'negative_to_positive_ratio': negative_count / max(positive_count, 1),
            'sentiment_column_used': sentiment_column
        }
        
        return {
            'signal': signal,
            'confidence': round(confidence, 3),
            'reason': reason,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_weighted_signal(self, df: pd.DataFrame, 
                                sentiment_column: str = 'combined_sentiment_label',
                                confidence_column: str = 'combined_sentiment_confidence') -> Dict:
        """
        Generate trading signal considering confidence scores
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis
            sentiment_column (str): Column containing sentiment labels
            confidence_column (str): Column containing confidence scores
            
        Returns:
            dict: Enhanced trading signal with confidence weighting
        """
        if confidence_column not in df.columns:
            # Fall back to basic signal if no confidence column
            return self.generate_basic_signal(df, sentiment_column)
        
        # Get basic signal first
        basic_signal = self.generate_basic_signal(df, sentiment_column)
        
        if basic_signal['signal'] == 'INSUFFICIENT_DATA':
            return basic_signal
        
        # Calculate weighted sentiment scores
        df_copy = df.copy()
        
        # Calculate weighted sentiment contribution
        positive_weight = df_copy[df_copy[sentiment_column] == 'positive'][confidence_column].sum()
        negative_weight = df_copy[df_copy[sentiment_column] == 'negative'][confidence_column].sum()
        neutral_weight = df_copy[df_copy[sentiment_column] == 'neutral'][confidence_column].sum()
        
        total_weight = positive_weight + negative_weight + neutral_weight
        
        if total_weight == 0:
            return basic_signal
        
        # Calculate weighted percentages
        weighted_positive_pct = (positive_weight / total_weight) * 100
        weighted_negative_pct = (negative_weight / total_weight) * 100
        weighted_neutral_pct = (neutral_weight / total_weight) * 100
        
        # Generate enhanced signal
        signal = basic_signal['signal']
        confidence = basic_signal['confidence']
        reason = basic_signal['reason']
        
        # Adjust based on weighted analysis
        if weighted_positive_pct > weighted_negative_pct * self.positive_threshold:
            if signal != 'BUY':
                signal = 'BUY'
                reason = f'Weighted analysis: {weighted_positive_pct:.1f}% positive vs {weighted_negative_pct:.1f}% negative'
            confidence = min(0.95, confidence + self.confidence_weight * 0.2)
            
        elif weighted_negative_pct > weighted_positive_pct * self.negative_threshold:
            if signal != 'SELL':
                signal = 'SELL'
                reason = f'Weighted analysis: {weighted_negative_pct:.1f}% negative vs {weighted_positive_pct:.1f}% positive'
            confidence = min(0.95, confidence + self.confidence_weight * 0.2)
        
        # Update details with weighted information
        enhanced_details = basic_signal['details'].copy()
        enhanced_details.update({
            'weighted_positive_percentage': weighted_positive_pct,
            'weighted_negative_percentage': weighted_negative_pct,
            'weighted_neutral_percentage': weighted_neutral_pct,
            'confidence_column_used': confidence_column,
            'total_confidence_weight': total_weight
        })
        
        return {
            'signal': signal,
            'confidence': round(confidence, 3),
            'reason': reason,
            'details': enhanced_details,
            'timestamp': datetime.now().isoformat()
        }
    
    def _normalize_datetime_columns(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Helper method to normalize datetime columns and handle timezone issues
        
        Args:
            df (pd.DataFrame): DataFrame with datetime column
            date_column (str): Name of the datetime column
            
        Returns:
            pd.DataFrame: DataFrame with normalized datetime column
        """
        df_copy = df.copy()
        
        # Ensure the column is datetime
        df_copy[date_column] = pd.to_datetime(df_copy[date_column])
        
        # Convert to timezone-naive UTC if timezone-aware
        if df_copy[date_column].dt.tz is not None:
            df_copy[date_column] = df_copy[date_column].dt.tz_convert('UTC').dt.tz_localize(None)
        
        return df_copy
    
    def generate_time_weighted_signal(self, df: pd.DataFrame, 
                                     sentiment_column: str = 'combined_sentiment_label',
                                     date_column: str = 'published_at',
                                     recent_days: int = 7) -> Dict:
        """
        Generate trading signal with more weight given to recent articles
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis
            sentiment_column (str): Column containing sentiment labels
            date_column (str): Column containing publication dates
            recent_days (int): Number of recent days to give more weight
            
        Returns:
            dict: Time-weighted trading signal
        """
        if date_column not in df.columns:
            return self.generate_weighted_signal(df, sentiment_column)
        
        try:
            # Normalize datetime columns to avoid timezone issues
            df_copy = self._normalize_datetime_columns(df, date_column)
            
            # Use timezone-naive current time
            current_time = pd.Timestamp.now().replace(tzinfo=None)
            
            # Calculate recency weights
            df_copy['days_ago'] = (current_time - df_copy[date_column]).dt.days
            
            # Handle negative days (future dates) by setting them to 0
            df_copy['days_ago'] = df_copy['days_ago'].clip(lower=0)
            
        except Exception as e:
            print(f"Warning: Could not calculate time weights due to datetime issues: {e}")
            print("Falling back to weighted signal analysis...")
            return self.generate_weighted_signal(df, sentiment_column)
        
        # Recent articles get higher weight
        df_copy['time_weight'] = np.where(
            df_copy['days_ago'] <= recent_days,
            2.0,  # Double weight for recent articles
            1.0   # Normal weight for older articles
        )
        
        # Calculate time-weighted sentiment counts
        time_weighted_positive = df_copy[df_copy[sentiment_column] == 'positive']['time_weight'].sum()
        time_weighted_negative = df_copy[df_copy[sentiment_column] == 'negative']['time_weight'].sum()
        time_weighted_neutral = df_copy[df_copy[sentiment_column] == 'neutral']['time_weight'].sum()
        
        total_time_weight = time_weighted_positive + time_weighted_negative + time_weighted_neutral
        
        # Get base signal
        base_signal = self.generate_weighted_signal(df, sentiment_column)
        
        if total_time_weight == 0:
            return base_signal
        
        # Calculate time-weighted ratios
        time_positive_pct = (time_weighted_positive / total_time_weight) * 100
        time_negative_pct = (time_weighted_negative / total_time_weight) * 100
        
        # Generate time-adjusted signal
        signal = base_signal['signal']
        confidence = base_signal['confidence']
        reason = base_signal['reason']
        
        if time_weighted_positive > time_weighted_negative * self.positive_threshold:
            signal = 'BUY'
            reason = f'Time-weighted analysis favors BUY: {time_positive_pct:.1f}% positive (recent articles weighted 2x)'
            confidence = min(0.95, confidence + 0.1)
            
        elif time_weighted_negative > time_weighted_positive * self.negative_threshold:
            signal = 'SELL'
            reason = f'Time-weighted analysis favors SELL: {time_negative_pct:.1f}% negative (recent articles weighted 2x)'
            confidence = min(0.95, confidence + 0.1)
        
        # Enhanced details
        enhanced_details = base_signal['details'].copy()
        enhanced_details.update({
            'time_weighted_positive_percentage': time_positive_pct,
            'time_weighted_negative_percentage': time_negative_pct,
            'recent_days_threshold': recent_days,
            'articles_in_recent_period': len(df_copy[df_copy['days_ago'] <= recent_days])
        })
        
        return {
            'signal': signal,
            'confidence': round(confidence, 3),
            'reason': reason,
            'details': enhanced_details,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_signal_summary(self, signal_result: Dict) -> str:
        """
        Generate a human-readable summary of the trading signal
        
        Args:
            signal_result (dict): Result from signal generation methods
            
        Returns:
            str: Formatted summary string
        """
        signal = signal_result['signal']
        confidence = signal_result['confidence']
        reason = signal_result['reason']
        details = signal_result['details']
        
        emoji_map = {
            'BUY': '🟢 📈',
            'SELL': '🔴 📉',
            'HOLD': '🟡 ➡️',
            'INSUFFICIENT_DATA': '⚪ ❓'
        }
        
        summary = f"\n{'='*60}\n"
        summary += f"🚦 TRADING SIGNAL ANALYSIS\n"
        summary += f"{'='*60}\n"
        summary += f"Signal: {emoji_map.get(signal, '❓')} {signal}\n"
        summary += f"Confidence: {confidence:.1%}\n"
        summary += f"Reason: {reason}\n"
        summary += f"\n📊 SENTIMENT BREAKDOWN:\n"
        summary += f"Total Articles: {details.get('total_articles', 0)}\n"
        summary += f"Positive: {details.get('positive_count', 0)} ({details.get('positive_percentage', 0):.1f}%)\n"
        summary += f"Negative: {details.get('negative_count', 0)} ({details.get('negative_percentage', 0):.1f}%)\n"
        summary += f"Neutral: {details.get('neutral_count', 0)} ({details.get('neutral_percentage', 0):.1f}%)\n"
        
        if 'positive_to_negative_ratio' in details:
            summary += f"\n📈 RATIOS:\n"
            summary += f"Positive/Negative Ratio: {details['positive_to_negative_ratio']:.2f}\n"
            summary += f"Negative/Positive Ratio: {details['negative_to_positive_ratio']:.2f}\n"
        
        summary += f"\n⏰ Generated: {signal_result['timestamp']}\n"
        summary += f"{'='*60}\n"
        
        return summary

# Convenience function for quick signal generation
def generate_trading_signal(df: pd.DataFrame, 
                           sentiment_column: str = 'combined_sentiment_label',
                           method: str = 'basic') -> Dict:
    """
    Quick function to generate trading signal
    
    Args:
        df (pd.DataFrame): DataFrame with sentiment analysis
        sentiment_column (str): Column containing sentiment labels
        method (str): Method to use ('basic', 'weighted', 'time_weighted')
        
    Returns:
        dict: Trading signal result
    """
    generator = TradingSignalGenerator()
    
    if method == 'basic':
        return generator.generate_basic_signal(df, sentiment_column)
    elif method == 'weighted':
        return generator.generate_weighted_signal(df, sentiment_column)
    elif method == 'time_weighted':
        return generator.generate_time_weighted_signal(df, sentiment_column)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'basic', 'weighted', or 'time_weighted'")