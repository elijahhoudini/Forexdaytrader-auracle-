"""
Blockchain Integration Module
=============================

This module provides comprehensive blockchain integration functionality
for the AURACLE trading bot, including Jupiter API integration, 
wallet management, transaction handling, and RPC management.
"""

from .blockchain_config import BlockchainConfig
from .blockchain_logger import BlockchainLogger
from .retry_decorator import retry_decorator

# Initialize empty list for available components
__all__ = [
    'BlockchainConfig',
    'BlockchainLogger',
    'retry_decorator',
]

# Try to import optional dependencies
try:
    from .jupiter_client import JupiterClient
    __all__.append('JupiterClient')
except ImportError:
    JupiterClient = None
    print("⚠️  JupiterClient not available - missing aiohttp dependency")

try:
    from .rpc_manager import RPCManager
    __all__.append('RPCManager')
except ImportError:
    RPCManager = None
    print("⚠️  RPCManager not available - missing solana dependency")

try:
    from .wallet_manager import WalletManager
    __all__.append('WalletManager')
except ImportError:
    WalletManager = None
    print("⚠️  WalletManager not available - missing solana dependency")

try:
    from .transaction_manager import TransactionManager
    __all__.append('TransactionManager')
except ImportError:
    TransactionManager = None
    print("⚠️  TransactionManager not available - missing solana dependency")

try:
    from .priority_fee_calculator import PriorityFeeCalculator
    __all__.append('PriorityFeeCalculator')
except ImportError:
    PriorityFeeCalculator = None
    print("⚠️  PriorityFeeCalculator not available - missing dependencies")

try:
    from .solscan_client import SolscanClient
    __all__.append('SolscanClient')
except ImportError:
    SolscanClient = None
    print("⚠️  SolscanClient not available - missing aiohttp dependency")

__version__ = '1.0.0'