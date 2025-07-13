"""
Jupiter Swap Integration Module
==============================

Provides real trading functionality using Jupiter's swap API.
Handles token swaps, quote generation, and transaction execution.
Integrates with risk management for secure trading.
"""

import httpx
import json
import time
import base64
import asyncio
from typing import Dict, Any, Optional, List
from solders.transaction import Transaction
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solana.rpc.types import TxOpts
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.signature import Signature
import config
from logger import AuracleLogger
from jupiter_risk import JupiterRiskManager, initialize_risk_manager


class JupiterSwapClient:
    """
    Jupiter Swap API client for executing real token swaps on Solana.
    
    Provides methods for:
    - Getting swap quotes
    - Executing swaps
    - Handling slippage and price impact
    - Managing transaction confirmations
    """
    
    def __init__(self, rpc_client: Client, wallet_keypair: Optional[Keypair] = None):
        """
        Initialize Jupiter swap client.
        
        Args:
            rpc_client: Solana RPC client
            wallet_keypair: Wallet keypair for signing transactions
        """
        self.rpc_client = rpc_client
        self.wallet_keypair = wallet_keypair
        self.logger = AuracleLogger()
        
        # Initialize risk manager
        self.risk_manager = initialize_risk_manager(self.logger)
        
        # Jupiter API endpoints
        self.jupiter_quote_url = config.JUPITER_QUOTE_URL
        self.jupiter_swap_url = config.JUPITER_SWAP_URL
        self.jupiter_price_url = config.JUPITER_PRICE_URL
        
        # Configuration from config module
        self.default_slippage_bps = config.JUPITER_DEFAULT_SLIPPAGE_BPS
        self.max_slippage_bps = config.JUPITER_MAX_SLIPPAGE_BPS
        self.quote_timeout = config.JUPITER_QUOTE_TIMEOUT
        self.swap_timeout = config.JUPITER_SWAP_TIMEOUT
        
        print("✅ Jupiter Swap Client initialized with risk management")
        print(f"   Quote timeout: {self.quote_timeout}s")
        print(f"   Swap timeout: {self.swap_timeout}s")
        print(f"   Default slippage: {self.default_slippage_bps} BPS")
    
    async def get_quote(self, 
                       input_mint: str, 
                       output_mint: str, 
                       amount: int,
                       slippage_bps: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get a swap quote from Jupiter.
        
        Args:
            input_mint: Input token mint address
            output_mint: Output token mint address
            amount: Amount to swap (in token's smallest unit)
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Quote data or None if failed
        """
        try:
            slippage = slippage_bps or self.default_slippage_bps
            
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": str(slippage),
                "onlyDirectRoutes": "false",
                "asLegacyTransaction": "false"
            }
            
            async with httpx.AsyncClient(timeout=self.quote_timeout) as client:
                response = await client.get(self.jupiter_quote_url, params=params)
                
                if response.status_code == 200:
                    quote_data = response.json()
                    
                    # Validate quote
                    if self._validate_quote(quote_data):
                        print(f"✅ Jupiter quote received: {quote_data.get('outAmount', 'N/A')} tokens")
                        return quote_data
                    else:
                        print("❌ Invalid quote received from Jupiter")
                        return None
                else:
                    print(f"❌ Jupiter quote failed: {response.status_code}")
                    return None
                    
        except httpx.TimeoutException:
            print("⏰ Jupiter quote timeout")
            return None
        except Exception as e:
            print(f"❌ Jupiter quote error: {str(e)}")
            self.logger.log_error(f"Jupiter quote error: {str(e)}")
            return None
    
    async def execute_swap(self, quote: Dict[str, Any]) -> Optional[str]:
        """
        Execute a swap transaction using Jupiter.
        
        Args:
            quote: Quote data from get_quote()
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            if not self.wallet_keypair:
                print("❌ No wallet keypair provided for swap execution")
                return None
            
            # Prepare swap request
            swap_request = {
                "quoteResponse": quote,
                "userPublicKey": str(self.wallet_keypair.pubkey()),
                "wrapAndUnwrapSol": True,
                "computeUnitPriceMicroLamports": 1000,
                "prioritizationFeeLamports": 1000
            }
            
            # Get swap transaction
            async with httpx.AsyncClient(timeout=self.swap_timeout) as client:
                response = await client.post(
                    self.jupiter_swap_url,
                    json=swap_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"❌ Jupiter swap request failed: {response.status_code}")
                    return None
                
                swap_data = response.json()
                
                # Extract and deserialize transaction
                if "swapTransaction" not in swap_data:
                    print("❌ No swap transaction in response")
                    return None
                
                transaction_data = swap_data["swapTransaction"]
                transaction_bytes = base64.b64decode(transaction_data)
                transaction = Transaction.deserialize(transaction_bytes)
                
                # Sign transaction
                transaction.sign(self.wallet_keypair)
                
                # Send transaction
                tx_opts = TxOpts(
                    skip_preflight=False,
                    preflight_commitment=Commitment("processed"),
                    max_retries=3
                )
                
                result = self.rpc_client.send_transaction(
                    transaction,
                    opts=tx_opts
                )
                
                if result.value:
                    signature = str(result.value)
                    print(f"✅ Jupiter swap executed: {signature}")
                    
                    # Wait for confirmation
                    confirmed = await self._wait_for_confirmation(signature)
                    if confirmed:
                        print(f"✅ Swap confirmed: {signature}")
                        return signature
                    else:
                        print(f"⏰ Swap confirmation timeout: {signature}")
                        return signature  # Return signature even if confirmation times out
                else:
                    print("❌ Failed to send swap transaction")
                    return None
                    
        except Exception as e:
            print(f"❌ Jupiter swap execution error: {str(e)}")
            self.logger.log_error(f"Jupiter swap execution error: {str(e)}")
            return None
    
    async def buy_token(self, 
                       token_mint: str, 
                       sol_amount: float,
                       token_data: Optional[Dict[str, Any]] = None,
                       slippage_bps: Optional[int] = None) -> Optional[str]:
        """
        Buy tokens using SOL via Jupiter swap with risk management.
        
        Args:
            token_mint: Token mint address to buy
            sol_amount: Amount of SOL to spend
            token_data: Token information for risk assessment
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            # SOL mint address
            sol_mint = "So11111111111111111111111111111111111111112"
            
            # Convert SOL amount to lamports
            lamports = int(sol_amount * 1_000_000_000)
            
            print(f"🛒 Getting Jupiter quote: {sol_amount} SOL -> {token_mint[:8]}...")
            
            # Get quote
            quote = await self.get_quote(
                input_mint=sol_mint,
                output_mint=token_mint,
                amount=lamports,
                slippage_bps=slippage_bps
            )
            
            if not quote:
                print("❌ Failed to get Jupiter quote for buy")
                return None
            
            # Risk assessment
            current_balance = sol_amount + 0.1  # Assume we have balance (simplified)
            risk_assessment = self.risk_manager.assess_swap_risk(
                quote=quote,
                token_data=token_data or {},
                trade_amount_sol=sol_amount,
                current_balance=current_balance
            )
            
            # Check risk assessment
            if risk_assessment["recommendation"] == "REJECT":
                print(f"❌ Trade rejected by risk manager: {risk_assessment['overall_risk']} risk")
                for issue in risk_assessment["critical_issues"]:
                    print(f"   - {issue}")
                return None
            
            if risk_assessment["recommendation"] == "CAUTION":
                print(f"⚠️ Trade proceeding with caution: {risk_assessment['overall_risk']} risk")
                for warning in risk_assessment["warnings"]:
                    print(f"   - {warning}")
            
            # Execute swap
            print(f"🔄 Executing buy swap: {sol_amount} SOL -> {token_mint[:8]}...")
            start_time = time.time()
            signature = await self.execute_swap(quote)
            
            if signature:
                # Monitor performance
                performance_metrics = self.risk_manager.monitor_transaction_performance(
                    signature, start_time
                )
                
                # Log successful buy
                self.logger.log_trade("BUY", {
                    "mint": token_mint,
                    "sol_amount": sol_amount,
                    "expected_tokens": quote.get("outAmount", "N/A"),
                    "price_impact": quote.get("priceImpactPct", 0),
                    "signature": signature,
                    "execution_time": performance_metrics.get("execution_time", 0),
                    "risk_score": risk_assessment["risk_score"]
                })
                
                return signature
            else:
                print("❌ Buy swap execution failed")
                return None
                
        except Exception as e:
            print(f"❌ Jupiter buy error: {str(e)}")
            self.logger.log_error(f"Jupiter buy error: {str(e)}")
            return None
    
    async def sell_token(self, 
                        token_mint: str, 
                        token_amount: int,
                        slippage_bps: Optional[int] = None) -> Optional[str]:
        """
        Sell tokens for SOL via Jupiter swap.
        
        Args:
            token_mint: Token mint address to sell
            token_amount: Amount of tokens to sell (in smallest unit)
            slippage_bps: Slippage tolerance in basis points
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            # SOL mint address
            sol_mint = "So11111111111111111111111111111111111111112"
            
            print(f"💰 Getting Jupiter quote: {token_amount} tokens -> SOL...")
            
            # Get quote
            quote = await self.get_quote(
                input_mint=token_mint,
                output_mint=sol_mint,
                amount=token_amount,
                slippage_bps=slippage_bps
            )
            
            if not quote:
                print("❌ Failed to get Jupiter quote for sell")
                return None
            
            # Check price impact
            price_impact = quote.get("priceImpactPct", 0)
            if abs(price_impact) > 5.0:  # 5% price impact limit
                print(f"⚠️ High price impact: {price_impact}% - skipping trade")
                return None
            
            # Execute swap
            print(f"🔄 Executing sell swap: {token_amount} tokens -> SOL...")
            signature = await self.execute_swap(quote)
            
            if signature:
                # Log successful sell
                expected_sol = int(quote.get("outAmount", 0)) / 1_000_000_000
                self.logger.log_trade("SELL", {
                    "mint": token_mint,
                    "token_amount": token_amount,
                    "expected_sol": expected_sol,
                    "price_impact": price_impact,
                    "signature": signature
                })
                
                return signature
            else:
                print("❌ Sell swap execution failed")
                return None
                
        except Exception as e:
            print(f"❌ Jupiter sell error: {str(e)}")
            self.logger.log_error(f"Jupiter sell error: {str(e)}")
            return None
    
    async def get_token_price(self, token_mint: str) -> Optional[float]:
        """
        Get current token price from Jupiter.
        
        Args:
            token_mint: Token mint address
            
        Returns:
            Price in USD or None if failed
        """
        try:
            params = {"ids": token_mint}
            
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(self.jupiter_price_url, params=params)
                
                if response.status_code == 200:
                    price_data = response.json()
                    token_data = price_data.get("data", {}).get(token_mint)
                    
                    if token_data:
                        return float(token_data.get("price", 0))
                    
                return None
                
        except Exception as e:
            print(f"❌ Error getting token price: {str(e)}")
            return None
    
    def _validate_quote(self, quote: Dict[str, Any]) -> bool:
        """
        Validate quote data.
        
        Args:
            quote: Quote data to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            required_fields = ["inputMint", "outputMint", "inAmount", "outAmount"]
            for field in required_fields:
                if field not in quote:
                    print(f"❌ Missing required field in quote: {field}")
                    return False
            
            # Check amounts
            in_amount = int(quote.get("inAmount", 0))
            out_amount = int(quote.get("outAmount", 0))
            
            if in_amount <= 0 or out_amount <= 0:
                print("❌ Invalid amounts in quote")
                return False
            
            # Check price impact
            price_impact = abs(quote.get("priceImpactPct", 0))
            if price_impact > 10.0:  # 10% maximum price impact
                print(f"❌ Price impact too high: {price_impact}%")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Quote validation error: {str(e)}")
            return False
    
    async def _wait_for_confirmation(self, signature: str, max_retries: int = 30) -> bool:
        """
        Wait for transaction confirmation.
        
        Args:
            signature: Transaction signature
            max_retries: Maximum number of retries
            
        Returns:
            True if confirmed, False if timeout
        """
        try:
            for attempt in range(max_retries):
                try:
                    result = self.rpc_client.get_signature_statuses([Signature.from_string(signature)])
                    
                    if result.value and result.value[0]:
                        status = result.value[0]
                        if status.confirmation_status in ["confirmed", "finalized"]:
                            return True
                        elif status.err:
                            print(f"❌ Transaction failed: {status.err}")
                            return False
                    
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    print(f"⚠️ Confirmation check error: {str(e)}")
                    await asyncio.sleep(1)
            
            return False
            
        except Exception as e:
            print(f"❌ Confirmation wait error: {str(e)}")
            return False


# Global Jupiter client instance
jupiter_client = None


def get_jupiter_client() -> Optional[JupiterSwapClient]:
    """
    Get the global Jupiter client instance.
    
    Returns:
        Jupiter client instance or None if not initialized
    """
    global jupiter_client
    return jupiter_client


def initialize_jupiter_client(rpc_client: Client, wallet_keypair: Optional[Keypair] = None) -> JupiterSwapClient:
    """
    Initialize the global Jupiter client instance.
    
    Args:
        rpc_client: Solana RPC client
        wallet_keypair: Wallet keypair for signing transactions
        
    Returns:
        Jupiter client instance
    """
    global jupiter_client
    jupiter_client = JupiterSwapClient(rpc_client, wallet_keypair)
    return jupiter_client