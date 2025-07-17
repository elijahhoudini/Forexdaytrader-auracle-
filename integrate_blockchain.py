#!/usr/bin/env python3
"""
AURACLE Blockchain Integration
============================

Integrates the blockchain folder implementation with AURACLE to fix transaction signing issues
and enable percentage-based trading.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AURACLEBlockchainIntegration:
    """Integration class for AURACLE and blockchain module."""
    
    def __init__(self):
        """Initialize the integration."""
        self.wallet_address = os.getenv("WALLET_ADDRESS", "")
        self.wallet_private_key = os.getenv("WALLET_PRIVATE_KEY", "")
        self.percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
        self.demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
        
        # Initialize blockchain components
        self.blockchain_integration = None
        self.wallet_manager = None
        self.transaction_manager = None
        self.jupiter_client = None
        
    async def initialize(self) -> bool:
        """Initialize blockchain components."""
        print("\n" + "=" * 60)
        print("🚀 AURACLE - Blockchain Integration")
        print("=" * 60)
        
        # Check wallet info
        if not self.wallet_address or not self.wallet_private_key:
            print("❌ Wallet address or private key not found in .env")
            return False
            
        masked_address = self.wallet_address[:8] + "..." + self.wallet_address[-8:] if len(self.wallet_address) > 16 else self.wallet_address
        print(f"✅ Using wallet: {masked_address}")
        
        # Show trading mode
        if self.demo_mode:
            print("🔷 DEMO MODE: No real money will be used")
        else:
            print("🔥 LIVE TRADING: Real money will be used")
            
        print(f"✅ Percentage-based trading: {self.percentage}% of balance per trade")
        
        try:
            # Import blockchain integration
            from main_blockchain_integration import BlockchainIntegration
            from blockchain.wallet_manager import WalletManager
            from blockchain.transaction_manager import TransactionManager
            from blockchain.jupiter_client import JupiterClient
            
            print("✅ Blockchain modules imported successfully")
            
            # Initialize blockchain integration
            self.blockchain_integration = BlockchainIntegration()
            
            # Load wallet from private key
            self.wallet_manager = WalletManager()
            self.wallet_manager.load_from_private_key(self.wallet_private_key)
            
            # Initialize transaction manager
            self.transaction_manager = TransactionManager(
                wallet_manager=self.wallet_manager
            )
            
            # Initialize Jupiter client
            self.jupiter_client = JupiterClient()
            
            print("✅ Blockchain components initialized")
            return True
            
        except ImportError as e:
            print(f"❌ Failed to import blockchain modules: {e}")
            return False
            
        except Exception as e:
            print(f"❌ Error initializing blockchain components: {e}")
            return False
    
    def patch_jupiter_api(self) -> bool:
        """Patch the AURACLE Jupiter API with blockchain implementation."""
        try:
            import jupiter_api
            
            # Store original methods to restore if needed
            self.original_execute_swap = jupiter_api.JupiterAPI.execute_swap
            
            # Define new execute_swap method
            async def new_execute_swap(self_api, input_mint: str, output_mint: str, amount: float, 
                                 wallet_keypair: Optional[Any] = None) -> Dict[str, Any]:
                """
                Execute a token swap with fixed transaction signing.
                
                Args:
                    input_mint: Input token mint address
                    output_mint: Output token mint address
                    amount: Amount of input token (in SOL for native SOL)
                    wallet_keypair: Wallet keypair for signing (None for demo mode)
                
                Returns:
                    Dict with success status and transaction details
                """
                print(f"[blockchain] 🔄 Executing swap: {amount} SOL of {input_mint} → {output_mint}")
                
                if self.demo_mode:
                    # In demo mode, just simulate the trade
                    print("[blockchain] 🔷 DEMO MODE: Simulating trade")
                    await asyncio.sleep(1)
                    return {
                        "success": True,
                        "signature": "SimulatedTransaction",
                        "input_amount": amount,
                        "output_amount": amount * 1.01
                    }
                
                try:
                    # Use Jupiter client from blockchain folder
                    async with self.jupiter_client:
                        # Get quote
                        quote = await self.jupiter_client.get_quote(
                            input_mint=input_mint,
                            output_mint=output_mint,
                            amount=int(amount * 1_000_000_000),  # Convert to lamports
                            slippage_bps=50  # 0.5% slippage
                        )
                        
                        # Get swap transaction
                        swap_tx_data = await self.jupiter_client.get_swap_transaction(
                            wallet_address=self.wallet_address,
                            swap_data=quote
                        )
                        
                        # Sign and send transaction using transaction manager
                        result = await self.transaction_manager.send_raw_transaction(
                            transaction_bytes=swap_tx_data["encoded_transaction"],
                            skip_preflight=True
                        )
                        
                        if "signature" in result:
                            print(f"[blockchain] ✅ Swap successful: {result['signature']}")
                            return {
                                "success": True,
                                "signature": result["signature"],
                                "input_amount": amount,
                                "output_amount": quote.get("outAmount", 0) / 1_000_000_000
                            }
                        else:
                            print(f"[blockchain] ❌ Swap failed: {result}")
                            return {
                                "success": False,
                                "error": str(result)
                            }
                
                except Exception as e:
                    print(f"[blockchain] ❌ Error executing swap: {e}")
                    return {"success": False, "error": str(e)}
            
            # Replace the method
            jupiter_api.JupiterAPI.execute_swap = new_execute_swap
            print("✅ Jupiter API patched with blockchain implementation")
            return True
        
        except Exception as e:
            print(f"❌ Failed to patch Jupiter API: {e}")
            return False
    
    def restore_jupiter_api(self) -> bool:
        """Restore the original Jupiter API methods."""
        try:
            if hasattr(self, 'original_execute_swap'):
                import jupiter_api
                jupiter_api.JupiterAPI.execute_swap = self.original_execute_swap
                print("✅ Jupiter API restored to original implementation")
            return True
        except Exception as e:
            print(f"❌ Failed to restore Jupiter API: {e}")
            return False
    
    async def calculate_trade_amount(self) -> float:
        """Calculate trade amount based on percentage of balance."""
        try:
            # Get wallet balance using blockchain RPC manager
            balance_lamports = await self.blockchain_integration.rpc_manager.get_balance(self.wallet_address)
            balance_sol = balance_lamports / 1_000_000_000
            
            # Calculate percentage
            trade_amount = balance_sol * (self.percentage / 100.0)
            
            # Apply safety limits
            min_amount = 0.01  # Minimum 0.01 SOL
            max_amount = balance_sol * 0.5  # Never use more than 50% as safety measure
            
            trade_amount = max(min_amount, min(trade_amount, max_amount))
            
            print(f"💰 Wallet balance: {balance_sol:.4f} SOL")
            print(f"💰 Trade amount: {trade_amount:.4f} SOL ({self.percentage}% of balance)")
            
            # Set this in environment for AURACLE to use
            os.environ["MAX_BUY_AMOUNT_SOL"] = str(trade_amount)
            
            return trade_amount
        except Exception as e:
            print(f"❌ Error calculating trade amount: {e}")
            return float(os.getenv("MAX_BUY_AMOUNT_SOL", "0.05"))
    
    async def run_auracle(self):
        """Run AURACLE with blockchain integration."""
        try:
            # Calculate trade amount first
            await self.calculate_trade_amount()
            
            # Patch the Jupiter API
            self.patch_jupiter_api()
            
            # Import and run AURACLE
            print("\n🚀 Starting AURACLE with blockchain integration...")
            
            # Try different methods to start AURACLE
            if os.path.exists("auracle.py"):
                print("✅ Running auracle.py...")
                os.system(f"python3 auracle.py")
            elif os.path.exists("start.py"):
                print("✅ Running start.py...")
                os.system(f"python3 start.py")
            else:
                print("❌ No AURACLE startup script found")
        
        except Exception as e:
            print(f"❌ Error starting AURACLE: {e}")
        finally:
            # Restore original methods
            self.restore_jupiter_api()

async def main():
    """Main entry point for AURACLE blockchain integration."""
    integration = AURACLEBlockchainIntegration()
    
    # Initialize integration
    if not await integration.initialize():
        print("❌ Failed to initialize blockchain integration")
        return
        
    try:
        # Run AURACLE with blockchain integration
        await integration.run_auracle()
    except KeyboardInterrupt:
        print("\n👋 Trading stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Program stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        
    print("\n✅ AURACLE blockchain integration session complete")
