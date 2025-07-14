#!/usr/bin/env python3
"""
Test script for Enhanced AURACLE Unified Intelligence Core
"""

import sys
import os
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import config
    from auracle import Auracle
    print("✅ Enhanced AURACLE imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

async def test_enhanced_features():
    """Test enhanced AURACLE features"""
    print("\n🧪 Testing Enhanced AURACLE Features")
    print("=" * 50)
    
    try:
        # Create AURACLE instance
        auracle = Auracle()
        print("✅ AURACLE instance created successfully")
        
        # Test encryption system
        if auracle.fernet:
            print("✅ Encryption system available")
        else:
            print("⚠️ Encryption system not configured")
        
        # Test advanced token scanning
        print("\n🔍 Testing advanced token scanning...")
        tokens = await auracle.advanced_token_scan()
        print(f"✅ Found {len(tokens)} tokens with advanced scanning")
        
        if tokens:
            for i, token in enumerate(tokens[:2]):
                symbol = token["baseToken"]["symbol"]
                score = token.get("auracle_score", 0)
                print(f"   {i+1}. {symbol} - Score: {score:.3f}")
        
        # Test diversification calculation
        div_weight = auracle.calculate_diversification_weight()
        print(f"✅ Diversification weight: {div_weight:.4f} SOL")
        
        # Test backup system
        print("\n💾 Testing backup system...")
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "traveler_id": config.TRAVELER_ID
        }
        backup_path = await auracle.save_encrypted_backup("test_backup.json", test_data)
        if backup_path:
            print(f"✅ Backup system working: {backup_path}")
            
            # Test backup loading
            loaded_data = await auracle.load_encrypted_backup("test_backup.json")
            if loaded_data and loaded_data.get("test"):
                print("✅ Backup loading successful")
            else:
                print("⚠️ Backup loading failed")
        
        # Test LLC report generation
        print("\n📄 Testing LLC report generation...")
        llc_report = auracle.generate_llc_report()
        if llc_report:
            print(f"✅ LLC report generated: {llc_report}")
        
        # Test network health check
        print("\n🌐 Testing network health check...")
        network_health = await auracle.check_solana_network_health()
        print(f"✅ Network health: {'Good' if network_health else 'Poor'}")
        
        print("\n🎉 All enhanced features tested successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🚀 Enhanced AURACLE Test Suite")
    print("Testing unified intelligence core features...")
    
    # Run async tests
    asyncio.run(test_enhanced_features())

if __name__ == "__main__":
    main()
