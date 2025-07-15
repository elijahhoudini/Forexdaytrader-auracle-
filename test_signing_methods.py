#!/usr/bin/env python3
"""
Test Jupiter API Transaction Signing Methods
==========================================

This script tests different transaction signing approaches to identify
the correct method for the solders library used by Jupiter API.
"""

import asyncio
import json
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.hash import Hash
from solders.pubkey import Pubkey
from solders.signature import Signature
import httpx
import config

async def test_signing_methods():
    """Test different signing methods to find the working approach"""
    
    # Initialize keypair
    keypair = Keypair.from_base58_string(config.WALLET_PRIVATE_KEY)
    print(f"🔑 Wallet: {keypair.pubkey()}")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Get a real Jupiter quote
        print("\n1️⃣ Getting Jupiter quote...")
        
        quote_url = "https://quote-api.jup.ag/v6/quote"
        quote_params = {
            "inputMint": "So11111111111111111111111111111111111111112",  # SOL
            "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            "amount": "10000000",  # 0.01 SOL
            "slippageBps": "50"
        }
        
        try:
            response = await client.get(quote_url, params=quote_params)
            if response.status_code == 200:
                quote_data = response.json()
                print(f"✅ Quote successful: {quote_data['inAmount']} SOL → {quote_data['outAmount']} USDC")
            else:
                print(f"❌ Quote failed: {response.status_code}")
                return None, None
        except Exception as e:
            print(f"❌ Quote error: {e}")
            return None, None
        
        # Test 2: Get swap transaction
        print("\n2️⃣ Getting swap transaction...")
        
        swap_url = "https://quote-api.jup.ag/v6/swap"
        swap_data = {
            "quoteResponse": quote_data,
            "userPublicKey": str(keypair.pubkey()),
            "wrapAndUnwrapSol": True
        }
        
        try:
            response = await client.post(swap_url, json=swap_data)
            if response.status_code == 200:
                swap_response = response.json()
                print("✅ Swap transaction retrieved successfully")
                
                # Extract transaction data
                serialized_tx = swap_response["swapTransaction"]
                print(f"📄 Transaction data length: {len(serialized_tx)} chars")
                
            else:
                print(f"❌ Swap failed: {response.status_code} - {response.text}")
                return None, None
        except Exception as e:
            print(f"❌ Swap error: {e}")
            return None, None
    
    # Test 3: Try different signing methods
    print("\n3️⃣ Testing signing methods...")
    
    try:
        # Deserialize the transaction
        import base64
        tx_bytes = base64.b64decode(serialized_tx)
        transaction = VersionedTransaction.from_bytes(tx_bytes)
        print("✅ Transaction deserialized successfully")
        
        # Method 1: Try partial_sign (most common)
        print("\n🔧 Method 1: partial_sign()")
        try:
            signed_tx = transaction.partial_sign([keypair])
            print(f"✅ partial_sign() successful: {type(signed_tx)}")
            
            # Serialize and test
            signed_bytes = bytes(signed_tx)
            print(f"✅ Serialization successful: {len(signed_bytes)} bytes")
            
            # Test if it's properly signed
            signatures = signed_tx.signatures
            print(f"✅ Signatures: {len(signatures)} found")
            
            return "partial_sign", signed_tx
            
        except Exception as e:
            print(f"❌ partial_sign() failed: {e}")
        
        # Method 2: Try sign() method
        print("\n🔧 Method 2: sign()")
        try:
            signed_tx = transaction.sign([keypair])
            print(f"✅ sign() successful: {type(signed_tx)}")
            
            signed_bytes = bytes(signed_tx)
            print(f"✅ Serialization successful: {len(signed_bytes)} bytes")
            
            return "sign", signed_tx
            
        except Exception as e:
            print(f"❌ sign() failed: {e}")
        
        # Method 3: Try manual signing
        print("\n🔧 Method 3: Manual message signing")
        try:
            # Get message to sign
            message = transaction.message
            print(f"✅ Message extracted: {type(message)}")
            
            # Sign the message
            signature = keypair.sign_message(bytes(message))
            print(f"✅ Message signed: {type(signature)}")
            
            # Create new transaction with signature
            signed_tx = VersionedTransaction.populate(message, [signature])
            print(f"✅ Transaction populated: {type(signed_tx)}")
            
            signed_bytes = bytes(signed_tx)
            print(f"✅ Serialization successful: {len(signed_bytes)} bytes")
            
            return "manual", signed_tx
            
        except Exception as e:
            print(f"❌ Manual signing failed: {e}")
        
        # Method 4: Try with blockhash
        print("\n🔧 Method 4: With recent blockhash")
        try:
            # Get recent blockhash
            from solana.rpc.async_api import AsyncClient
            
            client = AsyncClient("https://api.mainnet-beta.solana.com")
            blockhash_resp = await client.get_latest_blockhash()
            
            if blockhash_resp.value:
                recent_blockhash = blockhash_resp.value.blockhash
                print(f"✅ Recent blockhash: {recent_blockhash}")
                
                # Try signing with fresh transaction
                signed_tx = transaction.partial_sign([keypair])
                print(f"✅ Signing with blockhash successful: {type(signed_tx)}")
                
                return "blockhash", signed_tx
                
        except Exception as e:
            print(f"❌ Blockhash signing failed: {e}")
        
        print("❌ All signing methods failed!")
        return None, None
        
    except Exception as e:
        print(f"❌ Transaction processing error: {e}")
        return None, None

async def main():
    """Main test function"""
    print("🧪 Testing Jupiter API Transaction Signing Methods")
    print("=" * 60)
    
    try:
        method, signed_tx = await test_signing_methods()
        
        if method and signed_tx:
            print(f"\n✅ SUCCESS: {method} method works!")
            print(f"🔧 Use this method in jupiter_api.py")
            
            # Show implementation example
            print(f"\n📝 Implementation example:")
            print(f"```python")
            if method == "partial_sign":
                print(f"signed_tx = transaction.partial_sign([keypair])")
            elif method == "sign":
                print(f"signed_tx = transaction.sign([keypair])")
            elif method == "manual":
                print(f"message = transaction.message")
                print(f"signature = keypair.sign_message(bytes(message))")
                print(f"signed_tx = VersionedTransaction.populate(message, [signature])")
            elif method == "blockhash":
                print(f"signed_tx = transaction.partial_sign([keypair])")
            print(f"```")
            
        else:
            print(f"\n❌ FAILED: No working signing method found")
            print(f"🔧 Check solders library version and documentation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
