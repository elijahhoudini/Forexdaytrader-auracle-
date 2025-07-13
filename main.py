
"""
AURACLE Main Entry Point
========================

Simple entry point that starts the AURACLE bot.
"""

import sys
import os

if __name__ == "__main__":
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Try to import and run auracle
        try:
            from auracle import main
            main()
        except ImportError:
            # Fallback to simple bot if auracle module has issues
            print("⚠️ Using fallback bot implementation")
            exec(open("AURACLE_bot.py").read())
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")
        import traceback
        traceback.print_exc()
