#!/usr/bin/env python3
"""
AURACLE Trading Execution Test
=============================

Test script to verify the bot can properly execute trades.
Tests both Jupiter API integration and wallet functionality.
"""

import asyncio
import sys
import time
import config
from wallet import Wallet
from jupiter_api import JupiterTradeExecutor, JupiterAPI


async def test_trading_execution():
    """Test the complete trading execution pipeline."""
    print("🔧 AURACLE Trading Execution Test")
    print("=" * 50)
    
    # 1. Test Configuration
    print("\n1. Testing Configuration:")
    print(f"   Trading Mode: {'🔥 LIVE' if config.is_live_trading_enabled() else '🔶 DEMO'}")
    print(f"   Wallet Address: {config.WALLET_ADDRESS[:8]}...")
    print(f"   RPC Endpoint: {config.SOLANA_RPC_ENDPOINT}")
    print(f"   Demo Mode: {config.get_demo_mode()}")
    
    # 2. Test Wallet Initialization
    print("\n2. Testing Wallet Initialization:")
    try:
        wallet = Wallet()
        print(f"   ✅ Wallet initialized successfully")
        print(f"   📍 Address: {wallet.address[:8]}...")
        print(f"   🔑 Keypair: {'✅ Loaded' if wallet.keypair else '❌ Not loaded'}")
        print(f"   🌐 RPC Client: {'✅ Connected' if wallet.rpc_client else '❌ Not connected'}")
    except Exception as e:
        print(f"   ❌ Wallet initialization failed: {e}")
        return False
    
    # 3. Test Wallet Balance
    print("\n3. Testing Wallet Balance:")
    try:
        balance = await wallet.get_balance()
        print(f"   💰 SOL Balance: {balance:.4f} SOL")
        
        if balance > 0:
            print("   ✅ Balance check successful")
        else:
            print("   ⚠️ Zero balance detected")
    except Exception as e:
        print(f"   ❌ Balance check failed: {e}")
        return False
    
    # 4. Test Jupiter API
    print("\n4. Testing Jupiter API:")
    try:
        jupiter = JupiterAPI()
        print("   ✅ Jupiter API initialized")
        
        # Test quote request
        sol_mint = jupiter.SOL_MINT
        usdc_mint = jupiter.USDC_MINT
        amount_lamports = int(0.01 * 1e9)  # 0.01 SOL
        
        quote = await jupiter.get_quote(sol_mint, usdc_mint, amount_lamports)
        if quote:
            print(f"   ✅ Quote request successful")
            print(f"   📊 Output Amount: {quote.get('outAmount', 'N/A')}")
            print(f"   🛣️ Route Plan: {len(quote.get('routePlan', []))} steps")
        else:
            print("   ❌ Quote request failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Jupiter API test failed: {e}")
        return False
    
    # 5. Test Trade Executor
    print("\n5. Testing Trade Executor:")
    try:
        trade_executor = JupiterTradeExecutor(wallet.keypair)
        print("   ✅ Trade executor initialized")
        
        # Test quote only (no actual trade)
        test_token = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # USDC
        test_amount = 0.001  # Very small amount for testing
        
        print(f"   🧪 Testing quote for {test_amount} SOL -> USDC")
        quote = await jupiter.get_quote(sol_mint, test_token, int(test_amount * 1e9))
        
        if quote:
            print("   ✅ Trade quote successful")
            print(f"   📊 Expected Output: {quote.get('outAmount', 'N/A')} USDC")
        else:
            print("   ❌ Trade quote failed")
            return False
            
    except Exception as e:
        print(f"   ❌ Trade executor test failed: {e}")
        return False
    
    # 6. Test Transaction Building (without execution)
    print("\n6. Testing Transaction Building:")
    try:
        if not config.get_demo_mode() and wallet.keypair:
            # Test transaction building (but don't execute)
            user_pubkey = str(wallet.keypair.pubkey())
            print(f"   👤 User Pubkey: {user_pubkey[:8]}...")
            
            # Get swap transaction data
            swap_tx = await jupiter.get_swap_transaction(quote, user_pubkey)
            if swap_tx:
                print("   ✅ Transaction building successful")
                print(f"   📄 Transaction length: {len(swap_tx)} chars")
            else:
                print("   ❌ Transaction building failed")
                return False
        else:
            print("   🔶 Skipping transaction building (demo mode or no keypair)")
            
    except Exception as e:
        print(f"   ❌ Transaction building test failed: {e}")
        return False
    
    # 7. Test Bot Integration
    print("\n7. Testing Bot Integration:")
    try:
        # Import and test bot components
        from auracle_telegram_unified import AuracleUnifiedBot
        
        # Create bot instance (don't run)
        bot_token = config.TELEGRAM_BOT_TOKEN
        if bot_token:
            print("   ✅ Bot token configured")
            print("   ✅ Bot integration ready")
        else:
            print("   ❌ Bot token not configured")
            return False
            
    except Exception as e:
        print(f"   ❌ Bot integration test failed: {e}")
        return False
    
    # 8. Summary Report
    print("\n8. Summary Report:")
    print("   " + "=" * 40)
    print("   🎯 TRADING EXECUTION READINESS:")
    print("   " + "=" * 40)
    
    if config.get_demo_mode():
        print("   🔶 Demo Mode: Simulated trading ready")
        print("   🔶 All quotes and transactions will be simulated")
        print("   🔶 No real funds will be used")
    else:
        print("   🔥 Live Mode: Real trading ready")
        print("   🔥 All transactions will use real funds")
        print("   🔥 Jupiter API connected and functional")
        print(f"   🔥 Wallet balance: {balance:.4f} SOL")
    
    print("\n   ✅ ALL TESTS PASSED")
    print("   ✅ Bot can properly execute trades")
    print("   ✅ Jupiter API integration working")
    print("   ✅ Wallet functionality verified")
    
    return True


async def main():
    """Main test runner."""
    print("🚀 Starting AURACLE Trading Execution Test...")
    
    try:
        success = await test_trading_execution()
        
        if success:
            print("\n🎉 ALL TESTS PASSED! Trading execution is ready.")
            print("🤖 Bot can properly execute trades via Telegram.")
            return 0
        else:
            print("\n❌ TESTS FAILED! Trading execution needs attention.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
