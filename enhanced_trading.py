"""
Enhanced Trading Module for AURACLE
==================================

This module provides enhanced trading features including:
1. Percentage-based trading (uses a percentage of wallet balance)
2. Fixed duplicate method issues
3. Better error handling
"""

import os
import sys
import time
import random
import logging
import asyncio
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import config
try:
    import config
except ImportError:
    logger.error("Could not import config module")
    sys.exit(1)

class EnhancedTradeHandler:
    """Enhanced trade handler with percentage-based trading support."""
    
    def __init__(self, wallet, auracle_instance=None):
        """Initialize the enhanced trade handler."""
        self.wallet = wallet
        self.auracle_instance = auracle_instance
        logger.info("Enhanced trade handler initialized")
        print("✅ Enhanced trading features enabled")
        
        # Get trading configuration
        self.use_percentage = os.getenv("USE_PERCENTAGE_OF_BALANCE", "false").lower() == "true"
        self.percentage = float(os.getenv("MAX_BUY_PERCENTAGE", "10"))
        
        if self.use_percentage:
            print(f"✅ Percentage-based trading enabled: {self.percentage}% of balance per trade")
        else:
            print("📊 Using fixed amount per trade")

    async def get_wallet_balance(self):
        """Get the current wallet balance in SOL."""
        try:
            if hasattr(self.wallet, 'get_balance'):
                # Try async method first
                try:
                    return await self.wallet.get_balance("SOL")
                except:
                    pass
                    
            # Fallback to direct RPC call
            wallet_address = os.getenv("WALLET_ADDRESS")
            if not wallet_address:
                logger.error("No wallet address found")
                return 0.0
                
            rpc_url = os.getenv("SOLANA_RPC_ENDPOINT", "https://api.mainnet-beta.solana.com")
            
            # Prepare RPC request
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [wallet_address]
            }
            
            # Send request
            response = requests.post(rpc_url, json=payload)
            data = response.json()
            
            if "result" in data and "value" in data["result"]:
                # Convert lamports to SOL
                balance_sol = data["result"]["value"] / 1_000_000_000
                logger.info(f"Wallet balance: {balance_sol:.4f} SOL")
                return balance_sol
            else:
                logger.error(f"Failed to get wallet balance: {data}")
                return 0.0
        except Exception as e:
            logger.error(f"Error getting wallet balance: {e}")
            return 0.0

    async def calculate_trade_amount(self, token: Dict[str, Any]) -> float:
        """
        Calculate the trade amount based on percentage of wallet balance.
        
        Args:
            token: The token data
            
        Returns:
            The amount in SOL to use for the trade
        """
        if self.use_percentage:
            # Get current wallet balance
            balance = await self.get_wallet_balance()
            
            if balance <= 0:
                logger.warning("Zero or negative balance - using minimum amount")
                return 0.01  # Minimum amount
            
            # Calculate trade amount as percentage of balance
            trade_amount = balance * (self.percentage / 100.0)
            
            # Apply minimum and maximum limits for safety
            min_amount = 0.01  # Minimum 0.01 SOL
            max_amount = balance * 0.5  # Never use more than 50% of balance as safety measure
            
            trade_amount = max(min_amount, min(trade_amount, max_amount))
            
            logger.info(f"Using {self.percentage}% of wallet balance ({balance:.4f} SOL): {trade_amount:.4f} SOL")
            print(f"💰 Trade amount: {trade_amount:.4f} SOL ({self.percentage}% of {balance:.4f} SOL)")
            return trade_amount
        else:
            # Fall back to fixed amount from config
            amount = getattr(config, 'MAX_BUY_AMOUNT_SOL', 0.05)
            logger.info(f"Using fixed amount: {amount} SOL")
            return amount

    async def buy_token(self, token: Dict[str, Any], amount_sol: Optional[float] = None) -> bool:
        """
        Execute buy order for token using Jupiter.
        
        Args:
            token: Token data
            amount_sol: Optional override for SOL amount to use
            
        Returns:
            True if successful
        """
        try:
            mint = token.get("mint", "")
            if not mint:
                logger.error("No mint address provided for token")
                return False
                
            # Calculate trade amount if not provided
            if amount_sol is None:
                amount_sol = await self.calculate_trade_amount(token)
                
            # Check minimum amount
            if amount_sol < 0.01:
                logger.warning(f"Trade amount too small: {amount_sol} SOL. Using minimum 0.01 SOL")
                amount_sol = 0.01
                
            # Check wallet balance
            balance = await self.get_wallet_balance()
            if balance < amount_sol:
                logger.warning(f"Insufficient balance: {balance} SOL, needed {amount_sol} SOL")
                print(f"⚠️ Insufficient balance: {balance:.4f} SOL, needed {amount_sol:.4f} SOL")
                return False
                
            # Execute trade through wallet or delegate
            if hasattr(self.wallet, 'buy_token'):
                logger.info(f"Executing buy for {token.get('symbol', mint)}, amount: {amount_sol} SOL")
                print(f"🔄 Buying {token.get('symbol', mint)} for {amount_sol:.4f} SOL")
                
                # Call original wallet buy method
                success = await self.wallet.buy_token(mint, amount_sol)
                
                if success:
                    print(f"✅ Buy successful: {token.get('symbol', mint)} for {amount_sol:.4f} SOL")
                    logger.info(f"Buy successful: {token.get('symbol', mint)} for {amount_sol} SOL")
                else:
                    print(f"❌ Buy failed: {token.get('symbol', mint)}")
                    logger.error(f"Buy failed: {token.get('symbol', mint)}")
                
                return success
            else:
                logger.error("Wallet doesn't support buy_token method")
                return False
                
        except Exception as e:
            logger.error(f"Error buying token: {e}")
            print(f"❌ Error buying token: {e}")
            return False

    async def sell_token(self, mint: str, reason: str = "manual") -> bool:
        """
        Sell token using Jupiter.
        
        Args:
            mint: Token mint address
            reason: Reason for selling
            
        Returns:
            True if successful
        """
        try:
            if not mint:
                logger.error("No mint address provided")
                return False
                
            # Execute sell through wallet or delegate
            if hasattr(self.wallet, 'sell_token'):
                logger.info(f"Executing sell for {mint}, reason: {reason}")
                print(f"🔄 Selling token {mint} (Reason: {reason})")
                
                # Call original wallet sell method
                success = await self.wallet.sell_token(mint)
                
                if success:
                    print(f"✅ Sell successful: {mint}")
                    logger.info(f"Sell successful: {mint}")
                else:
                    print(f"❌ Sell failed: {mint}")
                    logger.error(f"Sell failed: {mint}")
                
                return success
            else:
                logger.error("Wallet doesn't support sell_token method")
                return False
                
        except Exception as e:
            logger.error(f"Error selling token: {e}")
            print(f"❌ Error selling token: {e}")
            return False
