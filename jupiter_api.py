"""
AURACLE Jupiter Aggregator Integration
=====================================

Real Jupiter API integration for optimal DEX routing and token swapping.
Provides actual Solana transaction building and execution via Jupiter.
"""

import asyncio
import json
import base64
import time
from typing import Dict, Any, Optional, List, Tuple

# Try to import httpx for HTTP requests, fallback to requests
try:
    import httpx
    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    try:
        import requests
        HTTP_CLIENT_AVAILABLE = False
    except ImportError:
        HTTP_CLIENT_AVAILABLE = False

# Try to import Solana libraries, fallback to minimal implementation
try:
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.types import TxOpts
    from solders.transaction import VersionedTransaction
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    from solders.system_program import TransferParams, transfer
    SOLANA_AVAILABLE = True
except ImportError:
    try:
        from minimal_solana import AsyncClient, TxOpts, VersionedTransaction, Pubkey, Keypair, TransferParams, transfer
        SOLANA_AVAILABLE = False
    except ImportError:
        SOLANA_AVAILABLE = False

import config


class JupiterAPI:
    """
    Jupiter aggregator API client for real Solana DEX trading.
    
    Provides optimal routing across multiple DEXs including:
    - Raydium, Orca, Serum, Meteora, Whirlpool, and more
    """
    
    def __init__(self, rpc_client: Optional[AsyncClient] = None):
        """Initialize Jupiter API client."""
        self.base_url = "https://quote-api.jup.ag/v6"
        self.rpc_client = rpc_client or AsyncClient(config.SOLANA_RPC_ENDPOINT)
        
        # Initialize HTTP client
        if HTTP_CLIENT_AVAILABLE:
            self.client = httpx.AsyncClient(timeout=10.0)
        else:
            self.client = None
        
        # SOL and USDC addresses for trading pairs
        self.SOL_MINT = "So11111111111111111111111111111111111111112"
        self.USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
        
        print("[jupiter] 🚀 Jupiter API initialized")
    
    async def get_quote(
        self, 
        input_mint: str, 
        output_mint: str, 
        amount: int,
        slippage_bps: int = 50  # 0.5% slippage
    ) -> Optional[Dict[str, Any]]:
        """
        Get a quote for swapping tokens via Jupiter.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address  
            amount: Amount to swap (in smallest units)
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Quote data or None if failed
        """
        try:
            # Validate inputs
            if not input_mint or not output_mint:
                print(f"[jupiter] ❌ Invalid mint addresses: input={input_mint}, output={output_mint}")
                return None
                
            if amount <= 0:
                print(f"[jupiter] ❌ Invalid amount: {amount}")
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
            
            # Use httpx if available, otherwise fallback to mock response
            if self.client:
                response = await self.client.get(url, params=params)
                
                if response.status_code == 200:
                    quote = response.json()
                    print(f"[jupiter] 📊 Quote: {amount} {input_mint[:8]}... -> {quote.get('outAmount', 0)} {output_mint[:8]}...")
                    return quote
                else:
                    error_text = response.text if hasattr(response, 'text') else "Unknown error"
                    print(f"[jupiter] ❌ Quote failed: {response.status_code} - {error_text}")
                    return None
            else:
                # Fallback to demo mode when no HTTP client
                if config.get_demo_mode():
                    import random
                    return {
                        "outAmount": str(int(amount * random.uniform(1000, 50000))),
                        "routePlan": [{"swapInfo": {"ammKey": "demo"}}],
                        "demo_fallback": True
                    }
                return None
                
        except Exception as e:
            print(f"[jupiter] ❌ Quote error: {e}")
            
            # In demo mode, generate a fake quote when network fails
            if config.get_demo_mode():
                import random
                return {
                    "outAmount": str(int(amount * random.uniform(1000, 50000))),
                    "routePlan": [{"swapInfo": {"ammKey": "demo"}}],
                    "demo_fallback": True
                }
            
            return None
    
    async def get_swap_transaction(
        self,
        quote: Dict[str, Any],
        user_public_key: str,
        priority_fee: int = 1000  # microlamports
    ) -> Optional[str]:
        """
        Get swap transaction data from Jupiter.
        
        Args:
            quote: Quote data from get_quote()
            user_public_key: User's wallet public key
            priority_fee: Priority fee in microlamports
            
        Returns:
            Base64 encoded transaction or None if failed
        """
        try:
            # Validate inputs
            if not quote:
                print(f"[jupiter] ❌ Invalid quote data provided")
                return None
                
            if not user_public_key:
                print(f"[jupiter] ❌ Invalid user public key provided")
                return None
                
            payload = {
                "quoteResponse": quote,
                "userPublicKey": user_public_key,
                "wrapAndUnwrapSol": True,
                "useSharedAccounts": True,
                "feeAccount": None,
                "prioritizationFeeLamports": priority_fee
            }
            
            url = f"{self.base_url}/swap"
            response = await self.client.post(
                url, 
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("swapTransaction")
            else:
                error_text = response.text if hasattr(response, 'text') else "Unknown error"
                print(f"[jupiter] ❌ Swap transaction failed: {response.status_code} - {error_text}")
                
                # Try to handle specific error cases
                if response.status_code == 400:
                    print(f"[jupiter] ⚠️ Bad request - check quote data and user public key")
                elif response.status_code == 429:
                    print(f"[jupiter] ⚠️ Rate limited - backing off")
                    
                return None
                
        except Exception as e:
            print(f"[jupiter] ❌ Swap transaction error: {e}")
            return None
    
    async def execute_swap(
        self,
        input_mint: str,
        output_mint: str, 
        amount_sol: float,
        wallet_keypair: Optional[Keypair] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete swap operation via Jupiter.
        
        Args:
            input_mint: Input token mint address (SOL if buying)
            output_mint: Output token mint address (token if buying)
            amount_sol: Amount of SOL to trade
            wallet_keypair: Wallet keypair for signing (None for demo mode)
            
        Returns:
            Transaction result dictionary
        """
        try:
            # Convert SOL to lamports
            amount_lamports = int(amount_sol * 1e9)
            
            # Get quote
            quote = await self.get_quote(
                input_mint=input_mint,
                output_mint=output_mint,
                amount=amount_lamports
            )
            
            if not quote:
                return {"success": False, "error": "Failed to get quote"}
            
            # In demo mode, simulate the swap
            if config.get_demo_mode():
                return await self._simulate_swap(quote, amount_sol)
            
            # Real mode - execute actual swap (only if network available)
            if not wallet_keypair:
                return {"success": False, "error": "Wallet keypair required for live trading"}
            
            user_public_key = str(wallet_keypair.pubkey())
            
            # Get swap transaction
            swap_tx_b64 = await self.get_swap_transaction(quote, user_public_key)
            if not swap_tx_b64:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            # Decode and sign transaction
            transaction_bytes = base64.b64decode(swap_tx_b64)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Sign transaction using the correct method
            transaction.sign([wallet_keypair])
            
            # Send transaction
            signature = await self.rpc_client.send_transaction(
                transaction,
                opts=TxOpts(skip_preflight=False, max_retries=3)
            )
            
            if signature.value:
                # Wait for confirmation
                await self._wait_for_confirmation(signature.value)
                
                return {
                    "success": True,
                    "signature": str(signature.value),
                    "input_amount": amount_lamports,
                    "output_amount": int(quote.get("outAmount", 0)),
                    "route_plan": quote.get("routePlan", []),
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "Transaction failed to send"}
                
        except Exception as e:
            print(f"[jupiter] ❌ Swap execution error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _simulate_swap(self, quote: Dict[str, Any], amount_sol: float) -> Dict[str, Any]:
        """Simulate swap for demo mode."""
        import random
        
        # Simulate success/failure (90% success rate)
        success = random.random() < 0.90
        
        if success:
            out_amount = int(quote.get("outAmount", 0))
            signature = f"demo_jupiter_{int(time.time())}_{random.randint(1000, 9999)}"
            
            return {
                "success": True,
                "signature": signature,
                "input_amount": int(amount_sol * 1e9),
                "output_amount": out_amount,
                "route_plan": quote.get("routePlan", []),
                "timestamp": time.time(),
                "demo_mode": True
            }
        else:
            return {
                "success": False,
                "error": "Demo swap failed (simulated)",
                "demo_mode": True
            }
    
    async def _wait_for_confirmation(self, signature: str, max_retries: int = 30) -> bool:
        """Wait for transaction confirmation."""
        for i in range(max_retries):
            try:
                response = await self.rpc_client.get_signature_statuses([signature])
                if response.value and response.value[0]:
                    status = response.value[0]
                    if status.confirmation_status:
                        print(f"[jupiter] ✅ Transaction confirmed: {signature}")
                        return True
                
                await asyncio.sleep(2)  # Wait 2 seconds between checks
                
            except Exception as e:
                print(f"[jupiter] ⚠️ Confirmation check error: {e}")
                
        print(f"[jupiter] ⚠️ Transaction confirmation timeout: {signature}")
        return False
    
    async def get_token_price(self, mint: str) -> Optional[float]:
        """Get current token price in USDC."""
        try:
            url = f"https://price.jup.ag/v4/price?ids={mint}"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                data = response.json()
                token_data = data.get("data", {}).get(mint)
                if token_data:
                    return float(token_data.get("price", 0))
            
            return None
            
        except Exception as e:
            print(f"[jupiter] ❌ Price fetch error: {e}")
            return None
    
    async def get_supported_tokens(self) -> List[Dict[str, Any]]:
        """Get list of supported tokens."""
        try:
            url = "https://token.jup.ag/all"
            response = await self.client.get(url)
            
            if response.status_code == 200:
                tokens = response.json()
                return tokens
            
            return []
            
        except Exception as e:
            print(f"[jupiter] ❌ Token list error: {e}")
            return []
    
    async def close(self):
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
        if hasattr(self.rpc_client, 'close'):
            await self.rpc_client.close()


class JupiterTradeExecutor:
    """High-level trade executor using Jupiter API."""
    
    def __init__(self, wallet_keypair: Optional[Keypair] = None):
        """Initialize trade executor."""
        self.jupiter = JupiterAPI()
        self.wallet_keypair = wallet_keypair
        
    async def buy_token(self, token_mint: str, amount_sol: float) -> Dict[str, Any]:
        """
        Buy token with SOL via Jupiter.
        
        Args:
            token_mint: Token mint address to buy
            amount_sol: Amount of SOL to spend
            
        Returns:
            Transaction result
        """
        return await self.jupiter.execute_swap(
            input_mint=self.jupiter.SOL_MINT,
            output_mint=token_mint,
            amount_sol=amount_sol,
            wallet_keypair=self.wallet_keypair
        )
    
    async def sell_token(self, token_mint: str, token_amount: int) -> Dict[str, Any]:
        """
        Sell token for SOL via Jupiter.
        
        Args:
            token_mint: Token mint address to sell
            token_amount: Amount of tokens to sell (in smallest units)
            
        Returns:
            Transaction result
        """
        # For selling, we need to quote the token amount
        quote = await self.jupiter.get_quote(
            input_mint=token_mint,
            output_mint=self.jupiter.SOL_MINT,
            amount=token_amount
        )
        
        if not quote:
            return {"success": False, "error": "Failed to get sell quote"}
        
        # Execute the swap using the quote
        try:
            if config.get_demo_mode():
                return await self.jupiter._simulate_swap(quote, 0.01)  # Demo amount
            
            if not self.wallet_keypair:
                return {"success": False, "error": "Wallet keypair required for live trading"}
            
            user_public_key = str(self.wallet_keypair.pubkey())
            swap_tx_b64 = await self.jupiter.get_swap_transaction(quote, user_public_key)
            
            if not swap_tx_b64:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            # Execute transaction similar to buy_token
            transaction_bytes = base64.b64decode(swap_tx_b64)
            transaction = VersionedTransaction.from_bytes(transaction_bytes)
            
            # Sign transaction using the correct method
            message = transaction.message
            signature = self.wallet_keypair.sign_message(message.serialize())
            signed_transaction = VersionedTransaction.populate(message, [signature])
            
            signature = await self.jupiter.rpc_client.send_transaction(
                signed_transaction,
                opts=TxOpts(skip_preflight=False, max_retries=3)
            )
            
            if signature.value:
                await self.jupiter._wait_for_confirmation(signature.value)
                
                return {
                    "success": True,
                    "signature": str(signature.value),
                    "input_amount": token_amount,
                    "output_amount": int(quote.get("outAmount", 0)),
                    "timestamp": time.time()
                }
            else:
                return {"success": False, "error": "Transaction failed to send"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close connections."""
        await self.jupiter.close()