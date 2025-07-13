
#!/usr/bin/env python3
"""
AURACLE Startup Script
======================

Simple script to start AURACLE with proper initialization.
"""

import sys
import os
import time

def check_dependencies():
    """Check if required modules are available."""
    required_modules = ['requests', 'pandas', 'datetime', 'json', 'threading']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("📝 Installing basic dependencies...")
        return False
    return True

def main():
    """Main startup function."""
    print("🤖 AURACLE Bot Startup")
    print("=" * 40)
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    print("✅ Data directory ready")
    
    # Check dependencies
    if not check_dependencies():
        print("⚠️ Some dependencies missing, but continuing with basic setup...")
    
    print("\n🚀 Starting AURACLE...")
    print("=" * 40)
    
    try:
        # Import and run AURACLE
        from auracle import main as auracle_main
        auracle_main()
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("🔧 Check your configuration in config.py")
        sys.exit(1)

if __name__ == "__main__":
    main()
