#!/usr/bin/env python3
"""
Test Jupiter API with Real Transaction
====================================

Test the current Jupiter API implementation with a small real transaction.
"""

import asyncio
from jupiter_api import JupiterTradeExecutor
from wallet import Wallet
import config

async def test_jupiter_trade():
    """Test Jupiter API with a real small trade"""
    
    print("🧪 Testing Jupiter API with Real Trade")
    print("=" * 50)
    
    # Initialize wallet and Jupiter
    wallet = Wallet()
    jupiter = JupiterTradeExecutor(wallet.keypair)
    
    # Get current balance
    balance = await wallet.get_balance()
    print(f"💰 Current balance: {balance:.4f} SOL")
    
    if balance < 0.005:
        print("❌ Insufficient balance for test trade")
        return
    
    # Test with tiny amount - 0.001 SOL to USDC
    test_amount = 0.001
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    
    print(f"\n🔄 Testing trade: {test_amount} SOL → USDC")
    print(f"📍 USDC mint: {usdc_mint}")
    
    try:
        # Execute the trade
        result = await jupiter.buy_token(usdc_mint, test_amount)
        
        if result.get('success'):
            print(f"✅ Trade successful!")
            print(f"📄 Signature: {result.get('signature')}")
            print(f"⚡ Output amount: {result.get('output_amount')}")
            
            # Check new balance
            new_balance = await wallet.get_balance()
            print(f"💰 New balance: {new_balance:.4f} SOL")
            print(f"📊 Change: {new_balance - balance:+.4f} SOL")
            
            return True
        else:
            print(f"❌ Trade failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    success = await test_jupiter_trade()
    
    if success:
        print("\n✅ Jupiter API is working correctly!")
        print("🎯 The issue may be in the trade execution logic")
    else:
        print("\n❌ Jupiter API still has issues")
        print("🔧 Need to debug transaction signing further")

if __name__ == "__main__":
    asyncio.run(main())
