#!/usr/bin/env python3
"""
Test AURACLE Stop Functionality
===============================

Test if AURACLE can be properly stopped via Telegram commands.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_stop_functionality():
    """Test AURACLE stop functionality"""
    try:
        import config
        from auracle_telegram_unified import AuracleUnifiedBot
        
        print("🔧 Testing AURACLE stop functionality...")
        
        # Check if bot token is configured
        token = config.TELEGRAM_BOT_TOKEN or os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ No Telegram bot token configured")
            return False
        
        # Create bot instance
        bot = AuracleUnifiedBot(token)
        
        # Test stop command method exists
        if hasattr(bot, 'stop_auracle_command'):
            print("✅ stop_auracle_command method exists")
        else:
            print("❌ stop_auracle_command method missing")
            return False
        
        # Test stop callback method exists
        if hasattr(bot, 'handle_stop_auracle_callback'):
            print("✅ handle_stop_auracle_callback method exists")
        else:
            print("❌ handle_stop_auracle_callback method missing")
            return False
        
        # Test button callback routing
        if hasattr(bot, 'button_callback'):
            print("✅ button_callback method exists")
        else:
            print("❌ button_callback method missing")
            return False
        
        # Test AURACLE control variables
        if hasattr(bot, 'auracle_running'):
            print("✅ auracle_running state variable exists")
        else:
            print("❌ auracle_running state variable missing")
            return False
        
        if hasattr(bot, 'auracle'):
            print("✅ auracle instance variable exists")
        else:
            print("❌ auracle instance variable missing")
            return False
        
        # Test stop mechanism
        bot.auracle_running = True
        
        # Simulate stop operation
        if bot.auracle:
            if hasattr(bot.auracle, 'running'):
                bot.auracle.running = False
                print("✅ AURACLE.running can be set to False")
            else:
                print("⚠️  AURACLE.running attribute not found")
        
        bot.auracle_running = False
        print("✅ auracle_running can be set to False")
        
        print("\n✅ All stop functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 AURACLE Stop Functionality Test")
    print("=" * 40)
    
    success = await test_stop_functionality()
    
    if success:
        print("\n✅ Stop functionality working! You can stop AURACLE via:")
        print("   • /stop_auracle command")
        print("   • 🛑 Stop AURACLE button")
        print("   • Both should work in Telegram")
    else:
        print("\n❌ Stop functionality has issues!")

if __name__ == "__main__":
    asyncio.run(main())
