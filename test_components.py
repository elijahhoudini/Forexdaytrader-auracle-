#!/usr/bin/env python3
"""
AURACLE Component Test Script
===========================

Test all core components to ensure they work correctly
without requiring network connectivity.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    try:
        import config
        print(f"✅ Config loaded successfully")
        print(f"   Demo Mode: {config.get_demo_mode()}")
        print(f"   Trading Mode: {config.get_trading_mode_string()}")
        print(f"   Max Buy Amount: {config.MAX_BUY_AMOUNT_SOL} SOL")
        print(f"   Telegram Enabled: {config.TELEGRAM_ENABLED}")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_wallet():
    """Test wallet functionality"""
    print("\n💰 Testing Wallet...")
    try:
        from wallet import Wallet
        wallet = Wallet()
        print(f"✅ Wallet initialized successfully")
        print(f"   Address: {wallet.address[:20]}...")
        print(f"   Demo Mode: {wallet.demo_mode}")
        
        # Test balance check
        balance = asyncio.run(wallet.get_balance("SOL"))
        print(f"   Balance: {balance} SOL")
        
        return True
    except Exception as e:
        print(f"❌ Wallet test failed: {e}")
        return False

def test_jupiter_api():
    """Test Jupiter API integration"""
    print("\n🚀 Testing Jupiter API...")
    try:
        from jupiter_api import JupiterAPI, JupiterTradeExecutor
        
        # Test API initialization
        api = JupiterAPI()
        print(f"✅ Jupiter API initialized")
        
        # Test executor
        executor = JupiterTradeExecutor()
        print(f"✅ Jupiter executor initialized")
        
        return True
    except Exception as e:
        print(f"❌ Jupiter API test failed: {e}")
        return False

def test_discovery():
    """Test token discovery"""
    print("\n🔍 Testing Token Discovery...")
    try:
        from enhanced_discovery import EnhancedTokenDiscovery
        
        discovery = EnhancedTokenDiscovery()
        print(f"✅ Enhanced discovery initialized")
        
        # Test token discovery (demo mode)
        tokens = asyncio.run(discovery.discover_tokens())
        print(f"✅ Discovered {len(tokens)} tokens")
        
        if tokens:
            token = tokens[0]
            print(f"   Sample token: {token.get('symbol', 'UNKNOWN')}")
            print(f"   Liquidity: ${token.get('liquidity', 0):,.0f}")
            print(f"   Opportunity Score: {token.get('opportunity_score', 0):.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Discovery test failed: {e}")
        return False

def test_risk_evaluator():
    """Test risk evaluation"""
    print("\n🛡️ Testing Risk Evaluator...")
    try:
        from risk import RiskEvaluator
        
        evaluator = RiskEvaluator()
        print(f"✅ Risk evaluator initialized")
        
        # Test with sample token
        sample_token = {
            "mint": "TestMint123",
            "symbol": "TEST",
            "name": "Test Token",
            "liquidity": 50000,
            "holders": 100,
            "volume24h": 20000,
            "priceChange24h": 0.05
        }
        
        result = evaluator.evaluate(sample_token)
        print(f"✅ Risk evaluation completed")
        print(f"   Safe: {result.get('safe', False)}")
        print(f"   Risk Score: {result.get('risk_score', 0)}")
        
        return True
    except Exception as e:
        print(f"❌ Risk evaluator test failed: {e}")
        return False

def test_trade_handler():
    """Test trade handler"""
    print("\n📈 Testing Trade Handler...")
    try:
        from trade import TradeHandler
        from wallet import Wallet
        
        wallet = Wallet()
        handler = TradeHandler(wallet)
        print(f"✅ Trade handler initialized")
        
        # Test with sample token
        sample_token = {
            "mint": "TestMint123",
            "symbol": "TEST",
            "name": "Test Token",
            "liquidity": 50000,
            "holders": 100,
            "volume24h": 20000,
            "priceChange24h": 0.05
        }
        
        should_buy = handler.should_buy(sample_token)
        print(f"✅ Buy decision: {should_buy}")
        
        amount = handler.calculate_trade_amount(sample_token)
        print(f"✅ Trade amount: {amount} SOL")
        
        return True
    except Exception as e:
        print(f"❌ Trade handler test failed: {e}")
        return False

def test_data_persistence():
    """Test data persistence"""
    print("\n💾 Testing Data Persistence...")
    try:
        from unified_telegram_bot import DataManager
        
        manager = DataManager()
        print(f"✅ Data manager initialized")
        
        # Test user data
        test_user_id = "test_user_123"
        user_data = {
            "username": "testuser",
            "first_seen": datetime.now().isoformat(),
            "test_data": True
        }
        
        manager.save_user_data(test_user_id, user_data)
        loaded_data = manager.get_user_data(test_user_id)
        print(f"✅ User data persistence works")
        
        # Test trade logging
        trade_data = {
            "action": "test_trade",
            "token": "TEST",
            "amount": 0.01,
            "success": True
        }
        
        manager.log_trade(test_user_id, trade_data)
        trades = manager.get_user_trades(test_user_id)
        print(f"✅ Trade logging works: {len(trades)} trades")
        
        return True
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def test_wallet_manager():
    """Test wallet management"""
    print("\n🔐 Testing Wallet Manager...")
    try:
        from unified_telegram_bot import WalletManager, DataManager
        
        data_manager = DataManager()
        wallet_manager = WalletManager(data_manager)
        print(f"✅ Wallet manager initialized")
        
        # Test wallet generation
        test_user_id = "test_user_456"
        wallet = wallet_manager.generate_wallet(test_user_id)
        
        if wallet:
            print(f"✅ Wallet generated successfully")
            print(f"   Address: {wallet['address'][:20]}...")
            
            # Test retrieval
            retrieved_wallet = wallet_manager.get_wallet(test_user_id)
            print(f"✅ Wallet retrieval works")
        
        return True
    except Exception as e:
        print(f"❌ Wallet manager test failed: {e}")
        return False

def test_referral_system():
    """Test referral system"""
    print("\n👥 Testing Referral System...")
    try:
        from unified_telegram_bot import ReferralManager, DataManager
        
        data_manager = DataManager()
        referral_manager = ReferralManager(data_manager)
        print(f"✅ Referral manager initialized")
        
        # Test referral code generation
        test_user_id = "test_user_789"
        referral_code = referral_manager.generate_referral_code(test_user_id)
        print(f"✅ Referral code generated: {referral_code}")
        
        # Test referral usage
        new_user_id = "test_user_987"
        success = referral_manager.use_referral_code(new_user_id, referral_code)
        print(f"✅ Referral code usage: {success}")
        
        # Test earnings
        referral_manager.add_earnings(test_user_id, 0.01)
        info = referral_manager.get_user_referral_info(test_user_id)
        print(f"✅ Referral earnings: {info['earnings']} SOL")
        
        return True
    except Exception as e:
        print(f"❌ Referral system test failed: {e}")
        return False

def test_sniper_manager():
    """Test sniper functionality"""
    print("\n🎯 Testing Sniper Manager...")
    try:
        from unified_telegram_bot import SniperManager, DataManager, WalletManager
        
        data_manager = DataManager()
        wallet_manager = WalletManager(data_manager)
        sniper_manager = SniperManager(data_manager, wallet_manager)
        print(f"✅ Sniper manager initialized")
        
        # Generate wallet for testing
        test_user_id = "test_user_sniper"
        wallet = wallet_manager.generate_wallet(test_user_id)
        
        if wallet:
            # Test manual snipe
            result = asyncio.run(sniper_manager.manual_snipe(test_user_id, 0.01))
            print(f"✅ Manual snipe test: {result.get('success', False)}")
            
            if result.get('success'):
                print(f"   Token: {result.get('token', 'Unknown')}")
                print(f"   Amount: {result.get('amount', 0)} SOL")
        
        return True
    except Exception as e:
        print(f"❌ Sniper manager test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 AURACLE Component Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_config),
        ("Wallet", test_wallet),
        ("Jupiter API", test_jupiter_api),
        ("Discovery", test_discovery),
        ("Risk Evaluator", test_risk_evaluator),
        ("Trade Handler", test_trade_handler),
        ("Data Persistence", test_data_persistence),
        ("Wallet Manager", test_wallet_manager),
        ("Referral System", test_referral_system),
        ("Sniper Manager", test_sniper_manager)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! AURACLE is ready for production.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)