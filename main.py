
#!/usr/bin/env python3
"""
AURACLE Main Entry Point
========================

Production-ready entry point that starts the unified AURACLE bot.
Now uses the production Telegram bot with all required features.
"""

import sys
import os
import asyncio

def main():
    """Main entry point for AURACLE bot."""
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        print("🚀 Starting AURACLE Production Bot...")
        
        # Import and run production bot
        from main_production import main as production_main
        
        # Run the production bot
        asyncio.run(production_main())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")
        import traceback
        traceback.print_exc()
        
        # Try fallback options
        print("⚠️ Attempting fallback methods...")
        
        # Try original auracle implementation
        try:
            print("⚠️ Trying original AURACLE implementation...")
            from auracle import Auracle
            bot = Auracle()
            bot.run()
        except Exception as auracle_error:
            print(f"❌ Original AURACLE failed: {auracle_error}")
            
            # Try the old fallback bot
            try:
                print("⚠️ Trying legacy fallback bot...")
                exec(open("AURACLE_bot.py").read())
            except Exception as fallback_error:
                print(f"❌ All fallback methods failed: {fallback_error}")
                print("❌ Please check configuration and try again")

if __name__ == "__main__":
    main()
