"""
Blockchain Integration Test Suite
=================================

Test suite for blockchain integration functionality.
Tests all modules and their interactions.
"""

import asyncio
import pytest
import sys
import os
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from blockchain import (
    BlockchainConfig,
    BlockchainLogger,
    JupiterClient,
    RPCManager,
    WalletManager,
    TransactionManager,
    PriorityFeeCalculator,
    SolscanClient,
    retry_decorator
)
from main_blockchain_integration import BlockchainIntegration


class TestBlockchainConfig:
    """Test blockchain configuration."""
    
    def test_config_initialization(self):
        """Test configuration initialization."""
        config = BlockchainConfig()
        
        assert config.rpc_endpoint == "https://api.mainnet-beta.solana.com"
        assert config.rpc_timeout == 30
        assert config.max_retries == 3
        assert config.default_slippage == 0.005
        assert config.network == "mainnet-beta"
        assert config.commitment == "confirmed"
    
    def test_config_to_dict(self):
        """Test configuration to dictionary conversion."""
        config = BlockchainConfig()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'rpc_endpoint' in config_dict
        assert 'jupiter_api_url' in config_dict
        assert 'default_slippage' in config_dict
    
    def test_config_from_dict(self):
        """Test configuration from dictionary."""
        config_dict = {
            'rpc_endpoint': 'https://test.solana.com',
            'rpc_timeout': 60,
            'max_retries': 5
        }
        
        config = BlockchainConfig.from_dict(config_dict)
        assert config.rpc_endpoint == 'https://test.solana.com'
        assert config.rpc_timeout == 60
        assert config.max_retries == 5


class TestBlockchainLogger:
    """Test blockchain logger."""
    
    def test_logger_initialization(self):
        """Test logger initialization."""
        logger = BlockchainLogger("test_logger")
        
        assert logger.name == "test_logger"
        assert logger.logger.name == "test_logger"
    
    def test_logger_methods(self):
        """Test logger methods."""
        logger = BlockchainLogger("test_logger")
        
        # Test that methods don't raise exceptions
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_transaction_logging(self):
        """Test transaction-specific logging."""
        logger = BlockchainLogger("test_logger")
        
        # Test transaction methods
        logger.transaction_start("test_sig", "swap")
        logger.transaction_success("test_sig", "swap", {"result": "success"})
        logger.transaction_error("test_sig", "swap", Exception("Test error"))
    
    def test_rpc_logging(self):
        """Test RPC-specific logging."""
        logger = BlockchainLogger("test_logger")
        
        # Test RPC methods
        logger.rpc_request("getBalance", {"account": "test"})
        logger.rpc_response("getBalance", True, {"balance": 1000})
        logger.rpc_response("getBalance", False, {"error": "Failed"})


class TestRetryDecorator:
    """Test retry decorator functionality."""
    
    def test_retry_decorator_success(self):
        """Test retry decorator with successful function."""
        call_count = 0
        
        @retry_decorator(max_retries=3)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_decorator_failure(self):
        """Test retry decorator with failing function."""
        call_count = 0
        
        @retry_decorator(max_retries=3, initial_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Test error")
        
        with pytest.raises(Exception):
            test_function()
        
        assert call_count == 4  # Original call + 3 retries
    
    def test_retry_decorator_eventual_success(self):
        """Test retry decorator with eventual success."""
        call_count = 0
        
        @retry_decorator(max_retries=3, initial_delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Test error")
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 3


class TestWalletManager:
    """Test wallet manager."""
    
    def test_wallet_manager_initialization(self):
        """Test wallet manager initialization."""
        wallet_manager = WalletManager()
        
        assert wallet_manager.keypair is None
        assert wallet_manager.public_key is None
        assert wallet_manager.public_key_str is None
    
    def test_create_wallet(self):
        """Test wallet creation."""
        wallet_manager = WalletManager()
        
        success = wallet_manager.create_wallet()
        assert success is True
        assert wallet_manager.keypair is not None
        assert wallet_manager.public_key is not None
        assert wallet_manager.public_key_str is not None
    
    def test_wallet_info(self):
        """Test wallet info retrieval."""
        wallet_manager = WalletManager()
        
        # Test with no wallet loaded
        info = wallet_manager.get_wallet_info()
        assert info['loaded'] is False
        assert info['public_key'] is None
        
        # Test with wallet loaded
        wallet_manager.create_wallet()
        info = wallet_manager.get_wallet_info()
        assert info['loaded'] is True
        assert info['public_key'] is not None
    
    def test_sign_message(self):
        """Test message signing."""
        wallet_manager = WalletManager()
        wallet_manager.create_wallet()
        
        message = b"test message"
        signature = wallet_manager.sign_message(message)
        
        assert signature is not None
        assert isinstance(signature, bytes)


@pytest.mark.asyncio
class TestJupiterClient:
    """Test Jupiter client."""
    
    async def test_jupiter_client_initialization(self):
        """Test Jupiter client initialization."""
        client = JupiterClient()
        
        assert client.api_url.startswith("https://quote-api.jup.ag")
        assert client.session is None
    
    @patch('aiohttp.ClientSession')
    async def test_get_quote(self, mock_session):
        """Test getting Jupiter quote."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value={
            'inputMint': 'So11111111111111111111111111111111111111112',
            'outputMint': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            'outAmount': '1000000',
            'priceImpactPct': '0.1'
        })
        
        mock_session_instance = Mock()
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance
        
        client = JupiterClient()
        client.session = mock_session_instance
        
        quote = await client.get_quote(
            'So11111111111111111111111111111111111111112',
            'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
            1000000
        )
        
        assert quote['inputMint'] == 'So11111111111111111111111111111111111111112'
        assert quote['outputMint'] == 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'
        assert 'outAmount' in quote
    
    @patch('aiohttp.ClientSession')
    async def test_get_tokens(self, mock_session):
        """Test getting Jupiter tokens."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = AsyncMock(return_value=[
            {'symbol': 'SOL', 'name': 'Solana', 'address': 'So11111111111111111111111111111111111111112'},
            {'symbol': 'USDC', 'name': 'USD Coin', 'address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'}
        ])
        
        mock_session_instance = Mock()
        mock_session_instance.get = AsyncMock(return_value=mock_response)
        mock_session.return_value = mock_session_instance
        
        client = JupiterClient()
        client.session = mock_session_instance
        
        tokens = await client.get_tokens()
        
        assert len(tokens) == 2
        assert tokens[0]['symbol'] == 'SOL'
        assert tokens[1]['symbol'] == 'USDC'


@pytest.mark.asyncio
class TestPriorityFeeCalculator:
    """Test priority fee calculator."""
    
    async def test_priority_fee_calculator_initialization(self):
        """Test priority fee calculator initialization."""
        calculator = PriorityFeeCalculator()
        
        assert calculator.rpc_manager is not None
        assert calculator._recent_fees == []
    
    async def test_calculate_priority_fee_default(self):
        """Test priority fee calculation with defaults."""
        calculator = PriorityFeeCalculator()
        
        # Mock get_recent_priority_fees to return empty list
        calculator.get_recent_priority_fees = AsyncMock(return_value=[])
        
        fee = await calculator.calculate_priority_fee()
        
        assert fee >= 1000  # Minimum fee
        assert fee <= 100000  # Maximum fee
    
    async def test_calculate_priority_fee_urgency(self):
        """Test priority fee calculation with different urgency levels."""
        calculator = PriorityFeeCalculator()
        
        # Mock get_recent_priority_fees
        calculator.get_recent_priority_fees = AsyncMock(return_value=[1000, 2000, 3000])
        
        low_fee = await calculator.calculate_priority_fee(urgency="low")
        high_fee = await calculator.calculate_priority_fee(urgency="high")
        
        assert low_fee < high_fee
    
    async def test_get_fee_recommendation(self):
        """Test fee recommendation generation."""
        calculator = PriorityFeeCalculator()
        
        # Mock get_recent_priority_fees
        calculator.get_recent_priority_fees = AsyncMock(return_value=[1000, 2000, 3000])
        
        recommendation = await calculator.get_fee_recommendation()
        
        assert 'recommendations' in recommendation
        assert 'statistics' in recommendation
        assert 'low' in recommendation['recommendations']
        assert 'medium' in recommendation['recommendations']
        assert 'high' in recommendation['recommendations']
        assert 'urgent' in recommendation['recommendations']


@pytest.mark.asyncio
class TestBlockchainIntegration:
    """Test main blockchain integration."""
    
    async def test_blockchain_integration_initialization(self):
        """Test blockchain integration initialization."""
        integration = BlockchainIntegration()
        
        assert integration.config is not None
        assert integration.logger is not None
        assert integration.rpc_manager is not None
        assert integration.wallet_manager is not None
        assert integration.transaction_manager is not None
        assert integration.jupiter_client is not None
        assert integration.solscan_client is not None
    
    async def test_get_status(self):
        """Test status retrieval."""
        integration = BlockchainIntegration()
        
        status = integration.get_status()
        
        assert isinstance(status, dict)
        assert 'rpc_connected' in status
        assert 'wallet_loaded' in status
        assert 'wallet_address' in status
        assert 'rpc_endpoint' in status
        assert 'pending_transactions' in status
        assert 'config' in status
    
    @patch('blockchain.rpc_manager.RPCManager.connect')
    @patch('blockchain.rpc_manager.RPCManager.get_recent_blockhash')
    async def test_initialize_success(self, mock_get_blockhash, mock_connect):
        """Test successful initialization."""
        mock_connect.return_value = None
        mock_get_blockhash.return_value = "test_blockhash"
        
        integration = BlockchainIntegration()
        
        success = await integration.initialize()
        
        assert success is True
        mock_connect.assert_called_once()
        mock_get_blockhash.assert_called_once()


def run_tests():
    """Run all tests."""
    print("🧪 Running Blockchain Integration Tests")
    
    # Run pytest with current file
    pytest.main([__file__, '-v'])


if __name__ == "__main__":
    run_tests()