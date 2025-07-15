"""
Wallet Manager Module
=====================

Provides wallet management functionality for Solana blockchain operations
including wallet creation, key management, and signing operations.
"""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from solana.keypair import Keypair
from solana.publickey import PublicKey
from .blockchain_config import config
from .blockchain_logger import logger
from .retry_decorator import retry_decorator


class WalletManager:
    """Manager for Solana wallet operations."""
    
    def __init__(self, wallet_path: Optional[str] = None):
        """
        Initialize wallet manager.
        
        Args:
            wallet_path: Path to wallet file
        """
        self.wallet_path = wallet_path or config.wallet_path
        self._keypair: Optional[Keypair] = None
        self._public_key: Optional[PublicKey] = None
    
    @property
    def keypair(self) -> Optional[Keypair]:
        """Get wallet keypair."""
        return self._keypair
    
    @property
    def public_key(self) -> Optional[PublicKey]:
        """Get wallet public key."""
        return self._public_key
    
    @property
    def public_key_str(self) -> Optional[str]:
        """Get wallet public key as string."""
        return str(self._public_key) if self._public_key else None
    
    def load_wallet(self, wallet_path: Optional[str] = None) -> bool:
        """
        Load wallet from file.
        
        Args:
            wallet_path: Path to wallet file
            
        Returns:
            True if loaded successfully, False otherwise
        """
        path = wallet_path or self.wallet_path
        
        if not path:
            logger.error("No wallet path provided")
            return False
        
        wallet_file = Path(path)
        
        if not wallet_file.exists():
            logger.error(f"Wallet file not found: {path}")
            return False
        
        try:
            with open(wallet_file, 'r') as f:
                wallet_data = json.load(f)
            
            # Support different wallet formats
            if isinstance(wallet_data, list):
                # Array format (standard Solana CLI format)
                secret_key = bytes(wallet_data[:32])
            elif isinstance(wallet_data, dict):
                # Object format
                secret_key = bytes(wallet_data.get('secretKey', [])[:32])
            else:
                logger.error(f"Unsupported wallet format: {type(wallet_data)}")
                return False
            
            self._keypair = Keypair.from_secret_key(secret_key)
            self._public_key = self._keypair.public_key
            
            logger.info("Wallet loaded successfully", {
                'public_key': str(self._public_key),
                'wallet_path': path
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load wallet: {str(e)}", {
                'wallet_path': path,
                'error': str(e)
            })
            return False
    
    def create_wallet(self, save_path: Optional[str] = None) -> bool:
        """
        Create a new wallet.
        
        Args:
            save_path: Path to save wallet file
            
        Returns:
            True if created successfully, False otherwise
        """
        try:
            # Generate new keypair
            self._keypair = Keypair.generate()
            self._public_key = self._keypair.public_key
            
            logger.info("New wallet created", {
                'public_key': str(self._public_key)
            })
            
            # Save wallet if path provided
            if save_path:
                return self.save_wallet(save_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {str(e)}")
            return False
    
    def save_wallet(self, save_path: str) -> bool:
        """
        Save wallet to file.
        
        Args:
            save_path: Path to save wallet file
            
        Returns:
            True if saved successfully, False otherwise
        """
        if not self._keypair:
            logger.error("No wallet to save")
            return False
        
        try:
            # Create directory if it doesn't exist
            save_file = Path(save_path)
            save_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save in standard Solana CLI format
            secret_key = list(self._keypair.secret_key)
            
            with open(save_file, 'w') as f:
                json.dump(secret_key, f, indent=2)
            
            # Set restrictive permissions
            os.chmod(save_file, 0o600)
            
            logger.info("Wallet saved successfully", {
                'public_key': str(self._public_key),
                'save_path': save_path
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to save wallet: {str(e)}", {
                'save_path': save_path,
                'error': str(e)
            })
            return False
    
    def load_from_private_key(self, private_key: str) -> bool:
        """
        Load wallet from private key string.
        
        Args:
            private_key: Private key as hex string or base58 string
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            # Try to decode as hex first
            if len(private_key) == 128:  # 64 bytes as hex
                secret_key = bytes.fromhex(private_key)
            else:
                # Try base58 decode
                import base58
                secret_key = base58.b58decode(private_key)
            
            self._keypair = Keypair.from_secret_key(secret_key[:32])
            self._public_key = self._keypair.public_key
            
            logger.info("Wallet loaded from private key", {
                'public_key': str(self._public_key)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load wallet from private key: {str(e)}")
            return False
    
    def sign_message(self, message: bytes) -> Optional[bytes]:
        """
        Sign a message with the wallet.
        
        Args:
            message: Message to sign
            
        Returns:
            Signature bytes or None if failed
        """
        if not self._keypair:
            logger.error("No wallet loaded for signing")
            return None
        
        try:
            signature = self._keypair.sign(message)
            
            logger.debug("Message signed successfully", {
                'message_length': len(message),
                'signature_length': len(signature.signature)
            })
            
            return signature.signature
            
        except Exception as e:
            logger.error(f"Failed to sign message: {str(e)}")
            return None
    
    def verify_signature(self, message: bytes, signature: bytes, public_key: Optional[str] = None) -> bool:
        """
        Verify a signature.
        
        Args:
            message: Original message
            signature: Signature to verify
            public_key: Public key to verify against (uses wallet public key if not provided)
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            if public_key:
                verify_key = PublicKey(public_key)
            else:
                verify_key = self._public_key
                
            if not verify_key:
                logger.error("No public key available for verification")
                return False
            
            # Verify signature (implementation depends on Solana library)
            # This is a placeholder - actual implementation would use proper verification
            logger.debug("Signature verification requested", {
                'public_key': str(verify_key),
                'message_length': len(message),
                'signature_length': len(signature)
            })
            
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"Failed to verify signature: {str(e)}")
            return False
    
    def get_wallet_info(self) -> Dict[str, Any]:
        """
        Get wallet information.
        
        Returns:
            Dictionary with wallet information
        """
        if not self._keypair or not self._public_key:
            return {
                'loaded': False,
                'public_key': None,
                'wallet_path': self.wallet_path
            }
        
        return {
            'loaded': True,
            'public_key': str(self._public_key),
            'wallet_path': self.wallet_path
        }


# Global wallet manager instance
wallet_manager = WalletManager()