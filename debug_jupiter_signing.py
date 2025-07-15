#!/usr/bin/env python3
"""
Debug Jupiter API Transaction Signing
====================================

Enhanced debugging of the Jupiter API transaction signing process.
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

async def debug_jupiter_signing():
    """Debug the Jupiter API signing process step by step"""
    
    print("🔍 Debugging Jupiter API Transaction Signing")
    print("=" * 60)
    
    # Initialize keypair
    keypair = Keypair.from_base58_string(config.WALLET_PRIVATE_KEY)
    print(f"🔑 Wallet: {keypair.pubkey()}")
    
    # Initialize RPC client
    rpc_client = AsyncClient("https://api.mainnet-beta.solana.com")
    print(f"🌐 RPC client initialized")
    
    async with httpx.AsyncClient() as client:
        # Step 1: Get quote
        print(f"\n1️⃣ Getting quote...")
        quote_url = "https://quote-api.jup.ag/v6/quote"
        quote_params = {
            "inputMint": "So11111111111111111111111111111111111111112",  # SOL
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": "1000000",  # 0.001 SOL
            "slippageBps": "50"
        }
        
        response = await client.get(quote_url, params=quote_params)
        if response.status_code != 200:
            print(f"❌ Quote failed: {response.status_code}")
            return False
        
        quote_data = response.json()
        print(f"✅ Quote: {quote_data['inAmount']} SOL → {quote_data['outAmount']} USDC")
        
        # Step 2: Get swap transaction
        print(f"\n2️⃣ Getting swap transaction...")
        swap_url = "https://quote-api.jup.ag/v6/swap"
        swap_data = {
            "quoteResponse": quote_data,
            "userPublicKey": str(keypair.pubkey()),
            "wrapAndUnwrapSol": True
        }
        
        response = await client.post(swap_url, json=swap_data)
        if response.status_code != 200:
            print(f"❌ Swap failed: {response.status_code} - {response.text}")
            return False
        
        swap_response = response.json()
        serialized_tx = swap_response["swapTransaction"]
        print(f"✅ Swap transaction retrieved: {len(serialized_tx)} chars")
        
        # Step 3: Decode transaction
        print(f"\n3️⃣ Decoding transaction...")
        try:
            transaction_bytes = base64.b64decode(serialized_tx)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            print(f"✅ Transaction decoded: {type(transaction)}")
            print(f"📄 Message type: {type(transaction.message)}")
            print(f"🔢 Signatures: {len(transaction.signatures)}")
        except Exception as e:
            print(f"❌ Decode error: {e}")
            return False
        
        # Step 4: Sign transaction
        print(f"\n4️⃣ Signing transaction...")
        try:
            # Extract message
            message = transaction.message
            print(f"✅ Message extracted: {type(message)}")
            
            # Convert message to bytes
            message_bytes = bytes(message)
            print(f"✅ Message bytes: {len(message_bytes)} bytes")
            
            # Sign the message
            signature = keypair.sign_message(message_bytes)
            print(f"✅ Message signed: {type(signature)}")
            print(f"📝 Signature: {signature}")
            
            # Create signed transaction
            signed_transaction = VersionedTransaction.populate(message, [signature])
            print(f"✅ Signed transaction created: {type(signed_transaction)}")
            
            # Verify signatures
            print(f"🔍 Signed transaction signatures: {len(signed_transaction.signatures)}")
            for i, sig in enumerate(signed_transaction.signatures):
                print(f"  Signature {i}: {sig}")
                
        except Exception as e:
            print(f"❌ Signing error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 5: Send transaction
        print(f"\n5️⃣ Sending transaction...")
        try:
            # Try to send with different options
            print(f"🚀 Sending transaction to RPC...")
            
            signature_result = await rpc_client.send_transaction(
                signed_transaction,
                opts=TxOpts(skip_preflight=False, max_retries=3)
            )
            
            if signature_result.value:
                print(f"✅ Transaction sent successfully!")
                print(f"📄 Signature: {signature_result.value}")
                
                # Wait for confirmation
                print(f"⏳ Waiting for confirmation...")
                confirmation = await rpc_client.confirm_transaction(signature_result.value)
                print(f"✅ Transaction confirmed: {confirmation}")
                
                return True
            else:
                print(f"❌ Transaction failed: {signature_result}")
                return False
                
        except Exception as e:
            print(f"❌ Send error: {e}")
            import traceback
            traceback.print_exc()
            return False

async def main():
    """Main function"""
    success = await debug_jupiter_signing()
    
    if success:
        print(f"\n✅ Jupiter API signing is working!")
        print(f"🎯 The issue might be elsewhere")
    else:
        print(f"\n❌ Jupiter API signing still has issues")
        print(f"🔧 Need deeper investigation")

if __name__ == "__main__":
    asyncio.run(main())
