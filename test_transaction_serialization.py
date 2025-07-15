#!/usr/bin/env python3
"""
Test Transaction Serialization and Validation
============================================

Test different ways to serialize and validate the signed transaction.
"""

import asyncio
import json
import base64
import time
from typing import Dict, Any, Optional

import httpx
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TxOpts
from solders.transaction import VersionedTransaction
from solders.keypair import Keypair

import config

async def test_transaction_serialization():
    """Test different serialization methods"""
    
    print("🔍 Testing Transaction Serialization")
    print("=" * 50)
    
    # Initialize keypair
    keypair = Keypair.from_base58_string(config.WALLET_PRIVATE_KEY)
    print(f"🔑 Wallet: {keypair.pubkey()}")
    
    # Initialize RPC client
    rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
    
    async with httpx.AsyncClient() as client:
        # Get quote and swap transaction
        print(f"\n1️⃣ Getting quote and swap transaction...")
        quote_url = "https://quote-api.jup.ag/v6/quote"
        quote_params = {
            "inputMint": "So11111111111111111111111111111111111111112",  # SOL
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": "1000000",  # 0.001 SOL
            "slippageBps": "50"
        }
        
        response = await client.get(quote_url, params=quote_params)
        quote_data = response.json()
        
        swap_url = "https://quote-api.jup.ag/v6/swap"
        swap_data = {
            "quoteResponse": quote_data,
            "userPublicKey": str(keypair.pubkey()),
            "wrapAndUnwrapSol": True
        }
        
        response = await client.post(swap_url, json=swap_data)
        swap_response = response.json()
        serialized_tx = swap_response["swapTransaction"]
        
        print(f"✅ Got transaction data")
        
        # Decode and sign
        print(f"\n2️⃣ Decoding and signing...")
        transaction_bytes = base64.b64decode(serialized_tx)
        transaction = VersionedTransaction.from_bytes(transaction_bytes)
        
        message = transaction.message
        signature = keypair.sign_message(bytes(message))
        signed_transaction = VersionedTransaction.populate(message, [signature])
        
        print(f"✅ Transaction signed")
        
        # Test different serialization methods
        print(f"\n3️⃣ Testing serialization methods...")
        
        # Method 1: Direct bytes() conversion
        try:
            serialized_bytes = bytes(signed_transaction)
            print(f"✅ Method 1 - Direct bytes(): {len(serialized_bytes)} bytes")
            
            # Test sending with direct bytes
            print(f"🚀 Testing direct bytes send...")
            try:
                signature_result = await rpc_client.send_raw_transaction(
                    serialized_bytes,
                    opts=TxOpts(skip_preflight=False, max_retries=3)
                )
                
                if signature_result.value:
                    print(f"✅ Method 1 SUCCESS: {signature_result.value}")
                    return True
                else:
                    print(f"❌ Method 1 failed: {signature_result}")
                    
            except Exception as e:
                print(f"❌ Method 1 error: {e}")
                
        except Exception as e:
            print(f"❌ Method 1 serialization error: {e}")
        
        # Method 2: Try to_solders() if available
        try:
            if hasattr(signed_transaction, 'to_solders'):
                solders_tx = signed_transaction.to_solders()
                print(f"✅ Method 2 - to_solders(): {type(solders_tx)}")
                
                # Test sending with solders transaction
                print(f"🚀 Testing solders send...")
                try:
                    signature_result = await rpc_client.send_transaction(
                        solders_tx,
                        opts=TxOpts(skip_preflight=False, max_retries=3)
                    )
                    
                    if signature_result.value:
                        print(f"✅ Method 2 SUCCESS: {signature_result.value}")
                        return True
                    else:
                        print(f"❌ Method 2 failed: {signature_result}")
                        
                except Exception as e:
                    print(f"❌ Method 2 error: {e}")
            else:
                print(f"❌ Method 2 not available: no to_solders() method")
                
        except Exception as e:
            print(f"❌ Method 2 error: {e}")
        
        # Method 3: Try with preflight checks disabled
        try:
            print(f"🚀 Testing with preflight disabled...")
            signature_result = await rpc_client.send_transaction(
                signed_transaction,
                opts=TxOpts(skip_preflight=True, max_retries=3)
            )
            
            if signature_result.value:
                print(f"✅ Method 3 SUCCESS: {signature_result.value}")
                return True
            else:
                print(f"❌ Method 3 failed: {signature_result}")
                
        except Exception as e:
            print(f"❌ Method 3 error: {e}")
        
        # Method 4: Try with different RPC endpoint
        try:
            print(f"🚀 Testing with different RPC endpoint...")
            alt_rpc_client = AsyncClient("https://api.devnet.solana.com")
            
            # Note: This would fail on devnet for mainnet tokens, but tests the RPC connection
            signature_result = await alt_rpc_client.send_transaction(
                signed_transaction,
                opts=TxOpts(skip_preflight=True, max_retries=1)
            )
            
            if signature_result.value:
                print(f"✅ Method 4 SUCCESS: {signature_result.value}")
                return True
            else:
                print(f"❌ Method 4 failed: {signature_result}")
                
        except Exception as e:
            print(f"❌ Method 4 error: {e}")
        
        # Method 5: Check transaction validation
        print(f"\n4️⃣ Transaction validation...")
        try:
            # Check if transaction has valid signatures
            print(f"📊 Transaction details:")
            print(f"  Message: {type(signed_transaction.message)}")
            print(f"  Signatures: {len(signed_transaction.signatures)}")
            
            for i, sig in enumerate(signed_transaction.signatures):
                print(f"  Signature {i}: {sig}")
                
            # Try to verify the signature manually
            message_bytes = bytes(signed_transaction.message)
            is_valid = keypair.pubkey().verify(signature, message_bytes)
            print(f"  Signature verification: {is_valid}")
            
            if not is_valid:
                print(f"❌ Signature verification failed!")
                return False
            else:
                print(f"✅ Signature verification passed!")
                
        except Exception as e:
            print(f"❌ Validation error: {e}")
    
    print(f"\n❌ All methods failed")
    return False

async def main():
    """Main function"""
    success = await test_transaction_serialization()
    
    if success:
        print(f"\n✅ Found working serialization method!")
    else:
        print(f"\n❌ All serialization methods failed")
        print(f"🔧 The issue might be with the transaction structure itself")

if __name__ == "__main__":
    asyncio.run(main())
