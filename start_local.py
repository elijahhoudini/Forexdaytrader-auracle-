#!/usr/bin/env python3
"""
AURACLE Bot - Local Terminal Launcher
====================================

Simple launcher optimized for local laptop/terminal usage.
No Replit dependencies, minimal configuration required.
"""

import os
import sys
import argparse
from pathlib import Path

def print_banner():
    """Print startup banner."""
    print("=" * 60)
    print("🚀 AURACLE Bot - Local Terminal Mode")
    print("=" * 60)
    print("🖥️  Optimized for local laptop/terminal usage")
    print("📁 Data stored locally in ./data/ directory")
    print("🔶 Safe demo mode enabled by default")
    print()

def check_dependencies():
    """Check if essential dependencies are available."""
    print("📦 Checking dependencies...")
    
    missing_deps = []
    essential_deps = [
        ('solana', 'Solana blockchain client'),
        ('requests', 'HTTP requests library'),
        ('pandas', 'Data analysis library'),
        ('python-dotenv', 'Environment variable loading')
    ]
    
    for dep, desc in essential_deps:
        try:
            if dep == 'python-dotenv':
                __import__('dotenv')
            else:
                __import__(dep.replace('-', '_'))
            print(f"✅ {desc} found")
        except ImportError:
            missing_deps.append(dep)
            print(f"❌ {desc} missing")
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("💡 Run: pip install -r requirements.minimal.txt")
        return False
    
    return True

def setup_local_environment():
    """Set up local environment variables."""
    print("🔧 Setting up local environment...")
    
    # Load .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded .env configuration")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")
    
    # Set safe defaults for local usage
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("TELEGRAM_ENABLED", "false")
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("MAX_BUY_AMOUNT_SOL", "0.01")
    os.environ.setdefault("SCAN_INTERVAL_SECONDS", "60")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    print("✅ Local environment configured")
    return True

def run_auracle():
    """Run the AURACLE autonomous bot."""
    print("🤖 Starting AURACLE Bot (Autonomous Mode)...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, str(Path(__file__).parent))
        
        print("🔍 Loading configuration...")
        import config
        print(f"✅ Configuration loaded - {config.get_trading_mode_string()}")
        
        print("🚀 Starting AURACLE system...")
        from auracle import Auracle
        
        # Create and run bot
        bot = Auracle()
        bot.run()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you've installed dependencies: pip install -r requirements.minimal.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting AURACLE: {e}")
        return False
    
    return True

def run_solbot():
    """Run the Solana Trading Bot (Telegram mode)."""
    print("📱 Starting Solbot (Telegram Mode)...")
    
    try:
        # Add src directory to Python path
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        
        print("🔍 Loading Solbot modules...")
        from solbot.main import main as solbot_main
        
        print("🚀 Starting Solbot...")
        solbot_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure Telegram bot token is configured")
        return False
    except Exception as e:
        print(f"❌ Error starting Solbot: {e}")
        return False
    
    return True

def run_demo_test():
    """Run a simple demo test."""
    print("🔶 Running demo test...")
    
    try:
        # Set demo mode
        os.environ["DEMO_MODE"] = "true"
        os.environ["TELEGRAM_ENABLED"] = "false"
        
        # Add current directory to Python path
        sys.path.insert(0, str(Path(__file__).parent))
        
        # Test configuration loading
        import config
        print(f"✅ Configuration test passed - {config.get_trading_mode_string()}")
        
        # Test basic imports
        from scanner import TokenScanner
        from trade import TradeHandler
        print("✅ Core modules imported successfully")
        
        print("🎉 Demo test completed successfully!")
        print("💡 You can now run the full bot with --bot auracle or --bot solbot")
        
    except Exception as e:
        print(f"❌ Demo test failed: {e}")
        return False
    
    return True

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description='AURACLE Bot - Local Terminal Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python start_local.py --bot auracle     # Run autonomous bot
  python start_local.py --bot solbot      # Run Telegram bot
  python start_local.py --test           # Run demo test
        '''
    )
    
    parser.add_argument('--bot', choices=['auracle', 'solbot'], 
                        help='Which bot to run')
    parser.add_argument('--test', action='store_true',
                        help='Run demo test')
    parser.add_argument('--setup', action='store_true',
                        help='Run setup wizard')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Run setup wizard if requested
    if args.setup:
        print("🛠️  Running setup wizard...")
        os.system("python setup_local.py")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 Run setup first: python start_local.py --setup")
        sys.exit(1)
    
    # Setup environment
    if not setup_local_environment():
        sys.exit(1)
    
    try:
        # Run requested mode
        if args.test:
            success = run_demo_test()
        elif args.bot == 'auracle':
            success = run_auracle()
        elif args.bot == 'solbot':
            success = run_solbot()
        else:
            # Interactive mode
            print("🎯 Interactive Mode")
            print("Choose an option:")
            print("1. Run AURACLE (autonomous trading)")
            print("2. Run Solbot (Telegram controlled)")
            print("3. Run demo test")
            
            choice = input("Enter choice (1-3): ").strip()
            
            if choice == "1":
                success = run_auracle()
            elif choice == "2":
                success = run_solbot()
            elif choice == "3":
                success = run_demo_test()
            else:
                print("❌ Invalid choice")
                success = False
        
        if success:
            print("\n✅ Bot finished successfully")
        else:
            print("\n❌ Bot encountered errors")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()