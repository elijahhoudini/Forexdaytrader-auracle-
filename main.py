
"""
AURACLE Main Entry Point
========================

Simple entry point that starts the AURACLE bot.
"""

import sys
import os

def main():
    """Main entry point for AURACLE bot."""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Import and run auracle
        print("🚀 Starting AURACLE bot...")
        from auracle import Auracle
        
        # Create and run the bot
        bot = Auracle()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")
        import traceback
        traceback.print_exc()
        
        # Try fallback bot as last resort
        try:
            print("⚠️ Attempting fallback bot implementation...")
            exec(open("AURACLE_bot.py").read())
        except Exception as fallback_error:
            print(f"❌ Fallback bot also failed: {fallback_error}")

if __name__ == "__main__":
    main()
