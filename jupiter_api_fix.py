"""
Fixed Jupiter API module to resolve signing issues
================================================

This module provides a fixed implementation of the Jupiter API
interaction code, specifically addressing the transaction signing
issue with the Solders library.
"""

import asyncio
import json
import base64
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Check if we have the Solana library or need to use minimal implementation
try:
    from solders.keypair import Keypair
    from solders.message import Message
    from solders.transaction import VersionedTransaction
    from solders.signature import Signature
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.types import TxOpts
    SOLDERS_AVAILABLE = True
    logger.info("Using solders library for transaction handling")
except ImportError:
    logger.warning("Solders library not available, using minimal implementation")
    SOLDERS_AVAILABLE = False
    # We'll define fallbacks later if needed

def create_fixed_jupiter_api():
    """Create and return a fixed Jupiter API module."""
    
    # Import original Jupiter API module
    try:
        import jupiter_api
        from jupiter_api import JupiterApi
        
        # Store original methods
        original_sign_and_send_swap_tx = JupiterApi.sign_and_send_swap_transaction
        
        def fixed_sign_and_send_swap_transaction(self, swap_tx_b64, wallet_keypair):
            """
            Fixed implementation of signing and sending swap transactions.
            Properly handles VersionedTransaction signing with the Solders library.
            """
            async def _execute():
                print(f"[jupiter] 🔄 Processing swap transaction with fixed signing...")
                
                # Decode transaction
                try:
                    transaction_bytes = base64.b64decode(swap_tx_b64)
                    transaction = VersionedTransaction.from_bytes(transaction_bytes)
                    print(f"[jupiter] 📝 Transaction decoded successfully")
                except Exception as decode_error:
                    print(f"[jupiter] ❌ Transaction decode error: {decode_error}")
                    return {"success": False, "error": f"Transaction decode failed: {decode_error}"}

                # Sign transaction using the CORRECT method for Solders VersionedTransaction
                try:
                    # Get the transaction message
                    message = transaction.message
                    
                    # Sign the message with the private key
                    signature = wallet_keypair.sign_message(message.serialize())
                    
                    # Create a new VersionedTransaction with the signature
                    signed_tx = VersionedTransaction.populate(message, [signature])
                    
                    print(f"[jupiter] ✅ Transaction signed successfully")

                except Exception as sign_error:
                    print(f"[jupiter] ❌ Transaction signing error: {sign_error}")
                    return {"success": False, "error": f"Transaction signing failed: {sign_error}"}

                # Send transaction
                print(f"[jupiter] 🚀 Sending transaction to Solana network...")
                print(f"[jupiter] 🌐 RPC endpoint: {self.rpc_client.endpoint_uri}")

                try:
                    signature_result = await self.rpc_client.send_transaction(
                        signed_tx,
                        opts=TxOpts(skip_preflight=True, max_retries=3)
                    )

                    if signature_result.value:
                        signature_str = str(signature_result.value)
                        print(f"[jupiter] ✅ Transaction sent successfully!")
                        print(f"[jupiter] 📋 Transaction signature: {signature_str}")
                        
                        # Create result with signature
                        result = {
                            "success": True,
                            "signature": signature_str,
                            "solscan_url": f"https://solscan.io/tx/{signature_str}"
                        }
                        return result
                    else:
                        print(f"[jupiter] ❌ Transaction failed: No signature returned")
                        return {"success": False, "error": "No signature returned"}
                        
                except Exception as send_error:
                    print(f"[jupiter] ❌ Transaction send error: {send_error}")
                    return {"success": False, "error": f"Transaction send failed: {send_error}"}

            # Run the async function
            return asyncio.create_task(_execute())
        
        # Replace the method in the JupiterApi class
        JupiterApi.sign_and_send_swap_transaction = fixed_sign_and_send_swap_transaction
        
        # Also fix the method that's used for market orders
        original_sign_and_send_tx = JupiterApi.sign_and_send_transaction
        
        def fixed_sign_and_send_transaction(self, tx_b64, wallet_keypair):
            """
            Fixed implementation of signing and sending transactions.
            Properly handles VersionedTransaction signing with the Solders library.
            """
            async def _execute():
                print(f"[jupiter] 🔄 Processing transaction with fixed signing...")
                
                # Decode transaction
                try:
                    transaction_bytes = base64.b64decode(tx_b64)
                    transaction = VersionedTransaction.from_bytes(transaction_bytes)
                    print(f"[jupiter] 📝 Transaction decoded successfully")
                except Exception as decode_error:
                    print(f"[jupiter] ❌ Transaction decode error: {decode_error}")
                    return {"success": False, "error": f"Transaction decode failed: {decode_error}"}

                # Sign transaction using the CORRECT method for Solders VersionedTransaction
                try:
                    # Get the transaction message
                    message = transaction.message
                    
                    # Sign the message with the private key
                    signature = wallet_keypair.sign_message(message.serialize())
                    
                    # Create a new VersionedTransaction with the signature
                    signed_tx = VersionedTransaction.populate(message, [signature])
                    
                    print(f"[jupiter] ✅ Transaction signed successfully")

                except Exception as sign_error:
                    print(f"[jupiter] ❌ Transaction signing error: {sign_error}")
                    return {"success": False, "error": f"Transaction signing failed: {sign_error}"}

                # Send transaction
                print(f"[jupiter] 🚀 Sending transaction to Solana network...")
                print(f"[jupiter] 🌐 RPC endpoint: {self.rpc_client.endpoint_uri}")

                try:
                    signature_result = await self.rpc_client.send_transaction(
                        signed_tx,
                        opts=TxOpts(skip_preflight=True, max_retries=3)
                    )

                    if signature_result.value:
                        signature_str = str(signature_result.value)
                        print(f"[jupiter] ✅ Transaction sent successfully!")
                        print(f"[jupiter] 📋 Transaction signature: {signature_str}")
                        
                        # Create result with signature
                        result = {
                            "success": True,
                            "signature": signature_str,
                            "solscan_url": f"https://solscan.io/tx/{signature_str}"
                        }
                        return result
                    else:
                        print(f"[jupiter] ❌ Transaction failed: No signature returned")
                        return {"success": False, "error": "No signature returned"}
                        
                except Exception as send_error:
                    print(f"[jupiter] ❌ Transaction send error: {send_error}")
                    return {"success": False, "error": f"Transaction send failed: {send_error}"}

            # Run the async function
            return asyncio.create_task(_execute())
            
        # Replace the method in the JupiterApi class
        JupiterApi.sign_and_send_transaction = fixed_sign_and_send_transaction
        
        # Return the patched module
        return jupiter_api
        
    except ImportError as e:
        logger.error(f"Failed to import jupiter_api module: {e}")
        return None
        
# Apply the patch when this module is imported
fixed_jupiter_api = create_fixed_jupiter_api()

# Print confirmation
if fixed_jupiter_api:
    print("✅ Jupiter API patched with fixed transaction signing")
else:
    print("❌ Failed to patch Jupiter API")
