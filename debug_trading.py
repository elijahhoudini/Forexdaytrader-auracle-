#!/usr/bin/env python3
"""
Debug Bot Trading Decisions
===========================

Test bot with actual token discovery to debug buy decisions.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scanner import TokenScanner
from trade import TradeHandler
from wallet import Wallet
from enhanced_discovery import EnhancedTokenDiscovery
import config

async def debug_trading_decisions():
    """Debug why tokens are being skipped."""
    
    print("🔍 Debugging Trading Decisions")
    print("="*60)
    
    # Initialize components
    print("🔧 Initializing components...")
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    discovery = EnhancedTokenDiscovery()
    
    print(f"📊 Demo Mode: {config.get_demo_mode()}")
    print(f"🎯 AI Confidence Threshold: {config.AI_CONFIDENCE_THRESHOLD}")
    print(f"💧 Min Liquidity: {config.MIN_LIQUIDITY_THRESHOLD}")
    print(f"📈 Volume Factor: {config.VOLUME_MOMENTUM_FACTOR}")
    print(f"🛡️ Safety Multiplier: {config.LIQUIDITY_SAFETY_MULTIPLIER}")
    
    # Get some tokens
    print("\n🌐 Discovering tokens...")
    tokens = await discovery.discover_tokens()
    
    if not tokens:
        print("❌ No tokens discovered!")
        return
    
    print(f"✅ Found {len(tokens)} tokens")
    
    # Test buy decisions on first few tokens
    print("\n🧪 Testing buy decisions...")
    for i, token in enumerate(tokens[:3]):
        print(f"\n--- TOKEN {i+1}: {token.get('symbol', 'UNKNOWN')} ---")
        
        # Show token details
        print(f"🏷️  Name: {token.get('name', 'Unknown')}")
        print(f"💧 Liquidity: ${token.get('liquidity', 0):,.0f}")
        print(f"📊 Volume 24h: ${token.get('volume24h', 0):,.0f}")
        print(f"👥 Holders: {token.get('holders', 0)}")
        print(f"📈 Price Change: {token.get('priceChange24h', 0):+.2%}")
        print(f"🎯 Source: {token.get('source', 'Unknown')}")
        
        # Calculate confidence
        confidence = trade_handler._calculate_confidence_score(token)
        print(f"🤖 AI Confidence: {confidence:.3f}")
        
        # Test buy decision
        should_buy = trade_handler.should_buy(token)
        print(f"💰 Buy Decision: {'✅ YES' if should_buy else '❌ NO'}")
        
        if should_buy:
            print("🚀 This token would be purchased!")
        
    print("\n" + "="*60)
    print("🏁 Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_trading_decisions())
