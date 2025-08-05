from transformers import pipeline
import warnings
warnings.filterwarnings("ignore")

def analyze_sentiment(text: str, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english") -> str:
    """
    Quick sentiment analysis function that returns simple labels
    
    Args:
        text (str): Text to analyze
        model_name (str): Hugging Face model name
        
    Returns:
        str: 'positive', 'negative', or 'neutral'
    """
    if not text or text.strip() == "":
        return 'neutral'
    
    try:
        # Initialize pipeline (cache it for better performance)
        if not hasattr(analyze_sentiment, 'pipeline'):
            analyze_sentiment.pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                return_all_scores=True
            )
        
        # Truncate text if too long
        text = text[:512]
        
        # Get sentiment
        results = analyze_sentiment.pipeline(text)[0]
        
        # Find positive and negative scores
        positive_score = 0.0
        negative_score = 0.0
        
        for result in results:
            if result['label'].upper() in ['POSITIVE', 'POS']:
                positive_score = result['score']
            elif result['label'].upper() in ['NEGATIVE', 'NEG']:
                negative_score = result['score']
        
        # Determine sentiment with threshold
        if positive_score > negative_score and positive_score > 0.6:
            return 'positive'
        elif negative_score > positive_score and negative_score > 0.6:
            return 'negative'
        else:
            return 'neutral'
            
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return 'neutral'

# Example usage function
def test_sentiment_function():
    """Test the sentiment analysis function with sample texts"""
    test_texts = [
        "The company reported excellent quarterly results with record profits!",
        "Stock prices plummeted amid concerns about the company's future.",
        "The company announced a new product launch for next quarter.",
        "Reliance Industries continues to expand its operations."
    ]
    
    print("Testing sentiment analysis function:")
    print("-" * 50)
    
    for text in test_texts:
        sentiment = analyze_sentiment(text)
        print(f"Text: {text}")
        print(f"Sentiment: {sentiment}")
        print("-" * 50)

if __name__ == "__main__":
    test_sentiment_function()