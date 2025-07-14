#!/usr/bin/env python3
"""
Test script to verify streamlined setup with minimal configuration
"""
import os
import sys
import tempfile
from pathlib import Path

# Add the project root to sys.path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_minimal_setup():
    """Test that the system works with minimal configuration"""
    print("🧪 Testing minimal setup...")
    
    # Create temporary .env file with minimal configuration
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("""
# Minimal configuration test
WALLET_PRIVATE_KEY=test_private_key_placeholder
TELEGRAM_BOT_TOKEN=test_bot_token_placeholder
DEMO_MODE=true
""")
        temp_env_file = f.name
    
    try:
        # Test file storage
        print("📁 Testing file storage...")
        sys.path.insert(0, str(project_root / "src"))
        from solbot.storage.file_storage import FileStorage
        storage = FileStorage(storage_dir="test_storage")
        
        # Test basic storage operations
        storage.store_priv_key(123, "test_key")
        assert storage.get_priv_key(123) == "test_key"
        print("✅ File storage works")
        
        # Test token info provider
        print("🪙 Testing token info provider...")
        from solbot.utils.token_info import TokenInfoProvider
        provider = TokenInfoProvider()
        
        # Test with known SOL token
        sol_token = "So11111111111111111111111111111111111111112"
        name, symbol, decimals, price = provider.get_token_info(sol_token)
        assert symbol == "SOL"
        assert name == "Wrapped SOL"
        assert decimals == 9
        print("✅ Token info provider works")
        
        # Test RPC fallback
        print("🌐 Testing RPC fallback...")
        # Add current directory to Python path for the test
        sys.path.insert(0, str(project_root / "src"))
        from solbot.web3.basic import get_rpc
        rpc = get_rpc()
        assert rpc.startswith("https://")
        print(f"✅ RPC endpoint: {rpc}")
        
        # Test configuration validation
        print("⚙️ Testing configuration validation...")
        os.environ["WALLET_PRIVATE_KEY"] = "test_key"
        os.environ["TELEGRAM_BOT_TOKEN"] = "test_token"
        os.environ["DEMO_MODE"] = "true"
        import config
        # This should pass with minimal config
        print("✅ Configuration validation passed")
        
        print("\n🎉 All tests passed! Minimal setup works correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        if os.path.exists(temp_env_file):
            os.unlink(temp_env_file)
        
        # Clean up test storage
        import shutil
        if os.path.exists("test_storage"):
            shutil.rmtree("test_storage")

def test_database_fallback():
    """Test that database functions fall back to file storage"""
    print("\n🧪 Testing database fallback...")
    
    try:
        # Test database import with fallback
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from solbot.database import connect_db, get_priv_key, set_referral
        
        # Initialize storage
        connect_db()
        
        # Test operations
        set_referral(456, 123)
        print("✅ Database fallback works")
        
        return True
        
    except Exception as e:
        print(f"❌ Database fallback test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_minimal_setup()
    success &= test_database_fallback()
    
    if success:
        print("\n🎊 All streamlined setup tests passed!")
        print("📋 Summary:")
        print("  - File storage works as database replacement")
        print("  - Token info works with free APIs")
        print("  - RPC fallback to free endpoints works")
        print("  - Configuration validation handles minimal setup")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)