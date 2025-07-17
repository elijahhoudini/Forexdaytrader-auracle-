#!/bin/bash
# AURACLE AutoStart Script
# This script automatically starts AURACLE using credentials from .env file

# Make sure our python script is executable
chmod +x start_with_env.py

# Check if .env file exists
if [ ! -f .env ]; then
  echo "⚠️ No .env file found. Creating one from template..."
  if [ -f env_template ]; then
    cp env_template .env
    echo "✅ Created .env file from template."
    echo "⚠️ IMPORTANT: Edit .env file to add your wallet private key!"
    echo "📝 Opening .env file for editing..."
    if command -v nano >/dev/null 2>&1; then
      nano .env
    elif command -v vim >/dev/null 2>&1; then
      vim .env
    else
      echo "❌ Could not find a text editor (nano or vim)."
      echo "Please edit .env file manually to add your wallet private key."
    fi
  else
    echo "❌ env_template not found. Creating minimal .env file..."
    echo "# AURACLE Environment Configuration" > .env
    echo "WALLET_PRIVATE_KEY=" >> .env
    echo "⚠️ Please add your wallet private key to .env file"
  fi
fi

# Start the bot
echo "🚀 Starting AURACLE with credentials from .env file..."
python3 start_with_env.py
