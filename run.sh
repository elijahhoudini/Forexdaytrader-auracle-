#!/bin/bash
# AURACLE Bot Launcher Script
# Usage: ./run.sh [options]

echo "🤖 AURACLE Bot Launcher"
echo "======================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if requirements are installed
if ! python3 -c "import solana, requests, pandas" &> /dev/null; then
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
fi

# Create data directory if it doesn't exist
mkdir -p data

# Set permissions
chmod +x run.sh

# Display configuration info
echo "🔧 Starting AURACLE with current configuration..."
echo "   Check config.py for trading parameters"
echo "   Logs will be saved to data/ directory"
echo ""

# Handle command line arguments
case "${1:-}" in
    "--test")
        echo "🧪 Running in test mode (will exit after 60 seconds)..."
        timeout 60 python3 auracle.py
        ;;
    "--config")
        echo "📋 Current configuration:"
        python3 -c "import config; print(config.get_config_dict())"
        ;;
    "--help")
        echo "Available options:"
        echo "  --test     Run for 60 seconds then exit"
        echo "  --config   Display current configuration"
        echo "  --help     Show this help message"
        ;;
    *)
        echo "🚀 Starting AURACLE autonomous trading bot..."
        python3 auracle.py
        ;;
esac