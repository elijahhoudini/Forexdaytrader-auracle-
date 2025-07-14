"""
Token information utilities to replace Moralis API dependency.
Uses free public APIs like Jupiter and Solana RPC.
"""
import json
import logging
from typing import Dict, Optional, Tuple, Any
import requests
from solana.rpc.api import Client
from solders.pubkey import Pubkey

logger = logging.getLogger(__name__)

class TokenInfoProvider:
    """Provides token information using free public APIs"""
    
    def __init__(self, rpc_endpoint: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_endpoint = rpc_endpoint
        self.client = Client(rpc_endpoint)
        self.jupiter_api = "https://quote-api.jup.ag/v6"
        self.jupiter_token_list = "https://token.jup.ag/all"
        self.cache = {}
    
    def get_token_price(self, token_address: str) -> Optional[float]:
        """Get token price using Jupiter API"""
        try:
            # Check cache first
            if token_address in self.cache:
                return self.cache[token_address].get('price')
            
            # Use Jupiter price API
            response = requests.get(
                f"{self.jupiter_api}/price",
                params={"ids": token_address},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and token_address in data['data']:
                    price = float(data['data'][token_address]['price'])
                    self.cache[token_address] = {'price': price}
                    return price
            
            # Fallback: return None if price not found
            return None
            
        except Exception as e:
            logger.error(f"Error getting token price for {token_address}: {e}")
            return None
    
    def get_token_info(self, token_address: str) -> Tuple[str, str, int, float]:
        """
        Get token information compatible with existing code.
        Returns: (name, symbol, decimals, price)
        """
        try:
            # Check cache first
            if token_address in self.cache and 'full_info' in self.cache[token_address]:
                info = self.cache[token_address]['full_info']
                return info['name'], info['symbol'], info['decimals'], info['price']
            
            # Special handling for well-known tokens
            known_tokens = {
                'So11111111111111111111111111111111111111112': {
                    'name': 'Wrapped SOL',
                    'symbol': 'SOL',
                    'decimals': 9
                },
                'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB': {
                    'name': 'USDT',
                    'symbol': 'USDT',
                    'decimals': 6
                },
                'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v': {
                    'name': 'USD Coin',
                    'symbol': 'USDC',
                    'decimals': 6
                }
            }
            
            if token_address in known_tokens:
                token_info = known_tokens[token_address]
                price = self.get_token_price(token_address) or 0.0
                
                # Cache the result
                self.cache[token_address] = {
                    'full_info': {
                        'name': token_info['name'],
                        'symbol': token_info['symbol'],
                        'decimals': token_info['decimals'],
                        'price': price
                    }
                }
                
                return token_info['name'], token_info['symbol'], token_info['decimals'], price
            
            # Try to get info from Jupiter token list
            token_info = self._get_token_from_jupiter_list(token_address)
            if token_info:
                price = self.get_token_price(token_address) or 0.0
                
                # Cache the result
                self.cache[token_address] = {
                    'full_info': {
                        'name': token_info['name'],
                        'symbol': token_info['symbol'],
                        'decimals': token_info['decimals'],
                        'price': price
                    }
                }
                
                return token_info['name'], token_info['symbol'], token_info['decimals'], price
            
            # Fallback: try to get basic info from RPC
            try:
                pubkey = Pubkey.from_string(token_address)
                # This is a simplified fallback
                price = self.get_token_price(token_address) or 0.0
                
                # Return basic info
                return "Unknown Token", "UNK", 9, price
                
            except Exception as e:
                logger.error(f"Error getting token info from RPC: {e}")
                return "Unknown Token", "UNK", 9, 0.0
                
        except Exception as e:
            logger.error(f"Error getting token info for {token_address}: {e}")
            return "Unknown Token", "UNK", 9, 0.0
    
    def _get_token_from_jupiter_list(self, token_address: str) -> Optional[Dict[str, Any]]:
        """Get token info from Jupiter token list"""
        try:
            response = requests.get(self.jupiter_token_list, timeout=10)
            if response.status_code == 200:
                tokens = response.json()
                for token in tokens:
                    if token.get('address') == token_address:
                        return {
                            'name': token.get('name', 'Unknown'),
                            'symbol': token.get('symbol', 'UNK'),
                            'decimals': token.get('decimals', 9)
                        }
            return None
        except Exception as e:
            logger.error(f"Error getting token from Jupiter list: {e}")
            return None
    
    def get_sol_price(self) -> float:
        """Get current SOL price in USD"""
        sol_address = "So11111111111111111111111111111111111111112"
        price = self.get_token_price(sol_address)
        return price if price is not None else 0.0

# Global instance
_token_info_provider = None

def get_token_info_provider() -> TokenInfoProvider:
    """Get the global token info provider instance"""
    global _token_info_provider
    if _token_info_provider is None:
        _token_info_provider = TokenInfoProvider()
    return _token_info_provider

# Compatibility functions for existing code
def get_token_information(token_address: str) -> Tuple[str, str, int, float]:
    """
    Get token information compatible with existing code.
    Returns: (name, symbol, decimals, price)
    """
    return get_token_info_provider().get_token_info(token_address)

def get_sol_price() -> float:
    """Get current SOL price in USD"""
    return get_token_info_provider().get_sol_price()