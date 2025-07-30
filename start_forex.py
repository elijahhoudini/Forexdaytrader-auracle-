#!/usr/bin/env python3
"""
AURACLE Forex Trading Bot Launcher
==================================

Main entry point for the AURACLE Forex trading bot.
Provides different modes: autonomous, interactive, and testing.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def print_banner():
    """Print AURACLE Forex banner."""
    print("=" * 70)
    print("🤖 AURACLE FOREX TRADING BOT v2.0")
    print("🌍 Autonomous Currency Trading Platform")
    print("💱 Major Pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD")
    print("=" * 70)

def check_dependencies():
    """Check if required dependencies are installed."""
    required_modules = [
        'pandas', 'numpy', 'aiohttp', 'requests', 'dotenv'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module.replace('-', '_'))
        except ImportError:
            missing.append(module)
    
    if missing:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("📦 Install with: pip install -r requirements.forex.txt")
        return False
    
    print("✅ All dependencies available")
    return True

def setup_directories():
    """Create necessary directories."""
    directories = [
        'data/forex',
        'logs',
        'data/forex/historical',
        'data/forex/trades'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created")

def check_configuration():
    """Check if configuration is valid."""
    try:
        import forex_config
        status = forex_config.validate_config()
        
        if not status['valid']:
            print("❌ Configuration validation failed")
            print("💡 Copy .env.forex.example to .env and configure your API keys")
            return False
        
        if status['warnings']:
            print("⚠️  Configuration warnings detected")
            for warning in status['warnings']:
                print(f"   - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def run_autonomous_mode():
    """Run in autonomous trading mode."""
    try:
        from auracle_forex import AuracleForex
        
        print("🚀 Starting Autonomous Trading Mode")
        print("⚠️  This mode will execute real trades in live mode!")
        
        # Confirm in non-demo mode
        import forex_config
        if not forex_config.FOREX_DEMO_MODE:
            confirm = input("⚠️  LIVE TRADING MODE - Type 'CONFIRM' to proceed: ")
            if confirm != 'CONFIRM':
                print("❌ Aborted")
                return
        
        auracle = AuracleForex()
        await auracle.run()
        
    except Exception as e:
        print(f"❌ Error in autonomous mode: {e}")

async def run_interactive_mode():
    """Run in interactive manual mode."""
    try:
        from auracle_forex import ForexTradingInterface
        
        print("🎮 Starting Interactive Trading Mode")
        interface = ForexTradingInterface()
        await interface.run_interactive()
        
    except Exception as e:
        print(f"❌ Error in interactive mode: {e}")

async def run_test_mode():
    """Run in testing mode."""
    try:
        print("🧪 Running AURACLE Forex Tests")
        
        # Test configuration
        print("\n1. Testing configuration...")
        if not check_configuration():
            return
        
        # Test market data
        print("\n2. Testing market data...")
        from forex_market_data import test_forex_data
        await test_forex_data()
        
        # Test technical indicators
        print("\n3. Testing technical indicators...")
        from forex_technical_indicators import test_technical_indicators
        test_technical_indicators()
        
        # Test trading engine
        print("\n4. Testing trading engine...")
        from forex_trading_engine import test_forex_trading
        await test_forex_trading()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error in test mode: {e}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AURACLE Forex Trading Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_forex.py --mode auto     # Autonomous trading
  python start_forex.py --mode manual   # Interactive trading
  python start_forex.py --mode test     # Run tests
  python start_forex.py --setup         # Setup wizard
        """
    )
    
    parser.add_argument('--mode', choices=['auto', 'manual', 'test'], 
                       default='test', help='Trading mode (default: test)')
    parser.add_argument('--setup', action='store_true', 
                       help='Run setup wizard')
    parser.add_argument('--check', action='store_true',
                       help='Check configuration and dependencies')
    
    args = parser.parse_args()
    
    print_banner()
    
    # Setup wizard
    if args.setup:
        print("🔧 Setup Wizard")
        setup_directories()
        
        if not Path('.env').exists() and Path('.env.forex.example').exists():
            print("📋 Copying example configuration...")
            import shutil
            shutil.copy('.env.forex.example', '.env')
            print("✅ .env file created from example")
            print("💡 Edit .env file to configure your API keys")
        
        print("✅ Setup completed")
        return
    
    # Dependency check
    if not check_dependencies():
        sys.exit(1)
    
    setup_directories()
    
    # Configuration check
    if args.check:
        if check_configuration():
            print("✅ Configuration is valid")
        else:
            sys.exit(1)
        return
    
    # Run selected mode
    try:
        if args.mode == 'auto':
            asyncio.run(run_autonomous_mode())
        elif args.mode == 'manual':
            asyncio.run(run_interactive_mode())
        elif args.mode == 'test':
            asyncio.run(run_test_mode())
            
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()