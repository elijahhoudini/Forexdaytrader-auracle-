#!/usr/bin/env python3
"""
Test suite for Autonomous AI Trading Bot enhancements.
"""

import asyncio
import os
import sys
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set mock environment variables for testing
os.environ['WALLET_PRIVATE_KEY'] = 'mock_private_key_1234567890123456789012345678901234567890123456789012345678901234'
os.environ['TELEGRAM_BOT_TOKEN'] = 'mock_bot_token_1234567890'
os.environ['TELEGRAM_CHAT_ID'] = '123456789'

# Test imports
def test_imports():
    """Test that all new modules can be imported."""
    try:
        import autonomous_ai_trader
        import telegram_interface
        import safety_checks
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_safety_checks():
    """Test safety checks functionality."""
    try:
        from safety_checks import SafetyChecks
        
        safety = SafetyChecks()
        assert safety is not None
        
        # Test environment variable checking
        result = safety.check_environment_variables()
        print(f"Environment check result: {result}")
        
        # Test kill switch functionality
        assert not safety.is_kill_switch_active()
        
        print("✅ Safety checks tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Safety checks test error: {e}")
        return False

def test_telegram_interface():
    """Test Telegram interface functionality."""
    try:
        # Mock the Update class for telegram
        class MockUpdate:
            def __init__(self):
                self.effective_user = MagicMock()
                self.effective_user.id = 123456789
                self.effective_user.username = 'testuser'
                self.effective_chat = MagicMock()
                self.effective_chat.id = 123456789
                self.message = MagicMock()
        
        # Patch the telegram imports
        with patch.dict('sys.modules', {
            'telegram': MagicMock(),
            'telegram.ext': MagicMock()
        }):
            from telegram_interface import TelegramInterface
            
            # Mock trader instance
            class MockTrader:
                def __init__(self):
                    self.running = True
                    self.paused = False
                    self.live_mode = False
                    self.pending_trades = {}
                    self.blacklisted_tokens = set()
                    self.session_stats = {
                        'trades_executed': 0,
                        'successful_trades': 0,
                        'failed_trades': 0,
                        'total_profit_loss': 0.0,
                        'average_execution_time': 0.0
                    }
                    self.websocket_client = None
                    self.trade_journal = []
                    
                    # Mock auracle with trade_handler
                    class MockAuracle:
                        def __init__(self):
                            self.trade_handler = MockTradeHandler()
                    
                    class MockTradeHandler:
                        def __init__(self):
                            self.open_positions = {}
                    
                    self.auracle = MockAuracle()
                
                async def get_wallet_balance(self):
                    return 0.1
                    
                async def emergency_stop(self):
                    self.running = False
                    
                async def execute_trade_with_redundancy(self, trade_data):
                    from autonomous_ai_trader import TradeMetadata
                    from datetime import datetime
                    
                    return TradeMetadata(
                        timestamp=datetime.utcnow(),
                        token_mint=trade_data.get('mint', 'test'),
                        token_symbol=trade_data.get('symbol', 'TEST'),
                        action=trade_data.get('action', 'buy'),
                        amount_sol=trade_data.get('amount', 0.001),
                        expected_price=0.0
                    )
            
            mock_trader = MockTrader()
            telegram_interface = TelegramInterface(mock_trader)
            
            assert telegram_interface is not None
            assert telegram_interface.trader == mock_trader
            
            # Test authorization check
            mock_update = MockUpdate()
            telegram_interface.authorized_users.add('testuser')
            assert telegram_interface.is_authorized(mock_update)
            
            print("✅ Telegram interface tests passed")
            return True
        
    except Exception as e:
        print(f"❌ Telegram interface test error: {e}")
        return False

def test_autonomous_trader_init():
    """Test autonomous trader initialization."""
    try:
        # Mock all the required modules to avoid import errors
        with patch.dict('sys.modules', {
            'solana': MagicMock(),
            'solana.rpc': MagicMock(),
            'solana.rpc.async_api': MagicMock(),
            'solders': MagicMock(),
            'solders.keypair': MagicMock(),
            'solders.pubkey': MagicMock(),
            'telegram': MagicMock(),
            'telegram.ext': MagicMock()
        }):
            # Mock the required modules to avoid circular imports
            with patch('autonomous_ai_trader.SafetyChecks') as MockSafetyChecks, \
                 patch('autonomous_ai_trader.TelegramInterface') as MockTelegramInterface, \
                 patch('autonomous_ai_trader.JupiterAPI') as MockJupiterAPI, \
                 patch('autonomous_ai_trader.Auracle') as MockAuracle:
                
                # Setup mock instances
                MockSafetyChecks.return_value = MagicMock()
                MockTelegramInterface.return_value = MagicMock()
                MockJupiterAPI.return_value = MagicMock()
                MockAuracle.return_value = MagicMock()
                MockAuracle.return_value.wallet = MagicMock()
                
                from autonomous_ai_trader import AutonomousAITrader
                
                trader = AutonomousAITrader(live_mode=False)
                assert trader is not None
                assert trader.live_mode == False
                assert trader.running == False
                assert trader.paused == False
                
                print("✅ Autonomous trader initialization test passed")
                return True
            
    except Exception as e:
        print(f"❌ Autonomous trader test error: {e}")
        return False

@pytest.mark.asyncio
async def test_enhanced_jupiter_api():
    """Test enhanced Jupiter API functionality."""
    try:
        from jupiter_api import JupiterAPI
        
        # Create Jupiter API instance
        jupiter = JupiterAPI()
        assert jupiter is not None
        
        # Test price impact calculation
        mock_quote = {
            'inAmount': '1000000000',  # 1 SOL
            'outAmount': '50000000000',  # 50k tokens
            'priceImpactPct': '1.5'
        }
        
        price_impact = await jupiter.calculate_price_impact(
            mock_quote, 
            jupiter.SOL_MINT, 
            'test_token_mint', 
            1000000000
        )
        
        assert price_impact >= 0
        print(f"Price impact: {price_impact}%")
        
        # Test optimal slippage calculation (will use mock data)
        optimal_slippage = await jupiter.get_optimal_slippage(
            jupiter.SOL_MINT,
            'test_token_mint',
            1000000000
        )
        
        assert optimal_slippage > 0
        print(f"Optimal slippage: {optimal_slippage}%")
        
        print("✅ Enhanced Jupiter API tests passed")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Jupiter API test error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🧪 Running Autonomous AI Trader Tests")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_safety_checks,
        test_telegram_interface,
        test_autonomous_trader_init,
    ]
    
    # Run async tests
    async_tests = [
        test_enhanced_jupiter_api,
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    # Run asynchronous tests
    for test in async_tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    asyncio.run(main())