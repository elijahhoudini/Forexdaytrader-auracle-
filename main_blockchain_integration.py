"""
Main Blockchain Integration Module
==================================

Main entry point for blockchain integration functionality.
Provides a unified interface for all blockchain operations.
"""

import asyncio
import sys
from typing import Dict, List, Optional, Any
from blockchain import (
    BlockchainConfig,
    BlockchainLogger,
    JupiterClient,
    RPCManager,
    WalletManager,
    TransactionManager,
    PriorityFeeCalculator,
    SolscanClient,
    config,
    logger
)


class BlockchainIntegration:
    """Main blockchain integration class."""
    
    def __init__(self):
        """Initialize blockchain integration."""
        self.config = config
        self.logger = logger
        
        # Initialize managers
        self.rpc_manager = RPCManager()
        self.wallet_manager = WalletManager()
        self.priority_fee_calculator = PriorityFeeCalculator(self.rpc_manager)
        self.transaction_manager = TransactionManager(
            self.rpc_manager,
            self.wallet_manager,
            self.priority_fee_calculator
        )
        
        # Initialize clients
        self.jupiter_client = JupiterClient()
        self.solscan_client = SolscanClient()
        
        self.logger.info("Blockchain integration initialized")
    
    async def initialize(self, wallet_path: Optional[str] = None) -> bool:
        """
        Initialize the blockchain integration.
        
        Args:
            wallet_path: Path to wallet file
            
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("Initializing blockchain integration")
            
            # Load wallet if path provided
            if wallet_path:
                if not self.wallet_manager.load_wallet(wallet_path):
                    self.logger.error("Failed to load wallet")
                    return False
            
            # Connect to RPC
            await self.rpc_manager.connect()
            
            # Test connection
            await self.rpc_manager.get_recent_blockhash()
            
            self.logger.info("Blockchain integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize blockchain integration: {str(e)}")
            return False
    
    async def close(self):
        """Close all connections."""
        try:
            await self.rpc_manager.close()
            self.logger.info("Blockchain integration closed")
        except Exception as e:
            self.logger.error(f"Error closing blockchain integration: {str(e)}")
    
    async def get_wallet_balance(self) -> Optional[float]:
        """
        Get wallet balance in SOL.
        
        Returns:
            Balance in SOL or None if failed
        """
        try:
            if not self.wallet_manager.public_key:
                self.logger.error("No wallet loaded")
                return None
            
            balance_lamports = await self.rpc_manager.get_balance(
                str(self.wallet_manager.public_key)
            )
            
            balance_sol = balance_lamports / 1e9
            
            self.logger.info(f"Wallet balance: {balance_sol} SOL")
            return balance_sol
            
        except Exception as e:
            self.logger.error(f"Failed to get wallet balance: {str(e)}")
            return None
    
    async def perform_jupiter_swap(self,
                                 input_mint: str,
                                 output_mint: str,
                                 amount: int,
                                 slippage_bps: int = 50) -> Optional[str]:
        """
        Perform a Jupiter swap.
        
        Args:
            input_mint: Input token mint
            output_mint: Output token mint
            amount: Amount to swap
            slippage_bps: Slippage in basis points
            
        Returns:
            Transaction signature or None if failed
        """
        try:
            self.logger.info("Performing Jupiter swap", {
                'input_mint': input_mint,
                'output_mint': output_mint,
                'amount': amount,
                'slippage_bps': slippage_bps
            })
            
            if not self.wallet_manager.public_key:
                self.logger.error("No wallet loaded for swap")
                return None
            
            # Get quote
            async with self.jupiter_client as client:
                quote = await client.get_quote(
                    input_mint=input_mint,
                    output_mint=output_mint,
                    amount=amount,
                    slippage_bps=slippage_bps
                )
                
                # Get swap transaction
                swap_data = await client.get_swap_transaction(
                    quote=quote,
                    user_public_key=str(self.wallet_manager.public_key)
                )
            
            # Execute swap
            signature = await self.transaction_manager.create_jupiter_swap_transaction(
                swap_data=swap_data
            )
            
            self.logger.info("Jupiter swap completed successfully", {
                'signature': signature
            })
            
            return signature
            
        except Exception as e:
            self.logger.error(f"Failed to perform Jupiter swap: {str(e)}")
            return None
    
    async def get_token_info(self, token_address: str) -> Optional[Dict[str, Any]]:
        """
        Get token information.
        
        Args:
            token_address: Token mint address
            
        Returns:
            Token information or None if failed
        """
        try:
            async with self.solscan_client as client:
                token_info = await client.get_token_info(token_address)
                
                self.logger.info("Token info retrieved successfully", {
                    'token_address': token_address,
                    'symbol': token_info.get('data', {}).get('symbol')
                })
                
                return token_info
                
        except Exception as e:
            self.logger.error(f"Failed to get token info: {str(e)}")
            return None
    
    async def get_account_info(self, account: str) -> Optional[Dict[str, Any]]:
        """
        Get account information.
        
        Args:
            account: Account public key
            
        Returns:
            Account information or None if failed
        """
        try:
            account_info = await self.rpc_manager.get_account_info(account)
            
            self.logger.info("Account info retrieved successfully", {
                'account': account
            })
            
            return account_info
            
        except Exception as e:
            self.logger.error(f"Failed to get account info: {str(e)}")
            return None
    
    async def calculate_priority_fee(self,
                                   urgency: str = "medium") -> Optional[int]:
        """
        Calculate priority fee for transactions.
        
        Args:
            urgency: Fee urgency level
            
        Returns:
            Priority fee in micro-lamports or None if failed
        """
        try:
            fee = await self.priority_fee_calculator.calculate_priority_fee(
                urgency=urgency
            )
            
            self.logger.info("Priority fee calculated", {
                'urgency': urgency,
                'fee': fee
            })
            
            return fee
            
        except Exception as e:
            self.logger.error(f"Failed to calculate priority fee: {str(e)}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get integration status.
        
        Returns:
            Status information
        """
        return {
            'rpc_connected': self.rpc_manager.client is not None,
            'wallet_loaded': self.wallet_manager.keypair is not None,
            'wallet_address': self.wallet_manager.public_key_str,
            'rpc_endpoint': self.rpc_manager.rpc_endpoint,
            'pending_transactions': len(self.transaction_manager.get_pending_transactions()),
            'config': self.config.to_dict()
        }


async def main():
    """Main function for testing blockchain integration."""
    print("🚀 Starting Blockchain Integration Test")
    
    # Initialize blockchain integration
    blockchain = BlockchainIntegration()
    
    try:
        # Initialize with wallet (if available)
        wallet_path = input("Enter wallet path (or press Enter to skip): ").strip()
        if not wallet_path:
            wallet_path = None
        
        success = await blockchain.initialize(wallet_path)
        if not success:
            print("❌ Failed to initialize blockchain integration")
            return
        
        print("✅ Blockchain integration initialized successfully")
        
        # Show status
        status = blockchain.get_status()
        print("\n📊 Status:")
        for key, value in status.items():
            if key != 'config':
                print(f"   {key}: {value}")
        
        # Get wallet balance if wallet is loaded
        if status['wallet_loaded']:
            balance = await blockchain.get_wallet_balance()
            if balance is not None:
                print(f"💰 Wallet balance: {balance} SOL")
        
        # Test token info
        print("\n🔍 Testing token info...")
        token_info = await blockchain.get_token_info(
            "So11111111111111111111111111111111111111112"  # SOL mint
        )
        if token_info:
            print("✅ Token info retrieved successfully")
        
        # Test priority fee calculation
        print("\n💸 Testing priority fee calculation...")
        fee = await blockchain.calculate_priority_fee("medium")
        if fee:
            print(f"✅ Priority fee calculated: {fee} micro-lamports")
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        await blockchain.close()


if __name__ == "__main__":
    asyncio.run(main())