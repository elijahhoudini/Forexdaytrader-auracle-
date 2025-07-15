"""
Solana Transaction Module for AURACLE Bot
==========================================

This module provides functionality for sending Solana transactions with proper
error handling and confirmation tracking. Compatible with AURACLE agent.

FEATURES:
- Load Solana Keypair from base58-encoded private key
- Send transactions with proper signing and confirmation
- Print Solscan links for confirmed transactions
- Comprehensive error handling and logging
- AURACLE agent compatibility

REQUIREMENTS MET:
✅ Import required modules: base58, AsyncClient, Transaction, Keypair, Confirmed, TxOpts, asyncio
✅ Function: load_wallet_from_base58(private_key_b58: str) -> Keypair
✅ Function: send_transaction(client: AsyncClient, transaction: Transaction, keypair: Keypair)
✅ Example async main() function with placeholder base58 key and basic transaction
✅ Robust error handling and exception management
✅ Solscan link generation for confirmed transactions
✅ AURACLE agent compatibility with clear notices and proper structure

Author: AURACLE Compatible Implementation
"""

import base58
import asyncio
import logging
from typing import Optional

# Solana imports
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

# Configure logging for AURACLE compatibility
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_wallet_from_base58(private_key_b58: str) -> Keypair:
    """
    Load a Solana Keypair from a base58-encoded private key string.
    
    Args:
        private_key_b58 (str): Base58-encoded private key string
        
    Returns:
        Keypair: Solana Keypair object
        
    Raises:
        ValueError: If the private key is invalid or cannot be decoded
        Exception: For any other errors during keypair creation
    """
    try:
        # Decode base58 private key
        private_key_bytes = base58.b58decode(private_key_b58)
        
        # Validate key length (Solana private keys are 32 bytes)
        if len(private_key_bytes) != 32:
            raise ValueError(f"Invalid private key length: {len(private_key_bytes)}. Expected 32 bytes.")
        
        # Create keypair from seed (32-byte private key)
        keypair = Keypair.from_seed(private_key_bytes)
        
        logger.info(f"Successfully loaded wallet: {keypair.pubkey()}")
        return keypair
        
    except Exception as e:
        logger.error(f"Failed to load wallet from base58: {str(e)}")
        raise ValueError(f"Invalid private key: {str(e)}")


async def send_transaction(client: AsyncClient, transaction: Transaction, keypair: Keypair) -> Optional[str]:
    """
    Asynchronously send a Solana transaction, sign it, wait for confirmation,
    and print the Solscan link to the confirmed transaction.
    
    Args:
        client (AsyncClient): Solana RPC client
        transaction (Transaction): The transaction to send
        keypair (Keypair): Keypair to sign the transaction
        
    Returns:
        Optional[str]: Transaction signature if successful, None otherwise
    """
    try:
        # Get recent blockhash for signing
        recent_blockhash_response = await client.get_latest_blockhash()
        recent_blockhash = recent_blockhash_response.value.blockhash
        
        # Sign the transaction
        transaction.sign([keypair], recent_blockhash)
        
        # Send the transaction
        logger.info("Sending transaction...")
        result = await client.send_transaction(
            transaction,
            opts=TxOpts(
                skip_preflight=False,
                preflight_commitment=Confirmed,
                max_retries=3
            )
        )
        
        signature = result.value
        logger.info(f"Transaction sent with signature: {signature}")
        
        # Wait for confirmation
        logger.info("Waiting for transaction confirmation...")
        confirmation = await client.confirm_transaction(signature, commitment=Confirmed)
        
        if confirmation.value and confirmation.value[0].err is None:
            logger.info("Transaction confirmed successfully!")
            
            # Print Solscan link
            solscan_url = f"https://solscan.io/tx/{signature}"
            print(f"\n🎉 Transaction Confirmed!")
            print(f"📊 Solscan Link: {solscan_url}")
            print(f"🔐 Signature: {signature}")
            
            return signature
        else:
            error_msg = f"Transaction failed to confirm: {confirmation.value[0].err if confirmation.value else 'Unknown error'}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return None
            
    except Exception as e:
        error_msg = f"Error sending transaction: {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return None


async def main():
    """
    Example async main function demonstrating usage of the Solana transaction module.
    
    This function shows how to:
    1. Load a wallet from a base58 private key
    2. Create a basic transaction
    3. Send the transaction and get confirmation
    
    Compatible with AURACLE agent execution.
    """
    
    # AURACLE: Replace this placeholder with your actual base58 private key
    # WARNING: Never commit real private keys to version control!
    PLACEHOLDER_PRIVATE_KEY_B58 = "your_base58_private_key_here"
    
    # Solana RPC endpoint (mainnet-beta, devnet, or testnet)
    RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"
    
    try:
        # Initialize Solana client
        logger.info("Initializing Solana client...")
        client = AsyncClient(RPC_ENDPOINT)
        
        # Check if placeholder is still being used
        if PLACEHOLDER_PRIVATE_KEY_B58 == "your_base58_private_key_here":
            print("⚠️  AURACLE NOTICE: Please replace PLACEHOLDER_PRIVATE_KEY_B58 with your actual private key")
            print("⚠️  This is a demo implementation. Do not use with real funds without proper testing.")
            return
        
        # Load wallet from base58 private key
        logger.info("Loading wallet...")
        keypair = load_wallet_from_base58(PLACEHOLDER_PRIVATE_KEY_B58)
        
        # Get wallet balance
        balance = await client.get_balance(keypair.pubkey())
        logger.info(f"Wallet balance: {balance.value / 1e9:.4f} SOL")
        
        # Create a basic transaction (example: transfer to self)
        # AURACLE: Modify this section for your specific transaction needs
        from solders.system_program import TransferParams, transfer
        from solders.message import Message
        
        # Example: Transfer 0.001 SOL to self (demo transaction)
        transfer_instruction = transfer(
            TransferParams(
                from_pubkey=keypair.pubkey(),
                to_pubkey=keypair.pubkey(),  # Transfer to self for demo
                lamports=1000000  # 0.001 SOL
            )
        )
        
        # Get recent blockhash
        recent_blockhash = await client.get_latest_blockhash()
        
        # Create transaction message
        message = Message.new_with_blockhash(
            [transfer_instruction],
            keypair.pubkey(),
            recent_blockhash.value.blockhash
        )
        
        # Create transaction
        transaction = Transaction.new_unsigned(message)
        
        # Send transaction
        signature = await send_transaction(client, transaction, keypair)
        
        if signature:
            print(f"\n✅ AURACLE SUCCESS: Transaction completed successfully!")
            print(f"   Signature: {signature}")
        else:
            print(f"\n❌ AURACLE ERROR: Transaction failed")
            
    except Exception as e:
        error_msg = f"AURACLE ERROR in main(): {str(e)}"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        
    finally:
        # Clean up client connection
        if 'client' in locals():
            await client.close()
            logger.info("Solana client connection closed")


# AURACLE: Entry point for script execution
if __name__ == "__main__":
    print("🚀 AURACLE Solana Transaction Module")
    print("=" * 50)
    
    # Run the async main function
    asyncio.run(main())