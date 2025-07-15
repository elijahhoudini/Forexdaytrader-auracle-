"""
RPC Manager Module
==================

Provides RPC connection management for Solana blockchain operations
with connection pooling, retry logic, and error handling.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from .blockchain_config import config
from .blockchain_logger import logger
from .retry_decorator import retry_rpc_call


class RPCManager:
    """Manager for Solana RPC connections."""
    
    def __init__(self, 
                 rpc_endpoint: Optional[str] = None,
                 commitment: Optional[Commitment] = None,
                 timeout: Optional[int] = None):
        """
        Initialize RPC manager.
        
        Args:
            rpc_endpoint: RPC endpoint URL
            commitment: Transaction commitment level
            timeout: Request timeout in seconds
        """
        self.rpc_endpoint = rpc_endpoint or config.rpc_endpoint
        self.commitment = commitment or Commitment(config.commitment)
        self.timeout = timeout or config.rpc_timeout
        self.client: Optional[AsyncClient] = None
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def connect(self):
        """Establish RPC connection."""
        if self.client is None:
            logger.debug(f"Connecting to RPC endpoint: {self.rpc_endpoint}")
            
            # Create HTTP session with timeout
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
            
            # Create Solana client
            self.client = AsyncClient(
                self.rpc_endpoint,
                commitment=self.commitment,
                timeout=self.timeout
            )
            
            logger.info("RPC connection established", {
                'endpoint': self.rpc_endpoint,
                'commitment': str(self.commitment),
                'timeout': self.timeout
            })
    
    async def close(self):
        """Close RPC connection."""
        if self.client:
            await self.client.close()
            self.client = None
            logger.debug("RPC connection closed")
        
        if self._session:
            await self._session.close()
            self._session = None
    
    @retry_rpc_call(max_retries=3)
    async def get_account_info(self, pubkey: str) -> Dict[str, Any]:
        """
        Get account information.
        
        Args:
            pubkey: Account public key
            
        Returns:
            Account information
        """
        if not self.client:
            await self.connect()
        
        logger.debug(f"Getting account info for: {pubkey}")
        
        try:
            from solana.publickey import PublicKey
            account_info = await self.client.get_account_info(PublicKey(pubkey))
            
            logger.debug("Account info retrieved successfully", {
                'pubkey': pubkey,
                'exists': account_info.value is not None
            })
            
            return {
                'pubkey': pubkey,
                'account': account_info.value,
                'context': account_info.context
            }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}", {
                'pubkey': pubkey,
                'error': str(e)
            })
            raise
    
    @retry_rpc_call(max_retries=3)
    async def get_balance(self, pubkey: str) -> int:
        """
        Get account balance.
        
        Args:
            pubkey: Account public key
            
        Returns:
            Balance in lamports
        """
        if not self.client:
            await self.connect()
        
        logger.debug(f"Getting balance for: {pubkey}")
        
        try:
            from solana.publickey import PublicKey
            balance_response = await self.client.get_balance(PublicKey(pubkey))
            balance = balance_response.value
            
            logger.debug("Balance retrieved successfully", {
                'pubkey': pubkey,
                'balance': balance
            })
            
            return balance
            
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}", {
                'pubkey': pubkey,
                'error': str(e)
            })
            raise
    
    @retry_rpc_call(max_retries=3)
    async def get_recent_blockhash(self) -> str:
        """
        Get recent blockhash.
        
        Returns:
            Recent blockhash
        """
        if not self.client:
            await self.connect()
        
        logger.debug("Getting recent blockhash")
        
        try:
            blockhash_response = await self.client.get_recent_blockhash()
            blockhash = blockhash_response.value.blockhash
            
            logger.debug("Recent blockhash retrieved successfully", {
                'blockhash': str(blockhash)
            })
            
            return str(blockhash)
            
        except Exception as e:
            logger.error(f"Failed to get recent blockhash: {str(e)}")
            raise
    
    @retry_rpc_call(max_retries=3)
    async def send_transaction(self, 
                             transaction: str,
                             skip_preflight: bool = False,
                             max_retries: int = 3) -> str:
        """
        Send transaction to the network.
        
        Args:
            transaction: Serialized transaction
            skip_preflight: Whether to skip preflight checks
            max_retries: Maximum number of retries
            
        Returns:
            Transaction signature
        """
        if not self.client:
            await self.connect()
        
        logger.debug("Sending transaction", {
            'skip_preflight': skip_preflight,
            'max_retries': max_retries
        })
        
        try:
            from solana.transaction import Transaction
            from solders.transaction import Transaction as SoldersTransaction
            
            # Parse transaction
            if isinstance(transaction, str):
                tx = Transaction.deserialize(bytes.fromhex(transaction))
            else:
                tx = transaction
            
            # Send transaction
            opts = TxOpts(
                skip_preflight=skip_preflight,
                max_retries=max_retries
            )
            
            response = await self.client.send_transaction(tx, opts)
            tx_signature = str(response.value)
            
            logger.info("Transaction sent successfully", {
                'signature': tx_signature,
                'skip_preflight': skip_preflight
            })
            
            return tx_signature
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {str(e)}", {
                'error': str(e)
            })
            raise
    
    @retry_rpc_call(max_retries=5)
    async def confirm_transaction(self, signature: str, timeout: int = 60) -> bool:
        """
        Confirm transaction.
        
        Args:
            signature: Transaction signature
            timeout: Confirmation timeout in seconds
            
        Returns:
            True if confirmed, False otherwise
        """
        if not self.client:
            await self.connect()
        
        logger.debug(f"Confirming transaction: {signature}")
        
        try:
            from solana.publickey import PublicKey
            from solders.signature import Signature
            
            # Create signature object
            sig = Signature.from_string(signature)
            
            # Wait for confirmation
            confirmation = await self.client.confirm_transaction(sig, self.commitment)
            
            is_confirmed = confirmation.value[0].err is None
            
            logger.info("Transaction confirmation result", {
                'signature': signature,
                'confirmed': is_confirmed
            })
            
            return is_confirmed
            
        except Exception as e:
            logger.error(f"Failed to confirm transaction: {str(e)}", {
                'signature': signature,
                'error': str(e)
            })
            raise
    
    @retry_rpc_call(max_retries=3)
    async def get_token_accounts(self, owner: str, mint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get token accounts for an owner.
        
        Args:
            owner: Owner public key
            mint: Token mint address (optional)
            
        Returns:
            List of token accounts
        """
        if not self.client:
            await self.connect()
        
        logger.debug(f"Getting token accounts", {
            'owner': owner,
            'mint': mint
        })
        
        try:
            from solana.publickey import PublicKey
            from solana.rpc.types import TokenAccountOpts
            
            owner_pubkey = PublicKey(owner)
            
            if mint:
                mint_pubkey = PublicKey(mint)
                opts = TokenAccountOpts(mint=mint_pubkey)
            else:
                opts = TokenAccountOpts()
            
            response = await self.client.get_token_accounts_by_owner(owner_pubkey, opts)
            
            accounts = []
            for account in response.value:
                accounts.append({
                    'pubkey': str(account.pubkey),
                    'account': account.account
                })
            
            logger.debug("Token accounts retrieved successfully", {
                'owner': owner,
                'mint': mint,
                'count': len(accounts)
            })
            
            return accounts
            
        except Exception as e:
            logger.error(f"Failed to get token accounts: {str(e)}", {
                'owner': owner,
                'mint': mint,
                'error': str(e)
            })
            raise


# Global RPC manager instance
rpc_manager = RPCManager()