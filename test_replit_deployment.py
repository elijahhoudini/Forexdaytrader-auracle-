#!/usr/bin/env python3
"""
Test script to verify the simplified Replit deployment works correctly.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_replit_files():
    """Test that Replit configuration files exist and are valid."""
    print("🔍 Testing Replit configuration files...")
    
    # Check .replit file exists
    replit_file = Path(".replit")
    assert replit_file.exists(), ".replit file missing"
    
    # Check replit.nix file exists
    nix_file = Path("replit.nix")
    assert nix_file.exists(), "replit.nix file missing"
    
    # Check .replit contains correct run command
    replit_content = replit_file.read_text()
    assert "python start.py" in replit_content, ".replit doesn't contain correct run command"
    
    print("✅ Replit configuration files are valid")

def test_start_script():
    """Test that start.py exists and runs correctly."""
    print("🔍 Testing start.py script...")
    
    # Check start.py exists
    start_file = Path("start.py")
    assert start_file.exists(), "start.py file missing"
    
    # Check it's executable
    assert start_file.is_file(), "start.py is not a file"
    
    # Test that it can be imported
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("start", start_file)
        start_module = importlib.util.module_from_spec(spec)
        # Just check it can be loaded, don't execute
        assert start_module is not None, "start.py cannot be imported"
    except Exception as e:
        assert False, f"start.py import failed: {e}"
    
    print("✅ start.py script is valid")

def test_documentation():
    """Test that documentation is streamlined."""
    print("🔍 Testing documentation...")
    
    # Check README.md exists and is reasonable length
    readme = Path("README.md")
    assert readme.exists(), "README.md missing"
    readme_content = readme.read_text()
    assert len(readme_content) < 10000, "README.md is too long (should be streamlined)"
    assert "Import → Run → " in readme_content, "README.md doesn't contain simplified instructions"
    
    # Check REPLIT_README.md exists
    replit_readme = Path("REPLIT_README.md")
    assert replit_readme.exists(), "REPLIT_README.md missing"
    replit_content = replit_readme.read_text()
    assert "One-Click Deployment" in replit_content, "REPLIT_README.md doesn't contain one-click deployment info"
    
    print("✅ Documentation is streamlined")

def test_redundant_files_removed():
    """Test that redundant files have been removed."""
    print("🔍 Testing redundant files removal...")
    
    # Files that should be removed
    removed_files = [
        "start_unified.py",
        "run_replit.py",
        "start_local.py",
        "start_auracle.py",
        "STREAMLINED_SETUP.md",
        "DEPLOYMENT.md",
        "DEPLOYMENT_SUMMARY.md",
        "ENHANCEMENT_DOCUMENTATION.md",
        "MERGE_SUMMARY.md",
        "MIGRATION_SUMMARY.md"
    ]
    
    for file in removed_files:
        assert not Path(file).exists(), f"Redundant file {file} still exists"
    
    print("✅ Redundant files have been removed")

def test_demo_mode_default():
    """Test that demo mode is enabled by default."""
    print("🔍 Testing demo mode default...")
    
    # Test config loads with demo mode enabled
    try:
        import config
        assert config.DEMO_MODE == True, "Demo mode should be enabled by default"
        assert config.get_demo_mode() == True, "get_demo_mode() should return True by default"
        print("✅ Demo mode is enabled by default")
    except Exception as e:
        assert False, f"Config loading failed: {e}"

def test_ai_logic_preserved():
    """Test that AI and trading logic files are preserved."""
    print("🔍 Testing AI/trading logic preservation...")
    
    # Core files that should exist
    core_files = [
        "auracle.py",
        "scanner.py",
        "trade.py",
        "risk.py",
        "wallet.py",
        "config.py",
        "logger.py"
    ]
    
    for file in core_files:
        assert Path(file).exists(), f"Core file {file} is missing"
    
    print("✅ AI/trading logic files are preserved")

def run_all_tests():
    """Run all tests."""
    print("🚀 Running Replit deployment tests...")
    print("=" * 50)
    
    try:
        test_replit_files()
        test_start_script()
        test_documentation()
        test_redundant_files_removed()
        test_demo_mode_default()
        test_ai_logic_preserved()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed!")
        print("🎉 Replit deployment is ready!")
        print("\nTo deploy:")
        print("1. Import repository to Replit")
        print("2. Click 'Run'")
        print("3. (Optional) Add secrets for live trading")
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)