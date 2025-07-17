#!/usr/bin/env python3
"""
ROYAL EARNING Bot System Startup Script
This script starts both the Telegram bot and the Flask admin panel
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def start_system():
    """Start the complete ROYAL EARNING bot system"""
    print("=" * 60)
    print("🎉 ROYAL EARNING Bot System")
    print("=" * 60)
    print("🚀 Starting system components...")
    
    try:
        # Import and start the main application
        from app import app, start_bot_in_thread
        
        # Start the Telegram bot in a separate thread
        print("🤖 Initializing Telegram bot...")
        bot_thread = threading.Thread(target=start_bot_in_thread, daemon=True)
        bot_thread.start()
        
        # Give the bot a moment to initialize
        time.sleep(2)
        
        # Start the Flask admin panel
        print("📊 Starting admin panel...")
        print(f"🌐 Admin Panel URL: http://localhost:{os.getenv('FLASK_PORT', 5000)}")
        print(f"👤 Admin Username: {os.getenv('ADMIN_USERNAME', 'royal_earning')}")
        print(f"🔑 Admin Password: {os.getenv('ADMIN_PASSWORD', 'Rishi@748')}")
        print("=" * 60)
        
        app.run(
            host=os.getenv('FLASK_HOST', '0.0.0.0'),
            port=int(os.getenv('FLASK_PORT', 5000)),
            debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
        )
        
    except KeyboardInterrupt:
        print("\n🛑 System shutdown requested...")
        print("👋 ROYAL EARNING Bot System stopped.")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_system()

