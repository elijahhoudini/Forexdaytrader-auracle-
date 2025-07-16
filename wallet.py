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
                    print(f"[wallet] 🔐 Loading private key (length: {len(config.WALLET_PRIVATE_KEY)})")
                    
                    # Handle different private key formats
                    private_key_bytes = None
                    
                    # Try Base58 decoding first (standard Solana format)
                    try:
                        private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
                        print(f"[wallet] ✅ Base58 private key decoded successfully")
                        
                        # Solders keypair expects exactly 64 bytes for from_bytes (32 private + 32 public)
                        # If we only have 32 bytes, we need to derive the full keypair
                        if len(private_key_bytes) == 32:
                            # Create keypair from seed bytes
                            self.keypair = Keypair.from_seed(private_key_bytes)
                            print(f"[wallet] ✅ Keypair created from 32-byte seed")
                        elif len(private_key_bytes) == 64:
                            # Full keypair bytes
                            self.keypair = Keypair.from_bytes(private_key_bytes)
                            print(f"[wallet] ✅ Keypair created from 64-byte data")
                        else:
                            raise ValueError(f"Invalid private key length: {len(private_key_bytes)}, expected 32 or 64")
                            
                    except Exception as b58_error:
                        print(f"[wallet] ⚠️ Base58 decode failed: {b58_error}")
                        
                        # Try hex decoding as fallback
                        try:
                            if len(config.WALLET_PRIVATE_KEY) == 64:  # Hex encoded
                                private_key_bytes = bytes.fromhex(config.WALLET_PRIVATE_KEY)
                                self.keypair = Keypair.from_seed(private_key_bytes)
                                print(f"[wallet] ✅ Hex private key decoded successfully")
                            else:
                                print(f"[wallet] ❌ Invalid private key format")
                                raise ValueError("Invalid private key format")
                        except Exception as hex_error:
                            print(f"[wallet] ❌ Hex decode failed: {hex_error}")
                            raise ValueError("Could not decode private key")
                    
                    # Update address to match keypair
                    derived_address = str(self.keypair.pubkey())
                    if self.address and self.address != derived_address:
                        print(f"⚠️ Configured address: {self.address}")
                        print(f"⚠️ Derived address: {derived_address}")
                        print("⚠️ Using derived address from private key")
                    
                    self.address = derived_address
                    print(f"[wallet] ✅ Keypair loaded successfully: {self.address[:8]}...")

                except Exception as e:
                    print(f"❌ Failed to load private key: {e}")
                    print(f"❌ Private key format or content invalid")
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

                # For live trading, verify transaction on blockchain
                if not demo_mode and "signature" in result:
                    print(f"[wallet] 🔍 Verifying transaction on blockchain...")
                    
                    # Wait a moment for transaction to propagate
                    await asyncio.sleep(2)
                    
                    # Verify transaction status
                    try:
                        if self.rpc_client:
                            from solders.signature import Signature
                            sig = Signature.from_string(result['signature'])
                            response = await self.rpc_client.get_signature_statuses([sig])
                            
                            if response.value and response.value[0]:
                                if response.value[0].confirmation_status:
                                    print(f"[wallet] ✅ Transaction confirmed on blockchain")
                                else:
                                    print(f"[wallet] ⏳ Transaction pending confirmation")
                            else:
                                print(f"[wallet] ⚠️ Transaction not found on blockchain yet")
                    except Exception as verify_error:
                        print(f"[wallet] ⚠️ Could not verify transaction: {verify_error}")

                # Log transaction details if available
                if "signature" in result:
                    print(f"[wallet] 📋 Transaction signature: {result['signature']}")
                    result['solscan_url'] = f"https://solscan.io/tx/{result['signature']}"

                if "solscan_url" in result:
                    print(f"[wallet] 🔍 View on Solscan: {result['solscan_url']}")

                # Add wallet-specific metadata
                result.update({
                    "action": "buy",
                    "token_mint": mint,
                    "amount_sol": amount_sol,
                    "wallet_address": self.address,
                    "demo_mode": demo_mode,
                    "timestamp": time.time()
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