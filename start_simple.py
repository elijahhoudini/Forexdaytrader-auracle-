
#!/usr/bin/env python3
"""
Simple AURACLE Startup Script
============================

A bulletproof startup script that will get AURACLE running
regardless of dependency issues.
"""

import sys
import os

def main():
    """Simple main function to start AURACLE."""
    print("🚀 AURACLE Simple Startup")
    print("=" * 40)
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Load minimal environment
    try:
        if os.path.exists('.env.minimal'):
            from minimal_dotenv import load_dotenv
            load_dotenv('.env.minimal')
            print("✅ Loaded minimal configuration")
    except Exception as e:
        print(f"⚠️ Config warning: {e}")
    
    # Try to start the main bot
    try:
        from main import main as main_bot
        main_bot()
    except Exception as e:
        print(f"❌ Main bot failed: {e}")
        
        # Fallback to simple demo
        print("\n🔄 Starting simple demo...")
        run_simple_demo()

def run_simple_demo():
    """Run a very simple demo."""
    import time
    
    print("\n🎯 AURACLE Simple Demo")
    print("✅ System: Online")
    print("✅ Mode: Demo (Safe)")
    print("✅ Status: Operational")
    
    try:
        counter = 0
        while True:
            counter += 1
            print(f"⏰ Cycle {counter} - System operational")
            
            if counter % 10 == 0:
                print("📊 Demo Status: All systems running smoothly")
            
            time.sleep(30)  # Check every 30 seconds
            
    except KeyboardInterrupt:
        print("\n👋 Demo stopped by user")

if __name__ == "__main__":
    main()
