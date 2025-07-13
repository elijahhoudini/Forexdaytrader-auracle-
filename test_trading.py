#!/usr/bin/env python3
"""
AURACLE Manual Trading Test
========================

Test script to verify manual buy/sell functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from buy_sell import buy, sell, auracle_trading
import config

def test_manual_trading():
    """Test manual trading functions"""
    print("🧪 Testing AURACLE Manual Trading Functions")
    print("=" * 50)
    
    # Mock bot object for testing
    class MockBot:
        def send_message(self, chat_id, message):
            print(f"📱 [TELEGRAM] {message}")
    
    mock_bot = MockBot()
    test_chat_id = 123456789
    test_token_address = "So11111111111111111111111111111111111111112"  # SOL mint
    
    print(f"🔧 Current mode: {config.get_trading_mode_string()}")
    print(f"💰 Wallet balance: {auracle_trading.get_wallet_balance()} SOL")
    print()
    
    print("🛒 Testing BUY function...")
    try:
        buy(mock_bot, test_chat_id, test_token_address, 0.01)
        print("✅ Buy function executed successfully")
    except Exception as e:
        print(f"❌ Buy function failed: {e}")
    
    print()
    print("🛒 Testing SELL function...")
    try:
        sell(mock_bot, test_chat_id, test_token_address, 25.0)  # Sell 25%
        print("✅ Sell function executed successfully")
    except Exception as e:
        print(f"❌ Sell function failed: {e}")
    
    print()
    print("📊 Trade Handler Portfolio Summary:")
    try:
        summary = auracle_trading.trade_handler.get_portfolio_summary()
        print(f"   Open positions: {summary['open_positions']}")
        print(f"   Total invested: {summary['total_invested_sol']} SOL")
        print(f"   Total value: {summary['total_value']:.6f} SOL")
        print(f"   Daily trades: {summary['daily_trades']}")
    except Exception as e:
        print(f"❌ Portfolio summary failed: {e}")
    
    print()
    print("🏁 Manual trading test completed!")

if __name__ == "__main__":
    test_manual_trading()