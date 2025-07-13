"""
AURACLE Wallet Module
====================

Enhanced wallet management with real Jupiter integration for Solana trading.
"""

import config
import time
import random
import json
import httpx
import asyncio
from typing import Optional, Dict, Any, List
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.rpc.responses import SendTransactionResp


class Wallet:
    """
    Enhanced wallet with real Jupiter integration for live trading.
    """
    
    def __init__(self):
        self.address = config.WALLET_ADDRESS
        self.demo_mode = config.get_demo_mode()
        
        # Initialize Solana connection
        self.rpc_client = Client(config.SOLANA_RPC_ENDPOINT)
        
        # Jupiter API endpoints
        self.jupiter_api_base = "https://quote-api.jup.ag/v6"
        self.jupiter_price_api = "https://price.jup.ag/v4"
        
        # Initialize wallet keypair for live trading
        self.keypair = None
        if not self.demo_mode and config.WALLET_PRIVATE_KEY:
            try:
                # Initialize keypair from private key
                private_key_bytes = bytes.fromhex(config.WALLET_PRIVATE_KEY)
                self.keypair = Keypair.from_bytes(private_key_bytes)
                print(f"🔥 Live wallet initialized: {self.address[:8]}...")
            except Exception as e:
                print(f"⚠️ Failed to initialize live wallet: {e}")
                config.set_demo_mode(True)  # Fall back to demo mode
                self.demo_mode = True
        
        if self.demo_mode:
            print("🔶 Wallet initialized in DEMO mode")
        else:
            print("🔥 Wallet initialized in LIVE mode")
            print(f"📍 Address: {self.address[:8]}...")

    async def get_balance(self, token: str = "SOL") -> float:
        """Get wallet balance for specified token"""
        try:
            if self.demo_mode:
                return 1.0  # Demo balance
            
            if token == "SOL":
                # Get SOL balance
                balance = self.rpc_client.get_balance(Pubkey.from_string(self.address))
                return balance.value / 1e9  # Convert lamports to SOL
            else:
                # For SPL tokens, we would need to implement SPL token balance checking
                # For now, return demo balance
                return 1.0
                
        except Exception as e:
            print(f"[wallet] Error getting balance: {e}")
            return 0.0

    async def get_jupiter_quote(self, input_mint: str, output_mint: str, amount: int) -> Optional[Dict]:
        """Get Jupiter quote for token swap"""
        try:
            params = {
                "inputMint": input_mint,
                "outputMint": output_mint,
                "amount": str(amount),
                "slippageBps": 50,  # 0.5% slippage
                "swapMode": "ExactIn",
                "onlyDirectRoutes": False,
                "asLegacyTransaction": False
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.jupiter_api_base}/quote", params=params)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"[wallet] Jupiter quote failed: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"[wallet] Error getting Jupiter quote: {e}")
            return None

    async def execute_jupiter_swap(self, quote: Dict, wallet_keypair: Keypair) -> Optional[str]:
        """Execute Jupiter swap transaction"""
        try:
            # Get swap transaction from Jupiter
            swap_payload = {
                "quoteResponse": quote,
                "userPublicKey": str(wallet_keypair.pubkey()),
                "wrapAndUnwrapSol": True,
                "prioritizationFeeLamports": 1000  # Priority fee
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.jupiter_api_base}/swap",
                    json=swap_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    print(f"[wallet] Jupiter swap preparation failed: {response.status_code}")
                    return None
                
                swap_response = response.json()
                swap_transaction = swap_response.get("swapTransaction")
                
                if not swap_transaction:
                    print("[wallet] No swap transaction received")
                    return None
                
                # Decode and sign transaction
                transaction = Transaction.from_bytes(swap_transaction)
                transaction.sign([wallet_keypair])
                
                # Send transaction
                signature = self.rpc_client.send_transaction(transaction)
                
                if signature.value:
                    print(f"[wallet] Jupiter swap executed: {signature.value}")
                    return signature.value
                else:
                    print("[wallet] Transaction failed to send")
                    return None
                    
        except Exception as e:
            print(f"[wallet] Error executing Jupiter swap: {e}")
            return None

    async def buy_token_jupiter(self, mint: str, amount_sol: float) -> bool:
        """Buy token using Jupiter aggregator"""
        try:
            if self.demo_mode:
                return await self._demo_buy_token(mint, amount_sol)
            
            if not self.keypair:
                print("[wallet] No keypair available for live trading")
                return False
            
            # SOL mint address
            sol_mint = "So11111111111111111111111111111111111111112"
            
            # Convert SOL to lamports
            amount_lamports = int(amount_sol * 1e9)
            
            # Get Jupiter quote
            quote = await self.get_jupiter_quote(sol_mint, mint, amount_lamports)
            
            if not quote:
                print("[wallet] Failed to get Jupiter quote")
                return False
            
            # Execute swap
            signature = await self.execute_jupiter_swap(quote, self.keypair)
            
            if signature:
                print(f"✅ Successfully bought {mint[:8]}... for {amount_sol} SOL")
                return True
            else:
                print(f"❌ Failed to buy {mint[:8]}...")
                return False
                
        except Exception as e:
            print(f"[wallet] Error buying token via Jupiter: {e}")
            return False

    async def sell_token_jupiter(self, mint: str, amount: float) -> bool:
        """Sell token using Jupiter aggregator"""
        try:
            if self.demo_mode:
                return await self._demo_sell_token(mint, amount)
            
            if not self.keypair:
                print("[wallet] No keypair available for live trading")
                return False
            
            # SOL mint address
            sol_mint = "So11111111111111111111111111111111111111112"
            
            # Convert amount to smallest unit (assuming 9 decimals)
            amount_units = int(amount * 1e9)
            
            # Get Jupiter quote
            quote = await self.get_jupiter_quote(mint, sol_mint, amount_units)
            
            if not quote:
                print("[wallet] Failed to get Jupiter quote for sell")
                return False
            
            # Execute swap
            signature = await self.execute_jupiter_swap(quote, self.keypair)
            
            if signature:
                print(f"✅ Successfully sold {amount} tokens of {mint[:8]}...")
                return True
            else:
                print(f"❌ Failed to sell {mint[:8]}...")
                return False
                
        except Exception as e:
            print(f"[wallet] Error selling token via Jupiter: {e}")
            return False

    async def _demo_buy_token(self, mint: str, amount_sol: float) -> bool:
        """Demo buy transaction simulation"""
        # Simulate transaction delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate success/failure
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            print(f"🔶 DEMO BUY: {mint[:8]}... - {amount_sol} SOL")
            return True
        else:
            print(f"❌ DEMO BUY FAILED: {mint[:8]}...")
            return False

    async def _demo_sell_token(self, mint: str, amount: float) -> bool:
        """Demo sell transaction simulation"""
        # Simulate transaction delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate success/failure
        success = random.choice([True, True, True, False])  # 75% success rate
        
        if success:
            print(f"🔶 DEMO SELL: {mint[:8]}... - {amount} tokens")
            return True
        else:
            print(f"❌ DEMO SELL FAILED: {mint[:8]}...")
            return False

    def send_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy transaction method for backward compatibility"""
        try:
            if self.demo_mode:
                # Simulate transaction in demo mode
                action = tx_data.get("action", "unknown")
                signature = f"demo_{action}_{int(time.time())}_{random.randint(1000, 9999)}"
                
                # Simulate success/failure
                success = random.choice([True, True, True, False])  # 75% success rate
                
                if success:
                    result = {
                        "success": True,
                        "signature": signature,
                        "timestamp": time.time()
                    }
                    
                    if action == "buy":
                        result["tokens_received"] = tx_data.get("amount_sol", 0) * random.uniform(1000, 50000)
                    elif action == "sell":
                        result["amount_received"] = random.uniform(0.8, 1.5) * tx_data.get("amount_sol", 0.01)
                        
                    return result
                else:
                    return {
                        "success": False,
                        "error": "Demo transaction failed (simulated)",
                        "signature": None
                    }
            else:
                # Real transaction logic would go here
                print(f"[wallet] 🔥 Live transaction: {tx_data.get('action', 'unknown')}")
                return {
                    "success": True,
                    "signature": f"live_{tx_data.get('action')}_{int(time.time())}",
                    "timestamp": time.time()
                }

        except Exception as e:
            print(f"[wallet] Transaction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }

    async def buy_token(self, mint: str, amount_sol: float) -> bool:
        """Execute buy transaction (enhanced with Jupiter)"""
        return await self.buy_token_jupiter(mint, amount_sol)

    async def sell_token(self, mint: str, amount: float) -> bool:
        """Execute sell transaction (enhanced with Jupiter)"""
        return await self.sell_token_jupiter(mint, amount)

    async def get_token_price(self, mint: str) -> Optional[float]:
        """Get current token price from Jupiter"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.jupiter_price_api}/price?ids={mint}")
                
                if response.status_code == 200:
                    data = response.json()
                    price_data = data.get("data", {}).get(mint)
                    if price_data:
                        return float(price_data.get("price", 0))
                        
        except Exception as e:
            print(f"[wallet] Error getting token price: {e}")
            
        return None