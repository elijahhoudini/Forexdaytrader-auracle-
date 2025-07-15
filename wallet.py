"""
AURACLE Wallet Module
====================

Enhanced wallet management with real Jupiter integration for Solana trading.
"""

import asyncio
import config
import time
import random
from typing import Optional, Dict, Any

# Try to import Solana libraries, fallback to minimal implementation
try:
    from solana.rpc.async_api import AsyncClient
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    import base58
    SOLANA_AVAILABLE = True
except ImportError:
    try:
        from minimal_solana import AsyncClient, Keypair, Pubkey, base58
        SOLANA_AVAILABLE = False
    except ImportError:
        SOLANA_AVAILABLE = False

from jupiter_api import JupiterTradeExecutor


class Wallet:
    def __init__(self):
        self.address = config.WALLET_ADDRESS
        self.demo_mode = config.get_demo_mode()
        self.keypair = None
        self.rpc_client = None
        self.jupiter_executor = None
        
        # Initialize RPC client
        if not self.demo_mode:
            self.rpc_client = AsyncClient(config.SOLANA_RPC_ENDPOINT)
            
            # Initialize keypair for live trading
            if hasattr(config, 'WALLET_PRIVATE_KEY') and config.WALLET_PRIVATE_KEY:
                try:
                    # Decode private key (assumes base58 encoded)
                    private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
                    self.keypair = Keypair.from_bytes(private_key_bytes)
                    
                    # Verify address matches
                    if str(self.keypair.pubkey()) != self.address:
                        print("⚠️ Warning: Private key doesn't match configured address")
                    
                except Exception as e:
                    print(f"❌ Failed to load private key: {e}")
                    self.demo_mode = True  # Fall back to demo mode
            else:
                print("⚠️ No private key configured, falling back to demo mode")
                self.demo_mode = True
        
        # Initialize Jupiter executor
        self.jupiter_executor = JupiterTradeExecutor(self.keypair)

        if self.demo_mode:
            print("🔶 Wallet initialized in DEMO mode with Jupiter simulation")
        else:
            print("🔥 Wallet initialized in LIVE mode with real Jupiter integration")
            print(f"📍 Address: {self.address[:8]}...")

    async def get_balance(self, token: str = "SOL") -> float:
        """Get wallet balance for specified token"""
        try:
            demo_mode = config.get_demo_mode()
            
            if demo_mode:
                print(f"[wallet] 🔶 Demo mode: Returning mock balance")
                return 1.0  # Demo balance
            else:
                print(f"[wallet] 🔥 Live mode: Fetching real balance from {config.SOLANA_RPC_ENDPOINT}")
                
                if token == "SOL":
                    # Get SOL balance
                    try:
                        response = await self.rpc_client.get_balance(Pubkey.from_string(self.address))
                        if response.value:
                            balance = response.value / 1e9  # Convert lamports to SOL
                            print(f"[wallet] 💰 SOL balance: {balance:.4f} SOL")
                            return balance
                        else:
                            print(f"[wallet] ❌ Failed to get SOL balance")
                            return 0.0
                    except Exception as balance_error:
                        print(f"[wallet] ❌ SOL balance error: {balance_error}")
                        return 0.0
                else:
                    # Get SPL token balance (would need token account lookup)
                    # For now, return demo value
                    print(f"[wallet] ⚠️ SPL token balance not implemented, returning demo value")
                    return 1.0
                
        except Exception as e:
            print(f"[wallet] ❌ Balance check error: {e}")
            return 0.0

    async def buy_token(self, mint: str, amount_sol: float) -> Dict[str, Any]:
        """Execute buy transaction via Jupiter"""
        try:
            demo_mode = config.get_demo_mode()
            mode_str = "🔶 DEMO" if demo_mode else "🔥 LIVE"
            
            print(f"[wallet] 🛒 {mode_str} - Buying {amount_sol} SOL worth of {mint[:8]}...")
            
            # Execute swap via Jupiter
            result = await self.jupiter_executor.buy_token(mint, amount_sol)
            
            if result["success"]:
                print(f"[wallet] ✅ {mode_str} buy successful!")
                
                # Log transaction details if available
                if "signature" in result:
                    print(f"[wallet] 📋 Transaction signature: {result['signature']}")
                    
                if "solscan_url" in result:
                    print(f"[wallet] 🔍 View on Solscan: {result['solscan_url']}")
                
                # Add wallet-specific metadata
                result.update({
                    "action": "buy",
                    "token_mint": mint,
                    "amount_sol": amount_sol,
                    "wallet_address": self.address,
                    "demo_mode": demo_mode
                })
                
                return result
            else:
                print(f"[wallet] ❌ Buy failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            print(f"[wallet] ❌ Buy error: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "buy",
                "token_mint": mint,
                "amount_sol": amount_sol
            }

    async def sell_token(self, mint: str, token_amount: int) -> Dict[str, Any]:
        """Execute sell transaction via Jupiter"""
        try:
            demo_mode = config.get_demo_mode()
            mode_str = "🔶 DEMO" if demo_mode else "🔥 LIVE"
            
            print(f"[wallet] 💰 {mode_str} - Selling {token_amount} of {mint[:8]}...")
            
            # Execute swap via Jupiter
            result = await self.jupiter_executor.sell_token(mint, token_amount)
            
            if result["success"]:
                print(f"[wallet] ✅ {mode_str} sell successful!")
                
                # Log transaction details if available
                if "signature" in result:
                    print(f"[wallet] 📋 Transaction signature: {result['signature']}")
                    
                if "solscan_url" in result:
                    print(f"[wallet] 🔍 View on Solscan: {result['solscan_url']}")
                
                # Add wallet-specific metadata
                result.update({
                    "action": "sell",
                    "token_mint": mint,
                    "token_amount": token_amount,
                    "wallet_address": self.address,
                    "demo_mode": demo_mode
                })
                
                return result
            else:
                print(f"[wallet] ❌ Sell failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            print(f"[wallet] ❌ Sell error: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": "sell",
                "token_mint": mint,
                "token_amount": token_amount
            }

    def send_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Legacy method - use buy_token/sell_token instead"""
        print("⚠️ send_transaction is deprecated, use buy_token/sell_token")
        
        action = tx_data.get("action", "unknown")
        if action == "buy":
            # Convert to async call
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.buy_token(
                    tx_data.get("token_mint", ""), 
                    tx_data.get("amount_sol", 0.01)
                )
            )
            loop.close()
            return result
        elif action == "sell":
            # Convert to async call  
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.sell_token(
                    tx_data.get("token_mint", ""), 
                    tx_data.get("token_amount", 1000)
                )
            )
            loop.close()
            return result
        else:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "signature": None
            }

    async def close(self):
        """Close connections"""
        if self.jupiter_executor:
            await self.jupiter_executor.close()
        if self.rpc_client:
            await self.rpc_client.close()