#!/usr/bin/env python3
"""
Simple launcher for the Trading Signal Web App
"""
import os
import sys
from pathlib import Path

# Change to src directory
src_dir = Path(__file__).parent / 'src'
os.chdir(src_dir)

# Add src to Python path
sys.path.insert(0, str(src_dir))

print("🚀 Starting Trading Signal Web Application...")
print("📊 Analyze any company's news sentiment for trading signals")
print("🌐 Open http://localhost:5001 in your browser")
print("⏰ First analysis may take 1-2 minutes to load models")
print("💡 Try companies like: Apple Inc, Tesla Inc, Microsoft Corporation")
print("-" * 60)

# Import and run the Flask app
try:
    from app import app
    app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)
except KeyboardInterrupt:
    print("\n👋 Web app stopped by user")
except Exception as e:
    print(f"❌ Error starting web app: {e}")