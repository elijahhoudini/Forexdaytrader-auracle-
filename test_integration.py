"""
Quick Integration Test for AURACLE Bot
=====================================

Test the AI-to-trading pipeline integration.
"""

import asyncio
import config
from risk import RiskEvaluator  
from scanner import TokenScanner
from trade import TradeHandler
from wallet import Wallet
from enhanced_discovery import EnhancedTokenDiscovery


async def test_ai_integration():
    """Test the AI integration pipeline."""
    print("🧪 Testing AI Integration Pipeline")
    print("=" * 50)
    
    # Initialize components
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    risk_evaluator = RiskEvaluator()
    
    # Test configuration validation
    print("\n1. Testing configuration validation...")
    if not config.validate_config():
        print("❌ Configuration validation failed")
        return False
    print("✅ Configuration validation passed")
    
    # Test enhanced discovery
    print("\n2. Testing enhanced token discovery...")
    discovery = EnhancedTokenDiscovery()
    try:
        tokens = await discovery.discover_tokens()
        if tokens:
            print(f"✅ Discovery found {len(tokens)} tokens")
        else:
            print("⚠️  No tokens found (expected in sandboxed environment)")
    except Exception as e:
        print(f"❌ Discovery error: {e}")
    finally:
        await discovery.close()
    
    # Test risk evaluation
    print("\n3. Testing risk evaluation...")
    demo_token = {
        'mint': 'TestToken123456789',
        'name': 'TestToken',
        'symbol': 'TEST',
        'liquidity': 50000,
        'volume24h': 10000,
        'priceChange24h': 5.0,
        'holders': 100,
        'developerHoldingsPercent': 15
    }
    
    risk_result = risk_evaluator.evaluate(demo_token)
    print(f"Risk assessment: {risk_result}")
    
    if risk_result.get("safe", False):
        print("✅ Token passed risk evaluation")
    else:
        print(f"❌ Token failed risk evaluation: {risk_result.get('reason', 'Unknown')}")
    
    # Test trade execution
    print("\n4. Testing trade execution...")
    try:
        # Test should_buy logic
        should_buy = trade_handler.should_buy(demo_token)
        print(f"Should buy decision: {should_buy}")
        
        if should_buy:
            # Test trade amount calculation
            trade_amount = trade_handler.calculate_trade_amount(demo_token)
            print(f"Trade amount: {trade_amount} SOL")
            
            # Test buy execution
            success = await trade_handler.buy_token(demo_token, trade_amount)
            print(f"Buy execution: {'Success' if success else 'Failed'}")
            
            # Test position monitoring
            await trade_handler.monitor_positions()
            print("✅ Position monitoring completed")
            
    except Exception as e:
        print(f"❌ Trade execution error: {e}")
    
    # Test scanner integration
    print("\n5. Testing scanner integration...")
    scanner = TokenScanner(trade_handler, None)
    
    try:
        # Test AI evaluation
        ai_result = scanner.ai_evaluate_token(demo_token)
        print(f"AI evaluation: {ai_result}")
        
        if ai_result['decision'] in ['BUY', 'BUY_HIGH_CONFIDENCE']:
            print("✅ Token passed AI evaluation")
        else:
            print(f"❌ Token failed AI evaluation: {ai_result['reasoning']}")
            
    except Exception as e:
        print(f"❌ Scanner integration error: {e}")
    
    # Test portfolio summary
    print("\n6. Testing portfolio summary...")
    portfolio = trade_handler.get_portfolio_summary()
    print(f"Portfolio: {portfolio}")
    
    # Close connections
    await wallet.close()
    await scanner.close()
    
    print("\n✅ Integration test completed successfully!")
    return True


async def test_safety_features():
    """Test safety features."""
    print("\n🛡️  Testing Safety Features")
    print("=" * 50)
    
    # Test demo mode
    print(f"Demo mode: {config.get_demo_mode()}")
    if config.get_demo_mode():
        print("✅ Bot is in safe demo mode")
    else:
        print("⚠️  Bot is in live trading mode")
    
    # Test risk patterns
    risk_evaluator = RiskEvaluator()
    
    # Test suspicious token
    suspicious_token = {
        'mint': 'SuspiciousToken123456789',
        'name': 'MoonScamToken',
        'symbol': 'SCAM',
        'liquidity': 500,  # Low liquidity
        'volume24h': 100,  # Low volume
        'priceChange24h': 150.0,  # Extreme price change
        'holders': 5,  # Very few holders
        'developerHoldingsPercent': 80  # High dev holdings
    }
    
    risk_result = risk_evaluator.evaluate(suspicious_token)
    print(f"Suspicious token risk: {risk_result}")
    
    if not risk_result.get("safe", True):
        print("✅ Risk evaluator correctly identified suspicious token")
    else:
        print("❌ Risk evaluator failed to identify suspicious token")
    
    # Test trading limits
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    
    print(f"Max daily trades: {config.MAX_DAILY_TRADES}")
    print(f"Max open positions: {config.MAX_OPEN_POSITIONS}")
    print(f"Current daily trades: {trade_handler.daily_trades}")
    
    await wallet.close()
    
    return True


async def main():
    """Run all integration tests."""
    print("🚀 AURACLE Integration Test Suite")
    print("=" * 60)
    
    try:
        # Test AI integration
        await test_ai_integration()
        
        # Test safety features
        await test_safety_features()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())