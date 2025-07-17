#!/usr/bin/env python3
"""
Jupiter API Transaction Signing Fix
=================================

This script directly fixes the transaction signing issue in the Jupiter API.
"""

import os
import sys
import base64
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def apply_fix():
    """Apply the transaction signing fix directly to jupiter_api.py."""
    try:
        # First, read the existing file
        with open('jupiter_api.py', 'r') as file:
            content = file.read()
            
        # Look for the problematic line
        old_sign_code = "transaction.sign([wallet_keypair])"
        
        # New signing code that works with VersionedTransaction
        new_sign_code = """# Get the transaction message
                message = transaction.message
                
                # Sign the message with the private key
                signature = wallet_keypair.sign_message(message.serialize())
                
                # Create a new VersionedTransaction with the signature
                transaction = VersionedTransaction.populate(message, [signature])"""
        
        # Replace the code
        if old_sign_code in content:
            content = content.replace(old_sign_code, new_sign_code)
            print("✅ Found and replaced transaction signing code")
        else:
            print("⚠️ Could not find the exact signing code to replace")
            
            # Try a more flexible replacement approach
            import re
            sign_pattern = r"transaction\.sign\(\[wallet_keypair\]\)"
            
            if re.search(sign_pattern, content):
                content = re.sub(sign_pattern, new_sign_code, content)
                print("✅ Found and replaced transaction signing code (regex)")
            else:
                print("❌ Could not find any transaction signing code to replace")
                return False
        
        # Create backup of the original file
        os.rename('jupiter_api.py', 'jupiter_api.py.bak')
        print("✅ Created backup: jupiter_api.py.bak")
        
        # Write the updated content
        with open('jupiter_api.py', 'w') as file:
            file.write(content)
            
        print("✅ Updated jupiter_api.py with fixed transaction signing")
        return True
        
    except Exception as e:
        print(f"❌ Error applying fix: {e}")
        return False

def main():
    """Apply the Jupiter API transaction signing fix."""
    print("\n" + "=" * 60)
    print("🔧 Jupiter API Transaction Signing Fix")
    print("=" * 60)
    
    if apply_fix():
        print("\n✅ Fix successfully applied!")
        print("You can now run AURACLE with: python3 auracle.py")
    else:
        print("\n❌ Failed to apply fix")
        print("Please check the jupiter_api.py file manually")

if __name__ == "__main__":
    main()
