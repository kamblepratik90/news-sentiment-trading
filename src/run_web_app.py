import os
import sys
from pathlib import Path

def main():
    """Launch the trading signal web application"""
    
    # Change to the web app directory
    web_app_dir = Path(__file__).parent / 'web_app'
    os.chdir(web_app_dir)
    
    # Add the src directory to Python path
    src_dir = Path(__file__).parent
    sys.path.insert(0, str(src_dir))
    
    print("🚀 Starting Trading Signal Web Application...")
    print("📊 This will run the complete news sentiment analysis pipeline")
    print("🌐 Open http://localhost:5001 in your browser")
    print("⏰ First analysis may take 1-2 minutes to load models")
    print("-" * 60)
    
    # Import and run the Flask app
    from web_app.app import app
    app.run(debug=True, host='0.0.0.0', port=5001)

if __name__ == "__main__":
    main()