"""
Blockchain Configuration Module
================================

Provides configuration management for blockchain operations including
RPC endpoints, network settings, and API configurations.
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class BlockchainConfig:
    """Configuration class for blockchain operations."""
    
    # RPC Configuration
    rpc_endpoint: str = "https://api.mainnet-beta.solana.com"
    rpc_timeout: int = 30
    max_retries: int = 3
    
    # Jupiter API Configuration
    jupiter_api_url: str = "https://quote-api.jup.ag/v6"
    jupiter_swap_url: str = "https://quote-api.jup.ag/v6/swap"
    
    # Solscan API Configuration
    solscan_api_url: str = "https://pro-api.solscan.io/v1.0"
    solscan_api_key: Optional[str] = None
    
    # Transaction Configuration
    default_slippage: float = 0.005  # 0.5%
    max_slippage: float = 0.05      # 5%
    priority_fee_multiplier: float = 1.2
    
    # Network Configuration
    network: str = "mainnet-beta"
    commitment: str = "confirmed"
    
    # Wallet Configuration
    wallet_path: Optional[str] = None
    
    def __post_init__(self):
        """Initialize configuration from environment variables."""
        self.rpc_endpoint = os.getenv('RPC_ENDPOINT', self.rpc_endpoint)
        self.solscan_api_key = os.getenv('SOLSCAN_API_KEY', self.solscan_api_key)
        self.wallet_path = os.getenv('WALLET_PATH', self.wallet_path)
        
        # Convert string values to appropriate types
        self.rpc_timeout = int(os.getenv('RPC_TIMEOUT', str(self.rpc_timeout)))
        self.max_retries = int(os.getenv('MAX_RETRIES', str(self.max_retries)))
        self.default_slippage = float(os.getenv('DEFAULT_SLIPPAGE', str(self.default_slippage)))
        self.max_slippage = float(os.getenv('MAX_SLIPPAGE', str(self.max_slippage)))
        self.priority_fee_multiplier = float(os.getenv('PRIORITY_FEE_MULTIPLIER', str(self.priority_fee_multiplier)))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'rpc_endpoint': self.rpc_endpoint,
            'rpc_timeout': self.rpc_timeout,
            'max_retries': self.max_retries,
            'jupiter_api_url': self.jupiter_api_url,
            'jupiter_swap_url': self.jupiter_swap_url,
            'solscan_api_url': self.solscan_api_url,
            'solscan_api_key': self.solscan_api_key,
            'default_slippage': self.default_slippage,
            'max_slippage': self.max_slippage,
            'priority_fee_multiplier': self.priority_fee_multiplier,
            'network': self.network,
            'commitment': self.commitment,
            'wallet_path': self.wallet_path,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'BlockchainConfig':
        """Create configuration from dictionary."""
        return cls(**config_dict)


# Global configuration instance
config = BlockchainConfig()