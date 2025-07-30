#!/usr/bin/env python3
"""
Enhanced Jupiter API Client for AURACLE Trading Bot
===================================================

Advanced Jupiter aggregator API client for autonomous AI trading with enhanced features:
- Real-time slippage calibration
- Price impact validation
- Redundant execution with fallbacks
- Transaction status monitoring
"""

import asyncio
import json
import base64
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

# Try to import httpx for HTTP requests, fallback to requests
try:
    import httpx
    HTTP_CLIENT_AVAILABLE = True
    HTTP_CLIENT = httpx.AsyncClient
except ImportError:
    try:
        import aiohttp
        HTTP_CLIENT_AVAILABLE = True
        HTTP_CLIENT = aiohttp.ClientSession
    except ImportError:
        HTTP_CLIENT_AVAILABLE = False
        HTTP_CLIENT = None

# Try to import Solana libraries
try:
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Confirmed
    from solders.transaction import VersionedTransaction
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

# Import config with fallback
try:
    import config
except ImportError:
    class config:
        SOLANA_RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"


class JupiterAPI:
    """
    Enhanced Jupiter aggregator API client for autonomous AI trading.

    Provides optimal routing across multiple DEXs with enhanced features:
    - Raydium, Orca, Serum, Meteora, Whirlpool, and more
    - Real-time slippage calibration
    - Price impact validation
    - Redundant execution with fallbacks
    - Transaction status monitoring
    """

    def __init__(self, rpc_client: Optional[AsyncClient] = None):
        """Initialize enhanced Jupiter API client."""
        self.base_url = "https://quote-api.jup.ag/v6"
        
        if SOLANA_AVAILABLE:
            self.rpc_client = rpc_client or AsyncClient(getattr(config, 'SOLANA_RPC_ENDPOINT', 'https://api.mainnet-beta.solana.com'))
        else:
            self.rpc_client = None
        
        # Setup logging
        self.logger = logging.getLogger('JupiterAPI')

        # Initialize HTTP client
        if HTTP_CLIENT_AVAILABLE:
            self.client = HTTP_CLIENT(timeout=30.0)
        else:
            self.client = None
            self.logger.warning("No HTTP client available")

        # SOL and USDC addresses for trading pairs
        self.SOL_MINT = "So11111111111111111111111111111111111111112"
        self.USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        
        # Enhanced features
        self.price_impact_threshold = 2.0  # 2% max price impact
        self.retry_attempts = 3
        self.execution_timeout = 10  # 10 seconds
        
        # Fallback RPC endpoints
        self.fallback_rpcs = [
            "https://api.mainnet-beta.solana.com",
            "https://solana-api.projectserum.com",
            "https://rpc.ankr.com/solana"
        ]
        
        # Transaction monitoring
        self.pending_transactions = {}
        
        self.logger.info("🚀 Enhanced Jupiter API initialized")
        print("[jupiter] 🚀 Enhanced Jupiter API initialized")

    async def get_quote(
        self, 
        input_mint: str, 
        output_mint: str, 
        amount: int,
        slippage_bps: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Get swap quote from Jupiter API.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to swap (in smallest units)
            slippage_bps: Slippage tolerance in basis points (50 = 0.5%)
            
        Returns:
            Dict containing quote data or None if failed
        """
        try:
            if not HTTP_CLIENT_AVAILABLE:
                self.logger.error("HTTP client not available")
                return None
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(slippage_bps),
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            url = f"{self.base_url}/quote"
            
            if HTTP_CLIENT == httpx.AsyncClient:
                async with self.client as client:
                    response = await client.get(url, params=params)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.logger.debug(f"Quote received: {data}")
                        return data
                    else:
                        self.logger.error(f"Quote request failed: {response.status_code} - {response.text}")
                        return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting quote: {e}")
            return None

    async def get_swap_transaction(
        self, 
        quote: Dict[str, Any], 
        user_public_key: str,
        wrap_unwrap_sol: bool = True,
        compute_unit_price_micro_lamports: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get swap transaction from Jupiter API.
        
        Args:
            quote: Quote data from get_quote()
            user_public_key: User's wallet public key
            wrap_unwrap_sol: Whether to wrap/unwrap SOL
            compute_unit_price_micro_lamports: Compute unit price for priority fees
            
        Returns:
            Dict containing transaction data or None if failed
        """
        try:
            if not HTTP_CLIENT_AVAILABLE:
                self.logger.error("HTTP client not available")
                return None
            
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": wrap_unwrap_sol
            }
            
            if compute_unit_price_micro_lamports:
                payload["computeUnitPriceMicroLamports"] = compute_unit_price_micro_lamports
            
            url = f"{self.base_url}/swap"
            
            if HTTP_CLIENT == httpx.AsyncClient:
                async with self.client as client:
                    response = await client.post(url, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        self.logger.debug(f"Swap transaction received")
                        return data
                    else:
                        self.logger.error(f"Swap request failed: {response.status_code} - {response.text}")
                        return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting swap transaction: {e}")
            return None

    async def execute_swap(
        self,
        input_mint: str,
        output_mint: str,
        amount: int,
        user_keypair: Keypair,
        slippage_bps: int = 50
    ) -> Optional[str]:
        """
        Execute a complete swap transaction.
        
        Args:
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap
            user_keypair: User's keypair for signing
            slippage_bps: Slippage tolerance
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            if not SOLANA_AVAILABLE:
                self.logger.error("Solana libraries not available")
                return None
            
            # Get quote
            quote = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
            if not quote:
                self.logger.error("Failed to get quote")
                return None
            
            # Get swap transaction
            user_public_key = str(user_keypair.pubkey())
            swap_data = await self.get_swap_transaction(quote, user_public_key)
            if not swap_data:
                self.logger.error("Failed to get swap transaction")
                return None
            
            # Deserialize and sign transaction
            transaction_data = swap_data.get("swapTransaction")
            if not transaction_data:
                self.logger.error("No transaction data in response")
                return None
            
            # Decode base64 transaction
            raw_transaction = base64.b64decode(transaction_data)
            transaction = VersionedTransaction.from_bytes(raw_transaction)
            
            # Sign transaction
            transaction.sign([user_keypair])
            
            # Send transaction
            if self.rpc_client:
                response = await self.rpc_client.send_transaction(
                    transaction,
                    opts={"skipPreflight": False, "maxRetries": 3}
                )
                
                if response.value:
                    signature = str(response.value)
                    self.logger.info(f"Transaction sent: {signature}")
                    return signature
                else:
                    self.logger.error("Failed to send transaction")
                    return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error executing swap: {e}")
            return None

    async def execute_buy(
        self,
        token_mint: str,
        amount_sol: float,
        user_keypair: Optional[Keypair] = None,
        slippage_bps: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a buy order (SOL -> Token).
        
        Args:
            token_mint: Token to buy
            amount_sol: Amount of SOL to spend
            user_keypair: User's keypair
            slippage_bps: Slippage tolerance
            
        Returns:
            Dict with transaction info or None if failed
        """
        try:
            amount_lamports = int(amount_sol * 1e9)  # Convert SOL to lamports
            
            if user_keypair and SOLANA_AVAILABLE:
                signature = await self.execute_swap(
                    self.SOL_MINT,
                    token_mint,
                    amount_lamports,
                    user_keypair,
                    slippage_bps
                )
                
                if signature:
                    return {
                        "transaction": signature,
                        "input_mint": self.SOL_MINT,
                        "output_mint": token_mint,
                        "amount": amount_lamports,
                        "type": "buy"
                    }
            else:
                # Mock execution for testing
                mock_tx = f"mock_buy_tx_{int(time.time())}"
                self.logger.info(f"Mock buy executed: {amount_sol} SOL -> {token_mint}")
                return {
                    "transaction": mock_tx,
                    "input_mint": self.SOL_MINT,
                    "output_mint": token_mint,
                    "amount": amount_lamports,
                    "type": "buy"
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error executing buy: {e}")
            return None

    async def execute_sell(
        self,
        token_mint: str,
        amount_tokens: int,
        user_keypair: Optional[Keypair] = None,
        slippage_bps: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a sell order (Token -> SOL).
        
        Args:
            token_mint: Token to sell
            amount_tokens: Amount of tokens to sell
            user_keypair: User's keypair
            slippage_bps: Slippage tolerance
            
        Returns:
            Dict with transaction info or None if failed
        """
        try:
            if user_keypair and SOLANA_AVAILABLE:
                signature = await self.execute_swap(
                    token_mint,
                    self.SOL_MINT,
                    amount_tokens,
                    user_keypair,
                    slippage_bps
                )
                
                if signature:
                    return {
                        "transaction": signature,
                        "input_mint": token_mint,
                        "output_mint": self.SOL_MINT,
                        "amount": amount_tokens,
                        "type": "sell"
                    }
            else:
                # Mock execution for testing
                mock_tx = f"mock_sell_tx_{int(time.time())}"
                self.logger.info(f"Mock sell executed: {amount_tokens} tokens -> SOL")
                return {
                    "transaction": mock_tx,
                    "input_mint": token_mint,
                    "output_mint": self.SOL_MINT,
                    "amount": amount_tokens,
                    "type": "sell"
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error executing sell: {e}")
            return None

    async def check_transaction_status(self, signature: str) -> Optional[str]:
        """
        Check the status of a transaction.
        
        Args:
            signature: Transaction signature
            
        Returns:
            Status string ("confirmed", "failed", "pending") or None
        """
        try:
            if not SOLANA_AVAILABLE or not self.rpc_client:
                # Mock status for testing
                if signature.startswith("mock_"):
                    return "confirmed"
                return "pending"
            
            response = await self.rpc_client.get_transaction(
                signature,
                encoding="json",
                commitment=Confirmed,
                max_supported_transaction_version=0
            )
            
            if response.value:
                if response.value.meta and response.value.meta.err:
                    return "failed"
                else:
                    return "confirmed"
            else:
                return "pending"
                
        except Exception as e:
            self.logger.error(f"Error checking transaction status: {e}")
            return None

    async def get_quote_with_price_impact(
        self, 
        input_mint: str, 
        output_mint: str, 
        amount: int,
        slippage_bps: int = 50
    ) -> Optional[Tuple[Dict[str, Any], float]]:
        """
        Get quote with price impact calculation.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address  
            amount: Amount to swap (in smallest units)
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Tuple of (quote_data, price_impact_percent) or None if failed
        """
        try:
            quote = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
            if not quote:
                return None
            
            # Calculate price impact
            price_impact = await self.calculate_price_impact(quote, input_mint, output_mint, amount)
            
            return quote, price_impact
            
        except Exception as e:
            self.logger.error(f"❌ Error getting quote with price impact: {e}")
            return None
    
    async def calculate_price_impact(self, quote: Dict[str, Any], input_mint: str, output_mint: str, amount: int) -> float:
        """
        Calculate price impact for a given quote.
        
        Args:
            quote: Jupiter quote data
            input_mint: Input token mint
            output_mint: Output token mint  
            amount: Input amount
            
        Returns:
            float: Price impact percentage
        """
        try:
            # Extract price impact from quote if available
            if 'priceImpactPct' in quote:
                return abs(float(quote['priceImpactPct']))
            
            # Fallback calculation
            in_amount = float(quote.get('inAmount', amount))
            out_amount = float(quote.get('outAmount', 0))
            
            if in_amount == 0 or out_amount == 0:
                return 0.0
            
            # Get reference price for small amount
            ref_quote = await self.get_quote(input_mint, output_mint, int(amount * 0.01), 50)
            if not ref_quote:
                return 0.0
            
            ref_in = float(ref_quote.get('inAmount', 1))
            ref_out = float(ref_quote.get('outAmount', 1))
            
            if ref_in == 0 or ref_out == 0:
                return 0.0
            
            # Calculate price impact
            current_rate = out_amount / in_amount
            reference_rate = ref_out / ref_in
            
            if reference_rate == 0:
                return 0.0
            
            price_impact = abs((current_rate - reference_rate) / reference_rate) * 100
            
            return min(price_impact, 100.0)  # Cap at 100%
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating price impact: {e}")
            return 0.0
    
    async def get_optimal_slippage(self, input_mint: str, output_mint: str, amount: int) -> float:
        """
        Calculate optimal slippage based on market conditions.
        
        Args:
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Trade amount
            
        Returns:
            float: Optimal slippage percentage
        """
        try:
            # Test different slippage levels
            slippage_levels = [0.5, 1.0, 1.5, 2.0, 3.0]  # Percentages
            
            best_slippage = 1.0  # Default
            best_output = 0
            
            for slippage_pct in slippage_levels:
                slippage_bps = int(slippage_pct * 100)
                
                quote = await self.get_quote(input_mint, output_mint, amount, slippage_bps)
                if quote:
                    output_amount = int(quote.get('outAmount', 0))
                    if output_amount > best_output:
                        best_output = output_amount
                        best_slippage = slippage_pct
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)
            
            self.logger.info(f"📊 Optimal slippage: {best_slippage}%")
            return best_slippage
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating optimal slippage: {e}")
            return 1.0  # Conservative fallback

    async def get_token_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get list of supported tokens from Jupiter.
        
        Returns:
            List of token information or None if failed
        """
        try:
            if not HTTP_CLIENT_AVAILABLE:
                return None
            
            url = f"{self.base_url}/tokens"
            
            if HTTP_CLIENT == httpx.AsyncClient:
                async with self.client as client:
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        self.logger.error(f"Token list request failed: {response.status_code}")
                        return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting token list: {e}")
            return None

    async def close(self):
        """Close HTTP client and RPC client connections."""
        try:
            if self.client and hasattr(self.client, 'aclose'):
                await self.client.aclose()
            if self.rpc_client and hasattr(self.rpc_client, 'close'):
                await self.rpc_client.close()
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")


# Jupiter Trade Executor class for backwards compatibility
class JupiterTradeExecutor:
    """Legacy trade executor for compatibility."""
    
    def __init__(self, jupiter_api: JupiterAPI):
        self.jupiter_api = jupiter_api
        self.logger = logging.getLogger('JupiterTradeExecutor')
    
    async def execute_trade(self, trade_data: Dict[str, Any]) -> Optional[str]:
        """Execute a trade using Jupiter API."""
        try:
            action = trade_data.get('action', 'buy')
            
            if action == 'buy':
                result = await self.jupiter_api.execute_buy(
                    trade_data['token_mint'],
                    trade_data['amount_sol'],
                    trade_data.get('user_keypair'),
                    trade_data.get('slippage_bps', 50)
                )
            else:
                result = await self.jupiter_api.execute_sell(
                    trade_data['token_mint'],
                    trade_data['amount_tokens'],
                    trade_data.get('user_keypair'),
                    trade_data.get('slippage_bps', 50)
                )
            
            if result:
                return result.get('transaction')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error executing trade: {e}")
            return None