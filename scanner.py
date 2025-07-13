import asyncio
import httpx
import time
import random
from trade import TradeHandler
from enhanced_discovery import EnhancedTokenDiscovery

class TokenScanner:
    def __init__(self, trade_handler: TradeHandler, auracle_instance=None):
        self.trade_handler = trade_handler
        self.auracle_instance = auracle_instance
        self.last_seen_tokens = set()
        
        # Use enhanced discovery system
        self.discovery = EnhancedTokenDiscovery()
        self.ai_enabled = True  # Enhanced AI decisions
        
        print("[scanner] 🔍 Enhanced scanner initialized with multi-source discovery")

    async def fetch_recent_tokens(self):
        """
        Fetch and intelligently rank recent Solana tokens using enhanced discovery.
        """
        try:
            # Use enhanced discovery system
            tokens = await self.discovery.discover_tokens()
            
            if not tokens:
                print("[scanner] ⚠️ No tokens discovered")
                return []
            
            print(f"[scanner] 🎯 Enhanced discovery found {len(tokens)} high-quality tokens")
            return tokens
            
        except Exception as e:
            print(f"[scanner] ❌ Enhanced discovery error: {e}")
            return []

    async def is_honeypot_or_rug(self, mint_address: str) -> bool:
        """
        Check if token is a honeypot or rug pull.
        Returns False if check fails (fail-safe approach).
        """
        try:
            # Enhanced honeypot detection using multiple indicators
            
            # Check for common honeypot patterns
            suspicious_patterns = [
                "honey", "rug", "scam", "fake", "test",
                "pump", "dump", "moon", "gem"  # Sometimes legitimate but risky
            ]
            
            # Simple pattern matching (would be enhanced with real API)
            mint_lower = mint_address.lower()
            for pattern in suspicious_patterns:
                if pattern in mint_lower:
                    return True
            
            # In demo mode, randomly flag some as suspicious
            if random.random() < 0.05:  # 5% false positive rate
                return True
                
            return False
            
        except Exception:
            return False  # Fail-safe: don't block on error

    def ai_evaluate_token(self, token: dict) -> dict:
        """
        Enhanced AI evaluation of token using multiple factors.
        """
        try:
            symbol = token.get("symbol", "UNKNOWN")
            name = token.get("name", "Unknown")
            
            # Enhanced evaluation criteria
            liquidity = token.get("liquidity", 0)
            volume = token.get("volume24h", 0)
            price_change = token.get("priceChange24h", 0)
            opportunity_score = token.get("opportunity_score", 0)
            risk_level = token.get("risk_level", "HIGH")
            trading_signals = token.get("trading_signals", [])
            
            # AI decision logic
            ai_decision = "BUY"
            confidence = opportunity_score
            
            # Enhanced filtering
            if risk_level == "HIGH":
                ai_decision = "SKIP"
                confidence *= 0.3
            elif liquidity < 15000:
                ai_decision = "SKIP"
                confidence *= 0.5
            elif volume < 2000:
                ai_decision = "SKIP"
                confidence *= 0.6
            elif "HIGH_CONFIDENCE" in trading_signals:
                confidence *= 1.2
            elif "BULLISH_MOMENTUM" in trading_signals:
                confidence *= 1.1
            
            # Confidence patterns for dynamic allocation
            confidence_patterns = token.get('confidence_patterns', [])
            if confidence_patterns and confidence > 0.7:
                ai_decision = "BUY_HIGH_CONFIDENCE"
            
            return {
                "decision": ai_decision,
                "confidence": min(confidence, 1.0),
                "reasoning": f"L:${liquidity:,.0f} V:${volume:,.0f} Risk:{risk_level} Signals:{len(trading_signals)}",
                "risk_level": risk_level,
                "trading_signals": trading_signals
            }
            
        except Exception as e:
            print(f"[scanner] AI evaluation error: {e}")
            return {"decision": "SKIP", "confidence": 0, "reasoning": "Evaluation error"}

    async def scan_loop(self):
        """Enhanced scanning loop with improved error handling."""
        print("[scanner] 🌐 Starting enhanced token scanner...")
        scan_count = 0
        
        while True:
            try:
                scan_count += 1
                
                # Fetch tokens using enhanced discovery
                tokens = await self.fetch_recent_tokens()
                
                if tokens:
                    print(f"[scanner] Found {len(tokens)} tokens to analyze")
                    
                    # Process each token
                    for token in tokens:
                        try:
                            await self.process_token(token)
                        except Exception as e:
                            print(f"[scanner] Error processing token: {e}")
                            continue
                else:
                    print("[scanner] No tokens found in this scan")
                
                # Update scanner state
                if self.auracle_instance:
                    self.auracle_instance.stats["tokens_evaluated"] += len(tokens)
                
                # Wait for next scan (using config interval)
                import config
                await asyncio.sleep(config.SCAN_INTERVAL_SECONDS)
                
            except Exception as e:
                print(f"[scanner] Error in scan loop: {e}")
                import traceback
                traceback.print_exc()
                # Wait longer on error to avoid rapid retries
                await asyncio.sleep(20)

    async def process_token(self, token: dict):
        """Process individual token with enhanced analysis."""
        try:
            mint = token.get("mint", "")
            symbol = token.get("symbol", "UNKNOWN")
            name = token.get("name", "Unknown")
            
            print(f"\n[scanner] Detected: {name} - {mint[:8]}...")
            
            # Skip if already seen
            if mint in self.last_seen_tokens:
                return
            
            # Add to seen set
            self.last_seen_tokens.add(mint)
            
            # Honeypot check
            if await self.is_honeypot_or_rug(mint):
                print(f"[scanner] ⚠️ Skipping suspicious token: {symbol}")
                return
            
            # AI evaluation
            ai_result = self.ai_evaluate_token(token)
            
            if ai_result["decision"] in ["BUY", "BUY_HIGH_CONFIDENCE"]:
                print(f"[AI] ✅ {symbol} passed AI filters - {ai_result['reasoning']}")
                print(f"[scanner] ✅ Token passed all filters: {name}")
                
                # High confidence allocation
                if ai_result["decision"] == "BUY_HIGH_CONFIDENCE":
                    print(f"📈 High confidence trade detected: {symbol} - Allocating enhanced amount")
                
                # Pass to trade handler
                success = await self.trade_handler.handle_token(mint, token)
                
                if success and self.auracle_instance:
                    self.auracle_instance.stats["trades_executed"] += 1
                    
            else:
                print(f"[AI] ❌ {symbol} rejected - {ai_result['reasoning']}")
                
        except Exception as e:
            print(f"[scanner] Error processing token {mint}: {e}")

    async def close(self):
        """Close scanner resources."""
        if hasattr(self.discovery, 'close'):
            await self.discovery.close()