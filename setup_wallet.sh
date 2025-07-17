#!/bin/bash
# setup_wallet.sh - Securely set wallet key for AURACLE bot
# Created: July 17, 2025

echo "===================================="
echo "🔐 AURACLE Secure Wallet Setup 🔐"
echo "===================================="
echo "This script sets your wallet key as an environment variable"
echo "without storing it in any files for maximum security."
echo ""
echo "IMPORTANT: Your private key will only be stored in memory,"
echo "you'll need to run this script each time you restart the bot."
echo "===================================="
echo ""

# Check if the key was provided as an argument
if [ $# -eq 1 ]; then
    WALLET_KEY=$1
else
    read -p "Enter your wallet private key (will not be displayed): " -s WALLET_KEY
    echo ""
fi

# Export the key as an environment variable
export WALLET_PRIVATE_KEY=$WALLET_KEY

# Clear the variable from the script to minimize exposure
WALLET_KEY=""

echo "✅ Wallet key set successfully as environment variable"
echo "To run the bot with your wallet key loaded, use:"
echo "./start_secure.sh"
echo ""
echo "Warning: This key will only be available in the current terminal session"

# Generate address (information only)
echo ""
echo "🔍 Checking wallet configuration..."
python -c "
import base58
from solders.keypair import Keypair
import os

try:
    key = os.environ.get('WALLET_PRIVATE_KEY')
    if not key:
        print('❌ No wallet key found in environment')
        exit(1)

    # Try to decode the key
    private_key_bytes = base58.b58decode(key)
    
    # Create keypair from seed bytes
    if len(private_key_bytes) == 32:
        keypair = Keypair.from_seed(private_key_bytes)
    elif len(private_key_bytes) == 64:
        keypair = Keypair.from_bytes(private_key_bytes)
    else:
        print(f'❌ Invalid key length: {len(private_key_bytes)}')
        exit(1)

    address = str(keypair.pubkey())
    masked_address = address[:6] + '...' + address[-6:]
    print(f'✅ Wallet decoded successfully')
    print(f'📬 Wallet address: {masked_address}')
except Exception as e:
    print(f'❌ Error: {str(e)}')
"
