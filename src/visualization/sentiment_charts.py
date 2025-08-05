import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, List, Optional
import os

class SentimentVisualizer:
    """
    A class to create visualizations for sentiment analysis results
    """
    
    def __init__(self, style='seaborn-v0_8', figsize=(10, 6)):
        """
        Initialize the visualizer
        
        Args:
            style (str): Matplotlib style
            figsize (tuple): Default figure size
        """
        plt.style.use('default')  # Use default style as seaborn styles may not be available
        self.figsize = figsize
        self.colors = {
            'positive': '#2E8B57',  # Sea Green
            'negative': '#DC143C',  # Crimson
            'neutral': '#4682B4'    # Steel Blue
        }
    
    def create_sentiment_bar_chart(self, df: pd.DataFrame, sentiment_column: str = 'title_sentiment_label', 
                                  title: str = None, save_path: str = None) -> str:
        """
        Create a bar chart showing sentiment distribution
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis results
            sentiment_column (str): Column containing sentiment labels
            title (str): Chart title
            save_path (str): Path to save the chart
            
        Returns:
            str: Path where the chart was saved
        """
        if sentiment_column not in df.columns:
            raise ValueError(f"Column '{sentiment_column}' not found in DataFrame")
        
        # Count sentiment distribution
        sentiment_counts = df[sentiment_column].value_counts()
        
        # Ensure all three categories are present
        for sentiment in ['positive', 'negative', 'neutral']:
            if sentiment not in sentiment_counts.index:
                sentiment_counts[sentiment] = 0
        
        # Reorder for consistent display
        sentiment_counts = sentiment_counts.reindex(['positive', 'neutral', 'negative'])
        
        # Calculate percentages
        total_articles = len(df)
        sentiment_percentages = (sentiment_counts / total_articles * 100).round(1)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Create bars
        bars = ax.bar(sentiment_counts.index, sentiment_counts.values, 
                     color=[self.colors[sentiment] for sentiment in sentiment_counts.index],
                     alpha=0.8, edgecolor='black', linewidth=1)
        
        # Customize the chart
        if title is None:
            title = f'Sentiment Distribution of News Articles'
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Sentiment', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        
        # Add value labels on bars
        for i, (bar, count, percentage) in enumerate(zip(bars, sentiment_counts.values, sentiment_percentages.values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + total_articles * 0.01,
                   f'{count}\n({percentage}%)', 
                   ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        # Customize appearance
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Set y-axis to start from 0 and add some padding
        ax.set_ylim(0, max(sentiment_counts.values) * 1.15)
        
        # Capitalize x-axis labels
        ax.set_xticklabels([label.capitalize() for label in sentiment_counts.index])
        
        # Add a subtle background
        ax.set_facecolor('#f8f9fa')
        
        plt.tight_layout()
        
        # Save the chart - FIX: Ensure directory exists
        if save_path is None:
            save_path = self._generate_save_path('sentiment_distribution.png')
        else:
            # Ensure the directory exists for the provided save_path
            save_dir = os.path.dirname(save_path)
            if save_dir:  # Only create if there's a directory component
                os.makedirs(save_dir, exist_ok=True)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Chart saved to: {save_path}")
        
        # Show the plot (optional)
        plt.show()
        
        return save_path
    
    def create_comprehensive_sentiment_chart(self, df: pd.DataFrame, save_path: str = None) -> str:
        """
        Create a comprehensive chart showing sentiment for title, description, and combined
        
        Args:
            df (pd.DataFrame): DataFrame with comprehensive sentiment analysis
            save_path (str): Path to save the chart
            
        Returns:
            str: Path where the chart was saved
        """
        # Check if comprehensive analysis columns exist
        analysis_types = []
        if 'title_sentiment_label' in df.columns:
            analysis_types.append('title')
        if 'description_sentiment_label' in df.columns:
            analysis_types.append('description')
        if 'combined_sentiment_label' in df.columns:
            analysis_types.append('combined')
        
        if not analysis_types:
            raise ValueError("No sentiment analysis columns found in DataFrame")
        
        # Prepare data for plotting
        sentiment_data = []
        for analysis_type in analysis_types:
            col_name = f'{analysis_type}_sentiment_label'
            counts = df[col_name].value_counts()
            
            for sentiment in ['positive', 'neutral', 'negative']:
                sentiment_data.append({
                    'analysis_type': analysis_type.capitalize(),
                    'sentiment': sentiment.capitalize(),
                    'count': counts.get(sentiment, 0),
                    'percentage': (counts.get(sentiment, 0) / len(df)) * 100
                })
        
        sentiment_df = pd.DataFrame(sentiment_data)
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: Grouped bar chart (counts)
        pivot_counts = sentiment_df.pivot(index='analysis_type', columns='sentiment', values='count')
        pivot_counts.plot(kind='bar', ax=ax1, color=[self.colors[s.lower()] for s in pivot_counts.columns],
                         alpha=0.8, edgecolor='black', linewidth=1)
        
        ax1.set_title('Sentiment Distribution by Analysis Type\n(Article Counts)', 
                     fontsize=14, fontweight='bold')
        ax1.set_xlabel('Analysis Type', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        ax1.legend(title='Sentiment', title_fontsize=11, fontsize=10)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
        
        # Plot 2: Stacked percentage bar chart
        pivot_pct = sentiment_df.pivot(index='analysis_type', columns='sentiment', values='percentage')
        pivot_pct.plot(kind='bar', stacked=True, ax=ax2, 
                      color=[self.colors[s.lower()] for s in pivot_pct.columns],
                      alpha=0.8, edgecolor='black', linewidth=1)
        
        ax2.set_title('Sentiment Distribution by Analysis Type\n(Percentages)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Analysis Type', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Percentage (%)', fontsize=12, fontweight='bold')
        ax2.legend(title='Sentiment', title_fontsize=11, fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # Save the chart
        if save_path is None:
            save_path = self._generate_save_path('comprehensive_sentiment_analysis.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Comprehensive chart saved to: {save_path}")
        
        plt.show()
        
        return save_path
    
    def create_sentiment_timeline(self, df: pd.DataFrame, sentiment_column: str = 'title_sentiment_label',
                                 save_path: str = None) -> str:
        """
        Create a timeline chart showing sentiment over time
        
        Args:
            df (pd.DataFrame): DataFrame with sentiment analysis and date columns
            sentiment_column (str): Column containing sentiment labels
            save_path (str): Path to save the chart
            
        Returns:
            str: Path where the chart was saved
        """
        if 'published_at' not in df.columns:
            raise ValueError("'published_at' column not found in DataFrame")
        
        if sentiment_column not in df.columns:
            raise ValueError(f"Column '{sentiment_column}' not found in DataFrame")
        
        # Prepare data
        df_copy = df.copy()
        df_copy['date'] = pd.to_datetime(df_copy['published_at']).dt.date
        
        # Group by date and sentiment
        daily_sentiment = df_copy.groupby(['date', sentiment_column]).size().unstack(fill_value=0)
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot lines for each sentiment
        for sentiment in ['positive', 'negative', 'neutral']:
            if sentiment in daily_sentiment.columns:
                ax.plot(daily_sentiment.index, daily_sentiment[sentiment], 
                       marker='o', linewidth=2, label=sentiment.capitalize(),
                       color=self.colors[sentiment], alpha=0.8)
        
        ax.set_title('Sentiment Trends Over Time', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Articles', fontsize=12, fontweight='bold')
        ax.legend(title='Sentiment', title_fontsize=11, fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Save the chart
        if save_path is None:
            save_path = self._generate_save_path('sentiment_timeline.png')
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Timeline chart saved to: {save_path}")
        
        plt.show()
        
        return save_path
    
    def _generate_save_path(self, filename: str) -> str:
        """
        Generate save path for charts
        
        Args:
            filename (str): Name of the file
            
        Returns:
            str: Full path where to save the chart
        """
        # Create charts directory if it doesn't exist
        charts_dir = os.path.join('data', 'charts')
        os.makedirs(charts_dir, exist_ok=True)
        
        return os.path.join(charts_dir, filename)

def create_simple_sentiment_chart(csv_filepath: str, sentiment_column: str = 'title_sentiment_label'):
    """
    Simple function to create a sentiment bar chart from a CSV file
    
    Args:
        csv_filepath (str): Path to CSV file with sentiment data
        sentiment_column (str): Column containing sentiment labels
    """
    try:
        # Load data
        df = pd.read_csv(csv_filepath)
        print(f"Loaded {len(df)} articles from {csv_filepath}")
        
        # Create visualizer
        visualizer = SentimentVisualizer()
        
        # Extract company name from file path for title
        filename = os.path.basename(csv_filepath)
        company_name = filename.replace('_', ' ').replace('.csv', '').title()
        
        # Create chart
        title = f'Sentiment Distribution - {company_name}'
        save_path = visualizer.create_sentiment_bar_chart(
            df, sentiment_column, title=title
        )
        
        return save_path
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None