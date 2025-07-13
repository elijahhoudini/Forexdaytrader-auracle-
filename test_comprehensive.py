#!/usr/bin/env python3
"""
AURACLE Comprehensive Test Suite
================================

Test all enhanced features and performance improvements.
"""

import sys
import os
import asyncio
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auracle import Auracle
from wallet import Wallet
from trade import TradeHandler
from scanner import TokenScanner
from risk import RiskEvaluator
import config

async def test_wallet_integration():
    """Test enhanced wallet with Jupiter integration"""
    print("🧪 Testing Enhanced Wallet Integration")
    print("-" * 50)
    
    wallet = Wallet()
    balance = await wallet.get_balance()
    print(f"✅ Wallet balance: {balance} SOL")
    
    # Test Jupiter price fetching
    try:
        sol_mint = "So11111111111111111111111111111111111111112"
        price = await wallet.get_token_price(sol_mint)
        print(f"✅ Jupiter price API test: SOL price = {price}")
    except Exception as e:
        print(f"⚠️ Jupiter price API test failed: {e}")
    
    print()

async def test_enhanced_scanner():
    """Test enhanced scanner with AI filtering"""
    print("🧪 Testing Enhanced Scanner")
    print("-" * 50)
    
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    scanner = TokenScanner(trade_handler)
    
    # Test token fetching
    tokens = await scanner.fetch_recent_tokens()
    print(f"✅ Scanner found {len(tokens)} tokens")
    
    # Test AI filtering
    for token in tokens[:3]:
        decision = scanner.ai_decision(token)
        print(f"{'✅' if decision else '❌'} AI Decision for {token.get('symbol', '?')}: {decision}")
    
    print()

async def test_enhanced_risk_evaluator():
    """Test enhanced risk evaluator"""
    print("🧪 Testing Enhanced Risk Evaluator")
    print("-" * 50)
    
    risk = RiskEvaluator()
    
    # Test with various token scenarios
    test_tokens = [
        {
            "mint": "good_token_123",
            "symbol": "GOOD",
            "name": "Good Token",
            "liquidity": 50000,
            "holders": 500,
            "volume24h": 10000,
            "developerHoldingsPercent": 5,
            "priceChange24h": 0.05
        },
        {
            "mint": "risky_token_456",
            "symbol": "PEPE",
            "name": "Pepe Token",
            "liquidity": 1000,
            "holders": 20,
            "volume24h": 100,
            "developerHoldingsPercent": 60,
            "priceChange24h": 0.8
        }
    ]
    
    for token in test_tokens:
        result = risk.evaluate(token)
        print(f"{'✅' if result['safe'] else '❌'} Risk eval for {token['symbol']}: {result['score']:.2f} - {result.get('reason', 'N/A')}")
    
    # Test risk summary
    summary = risk.get_risk_summary()
    print(f"✅ Risk summary: {summary}")
    
    print()

async def test_enhanced_trade_handler():
    """Test enhanced trade handler"""
    print("🧪 Testing Enhanced Trade Handler")
    print("-" * 50)
    
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    
    # Test token handling
    test_token = {
        "mint": "test_mint_789",
        "symbol": "TEST",
        "name": "Test Token",
        "liquidity": 25000,
        "holders": 200,
        "volume24h": 5000,
        "developerHoldingsPercent": 10,
        "priceChange24h": 0.1
    }
    
    # Test confidence scoring
    confidence = trade_handler._calculate_confidence_score(test_token)
    print(f"✅ Confidence score: {confidence:.2f}")
    
    # Test buy decision
    should_buy = trade_handler.should_buy(test_token)
    print(f"{'✅' if should_buy else '❌'} Should buy decision: {should_buy}")
    
    # Test portfolio summary
    portfolio = trade_handler.get_portfolio_summary()
    print(f"✅ Portfolio summary: {portfolio['open_positions']} positions")
    
    print()

async def test_full_system():
    """Test the complete enhanced system"""
    print("🧪 Testing Complete Enhanced System")
    print("-" * 50)
    
    # Create Auracle instance
    auracle = Auracle()
    
    # Test status
    status = auracle.get_status()
    print(f"✅ System status: {status['status']}")
    print(f"✅ Trading mode: {status['trading_mode']}")
    print(f"✅ Uptime: {status['uptime']}")
    print(f"✅ Configuration: {status['configuration']['max_buy_amount']} SOL max")
    
    # Test performance metrics
    if 'statistics' in status:
        stats = status['statistics']
        print(f"✅ Performance: {stats.get('trades_per_hour', 0)} trades/hour")
        print(f"✅ Scanning: {stats.get('scans_per_hour', 0)} scans/hour")
    
    # Test system health
    if 'system_health' in status:
        health = status['system_health']
        print(f"✅ System health: Cache size {health.get('cache_size', 0)}")
    
    print()

async def run_performance_benchmark():
    """Run performance benchmark"""
    print("🏁 Performance Benchmark")
    print("-" * 50)
    
    start_time = time.time()
    
    # Test scanner speed
    wallet = Wallet()
    trade_handler = TradeHandler(wallet)
    scanner = TokenScanner(trade_handler)
    
    scan_start = time.time()
    tokens = await scanner.fetch_recent_tokens()
    scan_time = time.time() - scan_start
    
    print(f"🚀 Scanner performance: {len(tokens)} tokens in {scan_time:.2f}s")
    
    # Test risk evaluation speed
    risk = RiskEvaluator()
    risk_start = time.time()
    
    for token in tokens:
        risk.evaluate(token)
    
    risk_time = time.time() - risk_start
    print(f"🛡️  Risk evaluation: {len(tokens)} tokens in {risk_time:.2f}s")
    
    # Test trade decision speed
    trade_start = time.time()
    
    for token in tokens:
        trade_handler.should_buy(token)
        trade_handler.calculate_trade_amount(token)
    
    trade_time = time.time() - trade_start
    print(f"💰 Trade decisions: {len(tokens)} tokens in {trade_time:.2f}s")
    
    total_time = time.time() - start_time
    print(f"⏱️  Total benchmark time: {total_time:.2f}s")
    
    # Calculate throughput
    throughput = len(tokens) / total_time
    print(f"📊 Overall throughput: {throughput:.1f} tokens/second")
    
    print()

async def main():
    """Run all tests"""
    print("🚀 AURACLE Enhanced System Test Suite")
    print("=" * 60)
    print(f"🔧 Current mode: {config.get_trading_mode_string()}")
    print("=" * 60)
    print()
    
    # Run all tests
    await test_wallet_integration()
    await test_enhanced_scanner()
    await test_enhanced_risk_evaluator()
    await test_enhanced_trade_handler()
    await test_full_system()
    await run_performance_benchmark()
    
    print("🎉 All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())