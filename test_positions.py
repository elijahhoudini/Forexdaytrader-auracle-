#!/usr/bin/env python3
"""
AURACLE Position Monitoring Test
============================

Test script to verify position monitoring and profit/loss calculations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trade import TradeHandler
from wallet import Wallet
import config
import time

def test_position_monitoring():
    """Test position monitoring and stop loss/take profit"""
    print("🧪 Testing AURACLE Position Monitoring")
    print("=" * 50)
    
    # Initialize components
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    
    print(f"🔧 Current mode: {config.get_trading_mode_string()}")
    print(f"💰 Wallet balance: {wallet.get_balance()} SOL")
    print()
    
    # Create some test positions
    test_tokens = [
        {
            "mint": "test_token_1",
            "symbol": "TEST1",
            "name": "Test Token 1",
            "liquidity": 50000,
            "volume24h": 10000,
            "priceChange24h": 0.05,
            "fdv": 1000000,
            "holders": 200
        },
        {
            "mint": "test_token_2", 
            "symbol": "TEST2",
            "name": "Test Token 2",
            "liquidity": 75000,
            "volume24h": 15000,
            "priceChange24h": -0.02,
            "fdv": 2000000,
            "holders": 300
        }
    ]
    
    print("🛒 Creating test positions...")
    for token in test_tokens:
        amount = 0.01
        success = trade_handler.buy_token(token, amount)
        if success:
            print(f"✅ Created position: {token['symbol']} - {amount} SOL")
        else:
            print(f"❌ Failed to create position: {token['symbol']}")
    
    print()
    print("📊 Initial Portfolio Summary:")
    summary = trade_handler.get_portfolio_summary()
    print(f"   Open positions: {summary['open_positions']}")
    print(f"   Total invested: {summary['total_invested_sol']:.6f} SOL")
    print(f"   Total value: {summary['total_value']:.6f} SOL")
    print(f"   Daily trades: {summary['daily_trades']}")
    
    print()
    print("🔍 Testing position monitoring...")
    for i in range(3):
        print(f"   Monitoring cycle {i+1}...")
        trade_handler.monitor_positions()
        time.sleep(1)
    
    print()
    print("📊 Final Portfolio Summary:")
    final_summary = trade_handler.get_portfolio_summary()
    print(f"   Open positions: {final_summary['open_positions']}")
    print(f"   Total invested: {final_summary['total_invested_sol']:.6f} SOL")
    print(f"   Total value: {final_summary['total_value']:.6f} SOL")
    print(f"   Daily trades: {final_summary['daily_trades']}")
    
    print()
    print("📈 Recent trades:")
    for trade in final_summary['recent_trades']:
        action = trade['action']
        if action == 'BUY':
            print(f"   📈 BUY: {trade['token']['symbol']} - {trade['amount']} SOL")
        elif action == 'SELL':
            print(f"   📉 SELL: {trade['symbol']} - P&L: {trade['pnl_percent']:.2f}%")
    
    print()
    print("🏁 Position monitoring test completed!")

if __name__ == "__main__":
    test_position_monitoring()