#!/usr/bin/env python3
"""
Test Jupiter API transaction signing
"""

import asyncio
import base64
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solana.rpc.async_api import AsyncClient
from jupiter_api import JupiterAPI
import config

async def test_jupiter_signing():
    """Test Jupiter API transaction signing"""
    
    print("🧪 Testing Jupiter API transaction signing...")
    
    # Initialize Jupiter API
    jupiter = JupiterAPI()
    
    # Create test wallet
    wallet = Keypair()
    print(f"📍 Test wallet: {wallet.pubkey()}")
    
    # Test quote
    sol_mint = "So11111111111111111111111111111111111111112"
    usdc_mint = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
    amount = 1000000  # 0.001 SOL
    
    try:
        # Get quote
        print("📊 Getting quote...")
        quote = await jupiter.get_quote(sol_mint, usdc_mint, amount)
        
        if not quote:
            print("❌ Failed to get quote")
            return
            
        print(f"✅ Quote received: {quote.get('outAmount', 0)} USDC")
        
        # Get swap transaction
        print("🔄 Getting swap transaction...")
        swap_tx = await jupiter.get_swap_transaction(quote, str(wallet.pubkey()))
        
        if not swap_tx:
            print("❌ Failed to get swap transaction")
            return
            
        print("✅ Swap transaction received")
        
        # Test transaction signing
        print("🔑 Testing transaction signing...")
        
        # Decode transaction
        transaction_bytes = base64.b64decode(swap_tx)
        transaction = VersionedTransaction.from_bytes(transaction_bytes)
        
        print(f"📋 Transaction decoded successfully")
        
        # Test signing methods
        try:
            # Method 1: Direct message signing
            print("🔐 Testing Method 1: Direct message signing...")
            message = transaction.message
            signature = wallet.sign_message(bytes(message))
            signed_tx = VersionedTransaction.populate(message, [signature])
            print("✅ Method 1 successful")
            
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
            
            try:
                # Method 2: Message serialization
                print("🔐 Testing Method 2: Message serialization...")
                message_bytes = transaction.message.serialize()
                signature = wallet.sign_message(message_bytes)
                signed_tx = VersionedTransaction.populate(transaction.message, [signature])
                print("✅ Method 2 successful")
                
            except Exception as e2:
                print(f"❌ Method 2 failed: {e2}")
                
                try:
                    # Method 3: Alternative approach
                    print("🔐 Testing Method 3: Alternative approach...")
                    # Try to understand the transaction structure
                    print(f"Transaction type: {type(transaction)}")
                    print(f"Message type: {type(transaction.message)}")
                    print(f"Available methods: {[m for m in dir(transaction) if not m.startswith('_')]}")
                    
                except Exception as e3:
                    print(f"❌ Method 3 failed: {e3}")
        
        print("✅ Transaction signing test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_jupiter_signing())
