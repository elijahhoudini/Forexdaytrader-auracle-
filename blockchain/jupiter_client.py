"""
Jupiter Client Module
=====================

Provides interface to Jupiter API for token swaps and price quotes
on the Solana blockchain.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from decimal import Decimal
from .blockchain_config import config
from .blockchain_logger import logger
from .retry_decorator import retry_api_call


class JupiterClient:
    """Client for interacting with Jupiter API."""
    
    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize Jupiter client.
        
        Args:
            api_url: Jupiter API URL (uses config default if not provided)
        """
        self.api_url = api_url or config.jupiter_api_url
        self.swap_url = config.jupiter_swap_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @retry_api_call(max_retries=3)
    async def get_quote(self, 
                       input_mint: str,
                       output_mint: str,
                       amount: Union[int, str],
                       slippage_bps: Optional[int] = None) -> Dict[str, Any]:
        """
        Get swap quote from Jupiter.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to swap (in smallest units)
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Quote response from Jupiter API
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        slippage_bps = slippage_bps or int(config.default_slippage * 10000)
        
        params = {
            'inputMint': input_mint,
            'outputMint': output_mint,
            'amount': str(amount),
            'slippageBps': slippage_bps,
            'onlyDirectRoutes': 'false',
            'asLegacyTransaction': 'false'
        }
        
        logger.debug(f"Getting Jupiter quote", {
            'input_mint': input_mint,
            'output_mint': output_mint,
            'amount': amount,
            'slippage_bps': slippage_bps
        })
        
        try:
            async with self.session.get(f"{self.api_url}/quote", params=params) as response:
                response.raise_for_status()
                quote_data = await response.json()
                
                logger.info("Jupiter quote retrieved successfully", {
                    'input_mint': input_mint,
                    'output_mint': output_mint,
                    'out_amount': quote_data.get('outAmount'),
                    'price_impact': quote_data.get('priceImpactPct')
                })
                
                return quote_data
                
        except Exception as e:
            logger.error(f"Failed to get Jupiter quote: {str(e)}", {
                'input_mint': input_mint,
                'output_mint': output_mint,
                'amount': amount,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_swap_transaction(self,
                                 quote: Dict[str, Any],
                                 user_public_key: str,
                                 wrap_unwrap_sol: bool = True,
                                 compute_unit_price_micro_lamports: Optional[int] = None) -> Dict[str, Any]:
        """
        Get swap transaction from Jupiter.
        
        Args:
            quote: Quote response from get_quote
            user_public_key: User's public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL
            compute_unit_price_micro_lamports: Compute unit price for priority fees
            
        Returns:
            Swap transaction response from Jupiter API
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        payload = {
            'quoteResponse': quote,
            'userPublicKey': user_public_key,
            'wrapAndUnwrapSol': wrap_unwrap_sol,
            'asLegacyTransaction': False
        }
        
        if compute_unit_price_micro_lamports:
            payload['computeUnitPriceMicroLamports'] = compute_unit_price_micro_lamports
        
        logger.debug("Getting Jupiter swap transaction", {
            'user_public_key': user_public_key,
            'input_mint': quote.get('inputMint'),
            'output_mint': quote.get('outputMint'),
            'compute_unit_price': compute_unit_price_micro_lamports
        })
        
        try:
            async with self.session.post(f"{self.swap_url}", json=payload) as response:
                response.raise_for_status()
                swap_data = await response.json()
                
                logger.info("Jupiter swap transaction retrieved successfully", {
                    'user_public_key': user_public_key,
                    'transaction_message': len(swap_data.get('swapTransaction', ''))
                })
                
                return swap_data
                
        except Exception as e:
            logger.error(f"Failed to get Jupiter swap transaction: {str(e)}", {
                'user_public_key': user_public_key,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_tokens(self) -> List[Dict[str, Any]]:
        """
        Get list of tokens supported by Jupiter.
        
        Returns:
            List of token information
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug("Getting Jupiter tokens list")
        
        try:
            async with self.session.get(f"{self.api_url}/tokens") as response:
                response.raise_for_status()
                tokens_data = await response.json()
                
                logger.info(f"Retrieved {len(tokens_data)} tokens from Jupiter")
                
                return tokens_data
                
        except Exception as e:
            logger.error(f"Failed to get Jupiter tokens: {str(e)}")
            raise
    
    @retry_api_call(max_retries=3)
    async def get_price(self, 
                       token_mint: str,
                       vs_token: str = "So11111111111111111111111111111111111111112") -> Dict[str, Any]:
        """
        Get token price from Jupiter.
        
        Args:
            token_mint: Token mint address
            vs_token: Reference token mint (default: SOL)
            
        Returns:
            Price information
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        params = {
            'ids': token_mint,
            'vsToken': vs_token
        }
        
        logger.debug(f"Getting Jupiter price", {
            'token_mint': token_mint,
            'vs_token': vs_token
        })
        
        try:
            async with self.session.get(f"{self.api_url}/price", params=params) as response:
                response.raise_for_status()
                price_data = await response.json()
                
                logger.info("Jupiter price retrieved successfully", {
                    'token_mint': token_mint,
                    'price': price_data.get('data', {}).get(token_mint, {}).get('price')
                })
                
                return price_data
                
        except Exception as e:
            logger.error(f"Failed to get Jupiter price: {str(e)}", {
                'token_mint': token_mint,
                'error': str(e)
            })
            raise


# Global Jupiter client instance
jupiter_client = JupiterClient()