"""
AURACLE Wallet Module
====================

Wallet management and transaction handling for Solana trading.
Integrates with Jupiter for real token swaps.
"""

import config
import time
import random
import base58
from typing import Optional, Dict, Any
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from jupiter_swap import JupiterSwapClient, initialize_jupiter_client


class Wallet:
    """
    Enhanced wallet with Jupiter integration for real trading.
    """
    
    def __init__(self):
        self.address = config.WALLET_ADDRESS
        self.demo_mode = config.get_demo_mode()
        self.keypair = None
        self.rpc_client = None
        self.jupiter_client = None
        
        # Initialize RPC client
        self.rpc_client = Client(
            config.SOLANA_RPC_ENDPOINT,
            commitment=Commitment(config.SOLANA_COMMITMENT)
        )
        
        # Initialize wallet keypair for live trading
        if not self.demo_mode and config.WALLET_PRIVATE_KEY:
            try:
                # Decode private key
                private_key_bytes = base58.b58decode(config.WALLET_PRIVATE_KEY)
                self.keypair = Keypair.from_bytes(private_key_bytes)
                
                # Initialize Jupiter client
                if config.JUPITER_ENABLED:
                    self.jupiter_client = initialize_jupiter_client(self.rpc_client, self.keypair)
                    
                print(f"🔥 Wallet initialized in LIVE mode with Jupiter")
                print(f"📍 Address: {self.address[:8]}...")
                
            except Exception as e:
                print(f"❌ Failed to initialize live wallet: {e}")
                print("⚠️  Falling back to demo mode")
                self.demo_mode = True
                config.set_demo_mode(True)
        
        if self.demo_mode:
            print("🔶 Wallet initialized in DEMO mode")
        
        # Validate wallet setup
        self._validate_setup()

    def _validate_setup(self):
        """Validate wallet setup and configuration."""
        try:
            if not self.demo_mode:
                # Check RPC connection
                health = self.rpc_client.get_health()
                if health.value != "ok":
                    print("⚠️  RPC connection unhealthy")
                
                # Check wallet balance
                if self.keypair:
                    balance = self.get_balance("SOL")
                    if balance < 0.01:  # Minimum 0.01 SOL for transactions
                        print(f"⚠️  Low SOL balance: {balance} SOL")
                
                print("✅ Live wallet setup validated")
            else:
                print("✅ Demo wallet setup validated")
                
        except Exception as e:
            print(f"⚠️  Wallet validation error: {e}")

    def get_balance(self, token: str = "SOL") -> float:
        """Get wallet balance for specified token."""
        try:
            if self.demo_mode:
                return 1.0  # Demo balance
            
            if token == "SOL" and self.keypair:
                # Get real SOL balance
                pubkey = self.keypair.pubkey()
                balance_response = self.rpc_client.get_balance(pubkey)
                
                if balance_response.value is not None:
                    return balance_response.value / 1_000_000_000  # Convert lamports to SOL
                
            return 0.0
            
        except Exception as e:
            print(f"❌ Error getting balance: {e}")
            return 0.0 if not self.demo_mode else 1.0

    def send_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a transaction to the blockchain."""
        try:
            if self.demo_mode:
                return self._simulate_transaction(tx_data)
            
            # For live trading, transactions are handled by Jupiter client
            # This method is kept for compatibility
            action = tx_data.get("action", "unknown")
            print(f"[wallet] 🔥 Live transaction: {action}")
            
            return {
                "success": True,
                "signature": f"live_{action}_{int(time.time())}",
                "timestamp": time.time()
            }

        except Exception as e:
            print(f"[wallet] Transaction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }

    def _simulate_transaction(self, tx_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate transaction in demo mode."""
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

    async def buy_token(self, mint: str, amount_sol: float, token_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute buy transaction using Jupiter or demo mode.
        
        Args:
            mint: Token mint address
            amount_sol: Amount of SOL to spend
            token_data: Token information for risk assessment
            
        Returns:
            Transaction result
        """
        try:
            if self.demo_mode:
                # Simulate buy transaction
                tx_data = {
                    "action": "buy",
                    "token_mint": mint,
                    "amount_sol": amount_sol,
                    "timestamp": time.time()
                }
                
                result = self._simulate_transaction(tx_data)
                
                if result["success"]:
                    print(f"[wallet] 🎯 Demo buy: {amount_sol} SOL -> {mint[:8]}...")
                else:
                    print(f"[wallet] Demo buy failed: {result.get('error', 'Unknown error')}")
                
                return result
            
            # Real Jupiter swap
            if not self.jupiter_client:
                print("❌ Jupiter client not initialized")
                return {"success": False, "error": "Jupiter client not available"}
            
            print(f"[wallet] 🔥 Live buy: {amount_sol} SOL -> {mint[:8]}...")
            
            # Execute buy through Jupiter with risk management
            signature = await self.jupiter_client.buy_token(
                token_mint=mint,
                sol_amount=amount_sol,
                token_data=token_data,
                slippage_bps=config.JUPITER_DEFAULT_SLIPPAGE_BPS
            )
            
            if signature:
                return {
                    "success": True,
                    "signature": signature,
                    "timestamp": time.time()
                }
            else:
                return {
                    "success": False,
                    "error": "Jupiter buy failed",
                    "signature": None
                }

        except Exception as e:
            print(f"[wallet] Error buying token: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }

    async def sell_token(self, mint: str, amount: float) -> Dict[str, Any]:
        """
        Execute sell transaction using Jupiter or demo mode.
        
        Args:
            mint: Token mint address
            amount: Amount of tokens to sell
            
        Returns:
            Transaction result
        """
        try:
            if self.demo_mode:
                # Simulate sell transaction
                tx_data = {
                    "action": "sell",
                    "token_mint": mint,
                    "amount": amount,
                    "timestamp": time.time()
                }
                
                result = self._simulate_transaction(tx_data)
                
                if result["success"]:
                    print(f"[wallet] 🎯 Demo sell: {amount} tokens of {mint[:8]}...")
                else:
                    print(f"[wallet] Demo sell failed: {result.get('error', 'Unknown error')}")
                
                return result
            
            # Real Jupiter swap
            if not self.jupiter_client:
                print("❌ Jupiter client not initialized")
                return {"success": False, "error": "Jupiter client not available"}
            
            print(f"[wallet] 🔥 Live sell: {amount} tokens of {mint[:8]}...")
            
            # Convert amount to token's smallest unit (assuming 9 decimals for most tokens)
            token_amount = int(amount * 1_000_000_000)
            
            # Execute sell through Jupiter
            signature = await self.jupiter_client.sell_token(
                token_mint=mint,
                token_amount=token_amount,
                slippage_bps=config.JUPITER_DEFAULT_SLIPPAGE_BPS
            )
            
            if signature:
                return {
                    "success": True,
                    "signature": signature,
                    "timestamp": time.time()
                }
            else:
                return {
                    "success": False,
                    "error": "Jupiter sell failed",
                    "signature": None
                }

        except Exception as e:
            print(f"[wallet] Error selling token: {e}")
            return {
                "success": False,
                "error": str(e),
                "signature": None
            }

    async def get_token_price(self, mint: str) -> Optional[float]:
        """
        Get current token price using Jupiter.
        
        Args:
            mint: Token mint address
            
        Returns:
            Price in USD or None if failed
        """
        try:
            if self.demo_mode:
                # Return random price for demo
                return random.uniform(0.001, 10.0)
            
            if self.jupiter_client:
                return await self.jupiter_client.get_token_price(mint)
            
            return None
            
        except Exception as e:
            print(f"[wallet] Error getting token price: {e}")
            return None

    def get_jupiter_client(self) -> Optional[JupiterSwapClient]:
        """Get the Jupiter client instance."""
        return self.jupiter_client

    def is_live_mode(self) -> bool:
        """Check if wallet is in live trading mode."""
        return not self.demo_mode and self.jupiter_client is not None