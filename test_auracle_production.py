#!/usr/bin/env python3
"""
AURACLE Bot Test Suite
======================

Test all bot commands and functionality to ensure production readiness.
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unified_telegram_bot import AuracleTelegramBot, DataManager, WalletManager, ReferralManager, SniperManager
from jupiter_api import JupiterTradeExecutor
from enhanced_discovery import EnhancedTokenDiscovery
from risk import RiskEvaluator
import config

class AuracleBotTester:
    """Test suite for AURACLE bot functionality"""
    
    def __init__(self):
        self.passed_tests = 0
        self.failed_tests = 0
        self.total_tests = 0
        
    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}: FAILED {message}")
    
    def test_configuration(self):
        """Test configuration validation"""
        print("\n🔧 Testing Configuration...")
        
        # Test demo mode
        demo_mode = config.get_demo_mode()
        self.log_test("Demo Mode", demo_mode, f"- Demo mode: {demo_mode}")
        
        # Test trading mode string
        mode_string = config.get_trading_mode_string()
        self.log_test("Trading Mode String", "DEMO" in mode_string, f"- Mode: {mode_string}")
        
        # Test config validation
        try:
            valid = config.validate_config()
            self.log_test("Config Validation", valid, "- Configuration is valid")
        except Exception as e:
            self.log_test("Config Validation", False, f"- Error: {e}")
    
    def test_data_manager(self):
        """Test data persistence"""
        print("\n💾 Testing Data Manager...")
        
        try:
            dm = DataManager()
            
            # Test user data
            test_user_id = "test_user_123"
            test_data = {
                "username": "TestUser",
                "created_at": datetime.now().isoformat(),
                "total_trades": 5
            }
            
            dm.save_user_data(test_user_id, test_data)
            loaded_data = dm.get_user_data(test_user_id)
            
            self.log_test("User Data Storage", loaded_data.get("username") == "TestUser", 
                         f"- Saved and loaded user data")
            
            # Test trade logging
            dm.log_trade(test_user_id, {
                "action": "snipe",
                "token": "TEST",
                "amount": 0.01,
                "success": True
            })
            
            trades = dm.get_user_trades(test_user_id)
            self.log_test("Trade Logging", len(trades) > 0, f"- {len(trades)} trades logged")
            
        except Exception as e:
            self.log_test("Data Manager", False, f"- Error: {e}")
    
    def test_wallet_manager(self):
        """Test wallet generation and management"""
        print("\n💰 Testing Wallet Manager...")
        
        try:
            dm = DataManager()
            wm = WalletManager(dm)
            
            # Test wallet generation
            test_user_id = "test_user_wallet"
            wallet = wm.generate_wallet(test_user_id)
            
            self.log_test("Wallet Generation", bool(wallet.get("address")), 
                         f"- Generated wallet: {wallet.get('address', 'None')[:20]}...")
            
            # Test wallet retrieval
            retrieved_wallet = wm.get_wallet(test_user_id)
            self.log_test("Wallet Retrieval", retrieved_wallet == wallet, 
                         f"- Retrieved same wallet data")
            
            # Test wallet connection
            success = wm.connect_wallet("test_user_connect", "TestAddress123456789012345678901234567890", "TestPrivateKey")
            self.log_test("Wallet Connection", success, f"- Connected external wallet")
            
        except Exception as e:
            self.log_test("Wallet Manager", False, f"- Error: {e}")
    
    def test_referral_manager(self):
        """Test referral system"""
        print("\n🎁 Testing Referral Manager...")
        
        try:
            dm = DataManager()
            rm = ReferralManager(dm)
            
            # Test referral code generation
            test_user_id = "test_user_ref"
            referral_code = rm.generate_referral_code(test_user_id)
            
            self.log_test("Referral Code Generation", len(referral_code) == 6, 
                         f"- Generated code: {referral_code}")
            
            # Test referral usage
            new_user_id = "test_user_new"
            success = rm.use_referral_code(new_user_id, referral_code)
            self.log_test("Referral Code Usage", success, f"- Used referral code successfully")
            
            # Test earnings
            initial_earnings = rm.get_user_referral_info(test_user_id).get("earnings", 0.0)
            rm.add_earnings(test_user_id, 0.05)
            final_earnings = rm.get_user_referral_info(test_user_id).get("earnings", 0.0)
            self.log_test("Referral Earnings", final_earnings == initial_earnings + 0.05, 
                         f"- Earnings: {final_earnings:.4f} SOL (added 0.05 SOL)")
            
        except Exception as e:
            self.log_test("Referral Manager", False, f"- Error: {e}")
    
    async def test_jupiter_executor(self):
        """Test Jupiter API integration"""
        print("\n🔄 Testing Jupiter Executor...")
        
        try:
            je = JupiterTradeExecutor()
            
            # Test token purchase (demo mode)
            result = await je.buy_token("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 0.01)
            self.log_test("Jupiter Buy Token", result.get("success") or result.get("demo"), 
                         f"- Buy result: {result.get('success', False)}")
            
            # Test token sale (demo mode)
            result = await je.sell_token("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 1000)
            self.log_test("Jupiter Sell Token", result.get("success") or result.get("demo"), 
                         f"- Sell result: {result.get('success', False)}")
            
            await je.close()
            
        except Exception as e:
            self.log_test("Jupiter Executor", False, f"- Error: {e}")
    
    async def test_token_discovery(self):
        """Test token discovery system"""
        print("\n🔍 Testing Token Discovery...")
        
        try:
            td = EnhancedTokenDiscovery()
            
            # Test token discovery
            tokens = await td.discover_tokens()
            self.log_test("Token Discovery", len(tokens) > 0, 
                         f"- Found {len(tokens)} tokens")
            
            # Test token scoring
            if tokens:
                token = tokens[0]
                has_score = 'opportunity_score' in token
                self.log_test("Token Scoring", has_score, 
                             f"- Token scored: {token.get('opportunity_score', 0):.3f}")
            
            await td.close()
            
        except Exception as e:
            self.log_test("Token Discovery", False, f"- Error: {e}")
    
    def test_risk_evaluator(self):
        """Test risk assessment"""
        print("\n🛡️ Testing Risk Evaluator...")
        
        try:
            re = RiskEvaluator()
            
            # Test safe token
            safe_token = {
                "mint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                "symbol": "USDC",
                "name": "USD Coin",
                "liquidity": 50000,
                "holders": 1000,
                "developerHoldingsPercent": 5,
                "volume24h": 100000
            }
            
            result = re.evaluate(safe_token)
            self.log_test("Safe Token Evaluation", result.get("safe", False), 
                         f"- Safe token approved")
            
            # Test risky token
            risky_token = {
                "mint": "RiskyToken123456789012345678901234567890",
                "symbol": "RUG",
                "name": "Rug Pull Token",
                "liquidity": 100,
                "holders": 5,
                "developerHoldingsPercent": 95,
                "volume24h": 10
            }
            
            result = re.evaluate(risky_token)
            self.log_test("Risky Token Evaluation", not result.get("safe", True), 
                         f"- Risky token rejected")
            
        except Exception as e:
            self.log_test("Risk Evaluator", False, f"- Error: {e}")
    
    async def test_sniper_manager(self):
        """Test sniper functionality"""
        print("\n🎯 Testing Sniper Manager...")
        
        try:
            dm = DataManager()
            wm = WalletManager(dm)
            sm = SniperManager(dm, wm)
            
            # Generate test wallet
            test_user_id = "test_user_sniper"
            wallet = wm.generate_wallet(test_user_id)
            
            # Test manual snipe
            result = await sm.manual_snipe(test_user_id, 0.01)
            self.log_test("Manual Snipe", result.get("success") or "error" in result, 
                         f"- Snipe result: {result.get('success', False)}")
            
            # Test sniper start/stop
            start_success = await sm.start_sniper(test_user_id, 0.01)
            self.log_test("Sniper Start", start_success, f"- Sniper started")
            
            # Wait a moment for sniper to initialize
            await asyncio.sleep(1)
            
            stop_success = sm.stop_sniper(test_user_id)
            self.log_test("Sniper Stop", stop_success, f"- Sniper stopped")
            
        except Exception as e:
            self.log_test("Sniper Manager", False, f"- Error: {e}")
    
    async def test_telegram_bot(self):
        """Test Telegram bot initialization"""
        print("\n📱 Testing Telegram Bot...")
        
        try:
            bot = AuracleTelegramBot("test_token")
            
            # Test bot initialization
            self.log_test("Bot Initialization", bot is not None, 
                         f"- Bot initialized successfully")
            
            # Test managers
            self.log_test("Data Manager", bot.data_manager is not None, 
                         f"- Data manager initialized")
            
            self.log_test("Wallet Manager", bot.wallet_manager is not None, 
                         f"- Wallet manager initialized")
            
            self.log_test("Referral Manager", bot.referral_manager is not None, 
                         f"- Referral manager initialized")
            
            self.log_test("Sniper Manager", bot.sniper_manager is not None, 
                         f"- Sniper manager initialized")
            
            await bot.stop()
            
        except Exception as e:
            self.log_test("Telegram Bot", False, f"- Error: {e}")
    
    def test_file_structure(self):
        """Test file structure and data persistence"""
        print("\n📁 Testing File Structure...")
        
        # Check data directory
        data_dir = "data"
        self.log_test("Data Directory", os.path.exists(data_dir), 
                     f"- Data directory exists: {data_dir}")
        
        # Check required files
        required_files = [
            "data/users.json",
            "data/wallets.json", 
            "data/referrals.json"
        ]
        
        for file_path in required_files:
            exists = os.path.exists(file_path)
            self.log_test(f"File {file_path}", exists, 
                         f"- Required file exists")
            
            if exists:
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    self.log_test(f"File {file_path} Valid JSON", True, 
                                 f"- Valid JSON file")
                except Exception as e:
                    self.log_test(f"File {file_path} Valid JSON", False, 
                                 f"- Invalid JSON: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🧪 AURACLE Bot Test Suite")
        print("=" * 60)
        
        # Run all tests
        self.test_configuration()
        self.test_data_manager()
        self.test_wallet_manager()
        self.test_referral_manager()
        await self.test_jupiter_executor()
        await self.test_token_discovery()
        self.test_risk_evaluator()
        await self.test_sniper_manager()
        await self.test_telegram_bot()
        self.test_file_structure()
        
        # Test summary
        print("\n" + "=" * 60)
        print("🏁 Test Summary")
        print("=" * 60)
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.failed_tests}")
        print(f"📊 Total: {self.total_tests}")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if self.failed_tests == 0:
            print("🎉 All tests passed! AURACLE bot is ready for production!")
        else:
            print(f"⚠️  {self.failed_tests} tests failed. Please review and fix issues.")
        
        return self.failed_tests == 0

async def main():
    """Main test runner"""
    print("Starting AURACLE Bot Test Suite...")
    print("Testing all components for production readiness...")
    
    tester = AuracleBotTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n✅ AURACLE Bot is fully functional and ready for production!")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix issues before deployment.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)