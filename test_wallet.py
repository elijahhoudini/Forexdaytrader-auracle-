#!/usr/bin/env python3
"""
Test AURACLE Wallet Private Key Loading
======================================

Test script to verify that the wallet private key is properly loaded.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import config
from wallet import Wallet

async def test_wallet():
    """Test wallet initialization and private key loading"""
    print("🔍 Testing AURACLE Wallet Configuration")
    print("=" * 50)
    
    # Check configuration
    print(f"📊 Demo Mode: {config.get_demo_mode()}")
    print(f"💰 Wallet Address: {config.WALLET_ADDRESS}")
    print(f"🔐 Private Key Configured: {'Yes' if config.WALLET_PRIVATE_KEY else 'No'}")
    
    if config.WALLET_PRIVATE_KEY:
        print(f"🔑 Private Key Length: {len(config.WALLET_PRIVATE_KEY)} characters")
        print(f"🔑 Private Key Preview: {config.WALLET_PRIVATE_KEY[:20]}...")
    
    print("\n🏦 Initializing Wallet...")
    
    # Initialize wallet
    wallet = Wallet()
    
    # Check wallet status
    print(f"🔄 Wallet Demo Mode: {wallet.demo_mode}")
    print(f"📍 Wallet Address: {wallet.address}")
    print(f"🔑 Keypair Loaded: {'Yes' if wallet.keypair else 'No'}")
    
    if wallet.keypair:
        print(f"✅ Keypair Public Key: {str(wallet.keypair.pubkey())}")
        print(f"✅ Address Match: {str(wallet.keypair.pubkey()) == wallet.address}")
    
    # Test balance
    print("\n💰 Testing Balance...")
    try:
        balance = await wallet.get_balance()
        print(f"💵 SOL Balance: {balance} SOL")
    except Exception as e:
        print(f"❌ Balance Error: {e}")
    
    print("\n🎯 Wallet Test Complete!")

if __name__ == "__main__":
    asyncio.run(test_wallet())
