#!/usr/bin/env python3
"""
AURACLE Bot - Replit Startup Script
==================================

This script starts the AURACLE bot optimized for Replit deployment.
"""

import os
import sys

def main():
    """Start AURACLE bot with Replit optimizations."""
    
    print("🚀 AURACLE Bot - Replit Deployment")
    print("=" * 50)
    
    # Set environment variables for Replit
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("TELEGRAM_ENABLED", "true")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import and run the main bot
    try:
        from main import main as bot_main
        bot_main()
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()