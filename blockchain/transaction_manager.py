"""
Transaction Manager Module
==========================

Provides comprehensive transaction management for Solana blockchain
operations including transaction building, signing, sending, and monitoring.
"""

import asyncio
import base64
from typing import Dict, List, Optional, Any, Union
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.instruction import Instruction
from solana.keypair import Keypair
from .blockchain_config import config
from .blockchain_logger import logger
from .rpc_manager import RPCManager
from .wallet_manager import WalletManager
from .priority_fee_calculator import PriorityFeeCalculator
from .retry_decorator import retry_transaction


class TransactionManager:
    """Manager for Solana transaction operations."""
    
    def __init__(self,
                 rpc_manager: Optional[RPCManager] = None,
                 wallet_manager: Optional[WalletManager] = None,
                 priority_fee_calculator: Optional[PriorityFeeCalculator] = None):
        """
        Initialize transaction manager.
        
        Args:
            rpc_manager: RPC manager instance
            wallet_manager: Wallet manager instance
            priority_fee_calculator: Priority fee calculator instance
        """
        self.rpc_manager = rpc_manager or RPCManager()
        self.wallet_manager = wallet_manager or WalletManager()
        self.priority_fee_calculator = priority_fee_calculator or PriorityFeeCalculator()
        
        self._pending_transactions: Dict[str, Dict[str, Any]] = {}
    
    async def build_transaction(self,
                              instructions: List[Instruction],
                              payer: Optional[PublicKey] = None,
                              recent_blockhash: Optional[str] = None) -> Transaction:
        """
        Build a transaction from instructions.
        
        Args:
            instructions: List of instructions
            payer: Transaction payer (uses wallet if not provided)
            recent_blockhash: Recent blockhash (fetched if not provided)
            
        Returns:
            Built transaction
        """
        logger.debug("Building transaction", {
            'instruction_count': len(instructions),
            'payer': str(payer) if payer else None
        })
        
        try:
            # Use wallet public key as payer if not provided
            if not payer:
                if not self.wallet_manager.public_key:
                    raise ValueError("No payer provided and no wallet loaded")
                payer = self.wallet_manager.public_key
            
            # Get recent blockhash if not provided
            if not recent_blockhash:
                recent_blockhash = await self.rpc_manager.get_recent_blockhash()
            
            # Build transaction
            transaction = Transaction()
            transaction.fee_payer = payer
            transaction.recent_blockhash = recent_blockhash
            
            # Add instructions
            for instruction in instructions:
                transaction.add(instruction)
            
            logger.info("Transaction built successfully", {
                'instruction_count': len(instructions),
                'payer': str(payer),
                'recent_blockhash': recent_blockhash
            })
            
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to build transaction: {str(e)}", {
                'instruction_count': len(instructions),
                'error': str(e)
            })
            raise
    
    async def sign_transaction(self,
                             transaction: Transaction,
                             signers: Optional[List[Keypair]] = None) -> Transaction:
        """
        Sign a transaction.
        
        Args:
            transaction: Transaction to sign
            signers: List of signers (uses wallet if not provided)
            
        Returns:
            Signed transaction
        """
        logger.debug("Signing transaction")
        
        try:
            # Use wallet keypair as signer if not provided
            if not signers:
                if not self.wallet_manager.keypair:
                    raise ValueError("No signers provided and no wallet loaded")
                signers = [self.wallet_manager.keypair]
            
            # Sign transaction
            transaction.sign(*signers)
            
            logger.info("Transaction signed successfully", {
                'signer_count': len(signers),
                'signature_count': len(transaction.signatures)
            })
            
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to sign transaction: {str(e)}")
            raise
    
    @retry_transaction(max_retries=3)
    async def send_transaction(self,
                             transaction: Transaction,
                             skip_preflight: bool = False,
                             max_retries: int = 3) -> str:
        """
        Send a transaction to the network.
        
        Args:
            transaction: Signed transaction
            skip_preflight: Whether to skip preflight checks
            max_retries: Maximum number of retries
            
        Returns:
            Transaction signature
        """
        logger.debug("Sending transaction", {
            'skip_preflight': skip_preflight,
            'max_retries': max_retries
        })
        
        try:
            # Serialize transaction
            serialized_tx = transaction.serialize()
            
            # Send transaction
            signature = await self.rpc_manager.send_transaction(
                serialized_tx,
                skip_preflight=skip_preflight,
                max_retries=max_retries
            )
            
            # Track transaction
            self._pending_transactions[signature] = {
                'signature': signature,
                'transaction': transaction,
                'timestamp': asyncio.get_event_loop().time(),
                'status': 'sent'
            }
            
            logger.info("Transaction sent successfully", {
                'signature': signature,
                'skip_preflight': skip_preflight
            })
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {str(e)}")
            raise
    
    async def confirm_transaction(self,
                                signature: str,
                                timeout: int = 60) -> bool:
        """
        Confirm a transaction.
        
        Args:
            signature: Transaction signature
            timeout: Confirmation timeout in seconds
            
        Returns:
            True if confirmed, False otherwise
        """
        logger.debug(f"Confirming transaction: {signature}")
        
        try:
            # Confirm transaction
            is_confirmed = await self.rpc_manager.confirm_transaction(signature, timeout)
            
            # Update transaction status
            if signature in self._pending_transactions:
                self._pending_transactions[signature]['status'] = 'confirmed' if is_confirmed else 'failed'
            
            logger.info("Transaction confirmation result", {
                'signature': signature,
                'confirmed': is_confirmed
            })
            
            return is_confirmed
            
        except Exception as e:
            logger.error(f"Failed to confirm transaction: {str(e)}", {
                'signature': signature,
                'error': str(e)
            })
            
            # Update transaction status
            if signature in self._pending_transactions:
                self._pending_transactions[signature]['status'] = 'error'
            
            raise
    
    async def send_and_confirm_transaction(self,
                                         transaction: Transaction,
                                         skip_preflight: bool = False,
                                         confirmation_timeout: int = 60) -> str:
        """
        Send and confirm a transaction.
        
        Args:
            transaction: Signed transaction
            skip_preflight: Whether to skip preflight checks
            confirmation_timeout: Confirmation timeout in seconds
            
        Returns:
            Transaction signature
        """
        logger.debug("Sending and confirming transaction")
        
        try:
            # Send transaction
            signature = await self.send_transaction(transaction, skip_preflight)
            
            # Confirm transaction
            is_confirmed = await self.confirm_transaction(signature, confirmation_timeout)
            
            if not is_confirmed:
                raise RuntimeError(f"Transaction confirmation failed: {signature}")
            
            logger.info("Transaction sent and confirmed successfully", {
                'signature': signature
            })
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to send and confirm transaction: {str(e)}")
            raise
    
    async def build_and_send_transaction(self,
                                       instructions: List[Instruction],
                                       payer: Optional[PublicKey] = None,
                                       signers: Optional[List[Keypair]] = None,
                                       priority_fee: Optional[int] = None,
                                       confirm: bool = True) -> str:
        """
        Build, sign, and send a transaction.
        
        Args:
            instructions: List of instructions
            payer: Transaction payer
            signers: List of signers
            priority_fee: Priority fee in micro-lamports
            confirm: Whether to confirm the transaction
            
        Returns:
            Transaction signature
        """
        logger.debug("Building and sending transaction", {
            'instruction_count': len(instructions),
            'priority_fee': priority_fee,
            'confirm': confirm
        })
        
        try:
            # Add priority fee instruction if specified
            if priority_fee:
                from solana.instruction import Instruction
                # Add compute budget instruction for priority fee
                # This is a simplified version - in practice, you'd use the actual instruction
                priority_instruction = Instruction(
                    program_id=PublicKey("ComputeBudget111111111111111111111111111111"),
                    accounts=[],
                    data=bytes([2])  # SetComputeUnitPrice instruction
                )
                instructions.insert(0, priority_instruction)
            
            # Build transaction
            transaction = await self.build_transaction(instructions, payer)
            
            # Sign transaction
            transaction = await self.sign_transaction(transaction, signers)
            
            # Send transaction
            if confirm:
                signature = await self.send_and_confirm_transaction(transaction)
            else:
                signature = await self.send_transaction(transaction)
            
            logger.info("Transaction built and sent successfully", {
                'signature': signature,
                'instruction_count': len(instructions)
            })
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to build and send transaction: {str(e)}", {
                'instruction_count': len(instructions),
                'error': str(e)
            })
            raise
    
    async def create_jupiter_swap_transaction(self,
                                            swap_data: Dict[str, Any],
                                            priority_fee: Optional[int] = None) -> str:
        """
        Create and send a Jupiter swap transaction.
        
        Args:
            swap_data: Swap transaction data from Jupiter API
            priority_fee: Priority fee in micro-lamports
            
        Returns:
            Transaction signature
        """
        logger.debug("Creating Jupiter swap transaction", {
            'priority_fee': priority_fee
        })
        
        try:
            # Get transaction from swap data
            swap_transaction = swap_data.get('swapTransaction')
            if not swap_transaction:
                raise ValueError("No swap transaction in swap data")
            
            # Decode transaction
            tx_bytes = base64.b64decode(swap_transaction)
            transaction = Transaction.deserialize(tx_bytes)
            
            # Add priority fee if specified
            if priority_fee:
                # Calculate priority fee
                calculated_fee = await self.priority_fee_calculator.calculate_priority_fee(
                    urgency="medium"
                )
                final_fee = priority_fee or calculated_fee
                
                logger.debug("Adding priority fee to Jupiter swap", {
                    'priority_fee': final_fee
                })
            
            # Sign transaction
            transaction = await self.sign_transaction(transaction)
            
            # Send and confirm transaction
            signature = await self.send_and_confirm_transaction(transaction)
            
            logger.info("Jupiter swap transaction completed successfully", {
                'signature': signature
            })
            
            return signature
            
        except Exception as e:
            logger.error(f"Failed to create Jupiter swap transaction: {str(e)}")
            raise
    
    def get_pending_transactions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get pending transactions.
        
        Returns:
            Dictionary of pending transactions
        """
        return self._pending_transactions.copy()
    
    def clear_completed_transactions(self, max_age: int = 3600):
        """
        Clear completed transactions older than max_age.
        
        Args:
            max_age: Maximum age in seconds
        """
        current_time = asyncio.get_event_loop().time()
        
        to_remove = []
        for signature, tx_data in self._pending_transactions.items():
            if (current_time - tx_data['timestamp']) > max_age:
                if tx_data['status'] in ['confirmed', 'failed', 'error']:
                    to_remove.append(signature)
        
        for signature in to_remove:
            del self._pending_transactions[signature]
        
        if to_remove:
            logger.debug(f"Cleared {len(to_remove)} completed transactions")


# Global transaction manager instance
transaction_manager = TransactionManager()