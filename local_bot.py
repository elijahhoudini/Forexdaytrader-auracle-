
#!/usr/bin/env python3
"""
Local fallback bot for when Telegram token is not available
"""

import asyncio
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class LocalBot:
    """Local fallback bot that runs without Telegram"""
    
    def __init__(self):
        self.running = False
        
    async def run_local_mode(self):
        """Run in local mode without Telegram"""
        print("🤖 AURACLE Local Mode - Running without Telegram")
        print("📊 Demo mode enabled - Safe for testing")
        print("⚠️  To use Telegram features, set TELEGRAM_BOT_TOKEN in Secrets")
        print("🔄 Bot will scan for tokens and log activity...")
        print("🛑 Press Ctrl+C to stop")
        
        self.running = True
        scan_count = 0
        
        try:
            while self.running:
                scan_count += 1
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] 🔍 Scan #{scan_count} - Checking for trading opportunities...")
                
                # Simulate token scanning
                await asyncio.sleep(30)  # 30 second intervals
                
                if scan_count % 5 == 0:
                    print(f"[{current_time}] 📊 Status: {scan_count} scans completed, demo mode active")
                    
        except KeyboardInterrupt:
            print("\n🛑 Local bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Local bot error: {e}")
            print(f"❌ Error: {e}")
            
        finally:
            self.running = False
            
    async def stop(self):
        """Stop the local bot"""
        self.running = False
        print("🛑 Local bot stopped")
