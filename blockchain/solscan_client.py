"""
Solscan Client Module
=====================

Provides interface to Solscan API for blockchain analytics,
transaction history, and token information.
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union
from .blockchain_config import config
from .blockchain_logger import logger
from .retry_decorator import retry_api_call


class SolscanClient:
    """Client for interacting with Solscan API."""
    
    def __init__(self, 
                 api_url: Optional[str] = None,
                 api_key: Optional[str] = None):
        """
        Initialize Solscan client.
        
        Args:
            api_url: Solscan API URL (uses config default if not provided)
            api_key: Solscan API key (uses config default if not provided)
        """
        self.api_url = api_url or config.solscan_api_url
        self.api_key = api_key or config.solscan_api_key
        self.session: Optional[aiohttp.ClientSession] = None
        self.headers = {
            'User-Agent': 'AURACLE-Bot/1.0',
            'Accept': 'application/json'
        }
        
        if self.api_key:
            self.headers['token'] = self.api_key
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    @retry_api_call(max_retries=3)
    async def get_account_info(self, account: str) -> Dict[str, Any]:
        """
        Get account information from Solscan.
        
        Args:
            account: Account public key
            
        Returns:
            Account information from Solscan
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan account info for: {account}")
        
        try:
            async with self.session.get(f"{self.api_url}/account/{account}") as response:
                response.raise_for_status()
                account_data = await response.json()
                
                logger.info("Solscan account info retrieved successfully", {
                    'account': account,
                    'type': account_data.get('data', {}).get('type')
                })
                
                return account_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan account info: {str(e)}", {
                'account': account,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token information from Solscan.
        
        Args:
            token_address: Token mint address
            
        Returns:
            Token information from Solscan
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan token info for: {token_address}")
        
        try:
            async with self.session.get(f"{self.api_url}/token/meta", 
                                      params={'tokenAddress': token_address}) as response:
                response.raise_for_status()
                token_data = await response.json()
                
                logger.info("Solscan token info retrieved successfully", {
                    'token_address': token_address,
                    'symbol': token_data.get('data', {}).get('symbol'),
                    'name': token_data.get('data', {}).get('name')
                })
                
                return token_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan token info: {str(e)}", {
                'token_address': token_address,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_token_holders(self, 
                               token_address: str,
                               offset: int = 0,
                               limit: int = 50) -> Dict[str, Any]:
        """
        Get token holders from Solscan.
        
        Args:
            token_address: Token mint address
            offset: Pagination offset
            limit: Number of holders to return
            
        Returns:
            Token holders information
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan token holders", {
            'token_address': token_address,
            'offset': offset,
            'limit': limit
        })
        
        try:
            params = {
                'tokenAddress': token_address,
                'offset': offset,
                'limit': limit
            }
            
            async with self.session.get(f"{self.api_url}/token/holders", 
                                      params=params) as response:
                response.raise_for_status()
                holders_data = await response.json()
                
                logger.info("Solscan token holders retrieved successfully", {
                    'token_address': token_address,
                    'count': len(holders_data.get('data', []))
                })
                
                return holders_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan token holders: {str(e)}", {
                'token_address': token_address,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_transaction_history(self,
                                    account: str,
                                    before: Optional[str] = None,
                                    limit: int = 50) -> Dict[str, Any]:
        """
        Get transaction history from Solscan.
        
        Args:
            account: Account public key
            before: Transaction signature to paginate before
            limit: Number of transactions to return
            
        Returns:
            Transaction history from Solscan
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan transaction history", {
            'account': account,
            'before': before,
            'limit': limit
        })
        
        try:
            params = {
                'account': account,
                'limit': limit
            }
            
            if before:
                params['before'] = before
            
            async with self.session.get(f"{self.api_url}/account/transactions", 
                                      params=params) as response:
                response.raise_for_status()
                history_data = await response.json()
                
                logger.info("Solscan transaction history retrieved successfully", {
                    'account': account,
                    'count': len(history_data.get('data', []))
                })
                
                return history_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan transaction history: {str(e)}", {
                'account': account,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_token_transfers(self,
                                token_address: str,
                                offset: int = 0,
                                limit: int = 50) -> Dict[str, Any]:
        """
        Get token transfer history from Solscan.
        
        Args:
            token_address: Token mint address
            offset: Pagination offset
            limit: Number of transfers to return
            
        Returns:
            Token transfer history
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan token transfers", {
            'token_address': token_address,
            'offset': offset,
            'limit': limit
        })
        
        try:
            params = {
                'tokenAddress': token_address,
                'offset': offset,
                'limit': limit
            }
            
            async with self.session.get(f"{self.api_url}/token/transfers", 
                                      params=params) as response:
                response.raise_for_status()
                transfers_data = await response.json()
                
                logger.info("Solscan token transfers retrieved successfully", {
                    'token_address': token_address,
                    'count': len(transfers_data.get('data', []))
                })
                
                return transfers_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan token transfers: {str(e)}", {
                'token_address': token_address,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_token_market_data(self, token_address: str) -> Dict[str, Any]:
        """
        Get token market data from Solscan.
        
        Args:
            token_address: Token mint address
            
        Returns:
            Token market data
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan token market data for: {token_address}")
        
        try:
            async with self.session.get(f"{self.api_url}/token/price", 
                                      params={'tokenAddress': token_address}) as response:
                response.raise_for_status()
                market_data = await response.json()
                
                logger.info("Solscan token market data retrieved successfully", {
                    'token_address': token_address,
                    'price': market_data.get('data', {}).get('price')
                })
                
                return market_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan token market data: {str(e)}", {
                'token_address': token_address,
                'error': str(e)
            })
            raise
    
    @retry_api_call(max_retries=3)
    async def get_nft_activities(self,
                               collection_id: str,
                               offset: int = 0,
                               limit: int = 50) -> Dict[str, Any]:
        """
        Get NFT activities from Solscan.
        
        Args:
            collection_id: NFT collection ID
            offset: Pagination offset
            limit: Number of activities to return
            
        Returns:
            NFT activities data
        """
        if not self.session:
            raise ValueError("Client not initialized. Use async context manager.")
        
        logger.debug(f"Getting Solscan NFT activities", {
            'collection_id': collection_id,
            'offset': offset,
            'limit': limit
        })
        
        try:
            params = {
                'collectionId': collection_id,
                'offset': offset,
                'limit': limit
            }
            
            async with self.session.get(f"{self.api_url}/nft/activities", 
                                      params=params) as response:
                response.raise_for_status()
                activities_data = await response.json()
                
                logger.info("Solscan NFT activities retrieved successfully", {
                    'collection_id': collection_id,
                    'count': len(activities_data.get('data', []))
                })
                
                return activities_data
                
        except Exception as e:
            logger.error(f"Failed to get Solscan NFT activities: {str(e)}", {
                'collection_id': collection_id,
                'error': str(e)
            })
            raise


# Global Solscan client instance
solscan_client = SolscanClient()