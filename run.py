#!/usr/bin/env python3
"""
AURACLE Simple Runner
====================

Simple script to run AURACLE bot in production mode.
Use this for easy deployment and testing.
"""

import subprocess
import sys
import os

def main():
    """Main runner function"""
    print("🚀 AURACLE Production Bot Runner")
    print("================================")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check if we're in the right directory
    if not os.path.exists("start_production.py"):
        print("❌ Please run from the AURACLE directory")
        return False
    
    # Run the production bot
    try:
        print("🔄 Starting AURACLE production bot...")
        result = subprocess.run([sys.executable, "start_production.py"], 
                              capture_output=False, text=True)
        return result.returncode == 0
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running bot: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)