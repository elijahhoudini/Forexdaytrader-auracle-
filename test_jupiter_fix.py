#!/usr/bin/env python3
"""
Test Jupiter API Fix
===================

Test if the Jupiter API signing issue is fixed.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_jupiter_signing():
    """Test Jupiter API signing fix"""
    try:
        import config
        from jupiter_api import JupiterTradeExecutor
        from solders.keypair import Keypair
        import base58
        
        print("🔧 Testing Jupiter API signing fix...")
        
        # Check if we have a keypair
        if not hasattr(config, 'WALLET_PRIVATE_KEY') or not config.WALLET_PRIVATE_KEY:
            print("❌ No wallet private key configured")
            return False
        
        # Initialize keypair
        try:
            private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
            keypair = Keypair.from_bytes(private_key_bytes)
            print(f"✅ Keypair loaded: {str(keypair.pubkey())[:8]}...")
        except Exception as e:
            print(f"❌ Failed to load keypair: {e}")
            return False
        
        # Initialize Jupiter executor
        jupiter = JupiterTradeExecutor(keypair)
        
        # Test getting a quote (this should work)
        print("🔍 Testing quote retrieval...")
        quote = await jupiter.jupiter.get_quote(
            input_mint=jupiter.jupiter.SOL_MINT,
            output_mint=jupiter.jupiter.USDC_MINT,
            amount=1000000  # 0.001 SOL
        )
        
        if quote:
            print(f"✅ Quote successful: {quote.get('outAmount', 0)} USDC")
        else:
            print("❌ Quote failed")
            return False
        
        # Test getting swap transaction (this should work now)
        print("🔍 Testing swap transaction creation...")
        swap_tx = await jupiter.jupiter.get_swap_transaction(
            quote, 
            str(keypair.pubkey())
        )
        
        if swap_tx:
            print("✅ Swap transaction created successfully")
            print(f"📄 Transaction size: {len(swap_tx)} bytes (base64)")
        else:
            print("❌ Swap transaction creation failed")
            return False
        
        print("\n✅ All Jupiter API tests passed! Trading should work now.")
        return True
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function"""
    print("🚀 Jupiter API Signing Fix Test")
    print("=" * 40)
    
    success = await test_jupiter_signing()
    
    if success:
        print("\n✅ Fix successful! AURACLE should now be able to execute trades.")
    else:
        print("\n❌ Fix failed! Trading may still have issues.")

if __name__ == "__main__":
    asyncio.run(main())
