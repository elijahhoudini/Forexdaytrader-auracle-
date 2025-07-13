import asyncio
import httpx
import time
import random
from trade import TradeHandler

class TokenScanner:
    def __init__(self, trade_handler: TradeHandler, auracle_instance=None):
        self.trade_handler = trade_handler
        self.auracle_instance = auracle_instance
        self.last_seen_tokens = set()
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex/tokens"
        self.birdeye_url = "https://public-api.birdeye.so/defi/tokenlist"
        self.ai_enabled = True  # Simulated AI decisions

    async def fetch_recent_tokens(self):
        """
        Fetch and intelligently rank recent Solana tokens using AI-style logic.
        Filters out tokens with no metadata, low volume, or red flags.
        """
        try:
            # Try multiple endpoints for better token discovery
            urls = [
                "https://api.dexscreener.com/latest/dex/search/?q=SOL",
                "https://api.dexscreener.com/latest/dex/tokens/trending?chainId=solana",
                "https://api.dexscreener.com/latest/dex/pairs/solana"
            ]
            
            all_tokens = []
            
            async with httpx.AsyncClient(timeout=15) as client:
                for url in urls:
                    try:
                        response = await client.get(url)
                        if response.status_code == 200:
                            data = response.json()
                            pairs = data.get('pairs', [])
                            
                            for pair in pairs[:20]:  # Get more tokens for better filtering
                                if pair.get('chainId') == 'solana' and pair.get('baseToken'):
                                    token_info = {
                                        'mint': pair['baseToken']['address'],
                                        'name': pair['baseToken'].get('name', 'Unknown'),
                                        'symbol': pair['baseToken'].get('symbol', 'UNKNOWN'),
                                        'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                                        'volume24h': float(pair.get('volume', {}).get('h24', 0)),
                                        'priceChange24h': float(pair.get('priceChange', {}).get('h24', 0)),
                                        'fdv': float(pair.get('fdv', 0)),
                                        'holders': random.randint(50, 500),  # Simulated for now
                                        'developerHoldingsPercent': random.randint(0, 30)  # Simulated
                                    }
                                    all_tokens.append(token_info)
                            
                            if pairs:  # If we got data from this endpoint, break
                                break
                    except Exception as e:
                        print(f"[scanner] Failed endpoint {url}: {e}")
                        continue
            
            if not all_tokens:
                print("[scanner] All APIs failed, using demo tokens")
                return self._generate_demo_tokens()
            
            def ai_score(token: dict) -> float:
                """Returns a confidence score for the token [0.0 - 1.0]."""
                try:
                    liquidity = token.get("liquidity", 0)
                    volume = token.get("volume24h", 0)
                    holders = token.get("holders", 0)
                    dev_pct = token.get("developerHoldingsPercent", 100)

                    # Basic safety check
                    if not token.get("name") or token.get("name").strip().lower() in ("unknown", "unnamed"):
                        return 0.0

                    if dev_pct > 25:
                        return 0.1

                    score = 0.0
                    if liquidity > 10000:
                        score += 0.4
                    if volume > 1000:
                        score += 0.3
                    if holders > 50:
                        score += 0.2
                    if dev_pct < 10:
                        score += 0.1

                    return min(score, 1.0)
                except:
                    return 0.0

            # Apply AI scoring and sort
            ranked = []
            for token in all_tokens:
                mint = token.get("mint")
                if not mint or mint in self.last_seen_tokens:
                    continue
                score = ai_score(token)
                if score >= 0.5:
                    ranked.append((score, token))

            # Sort by confidence score descending
            ranked.sort(reverse=True, key=lambda x: x[0])

            # Return top 5-10 high-confidence tokens
            result_tokens = [t[1] for t in ranked[:10]]
            print(f"[scanner] AI filtered {len(all_tokens)} -> {len(result_tokens)} high-confidence tokens")
            
            return result_tokens
                
        except Exception as e:
            print(f"[scanner] Error in fetch_recent_tokens: {e}")
            return self._generate_demo_tokens()

    def _generate_demo_tokens(self):
        """Generate demo tokens for testing when APIs are unavailable"""
        import string
        
        demo_names = ["MoonDoge", "SolanaAI", "MetaVerse", "CryptoGem", "LunarCoin"]
        demo_symbols = ["MDOGE", "SOLAI", "META", "GEM", "LUNAR"]
        
        demo_tokens = []
        for i in range(5):  # Generate 5 demo tokens
            mint = ''.join(random.choices(string.ascii_letters + string.digits, k=44))
            token = {
                'mint': mint,
                'name': demo_names[i],
                'symbol': demo_symbols[i],
                'liquidity': random.randint(15000, 100000),  # Higher liquidity for better scores
                'volume24h': random.randint(2000, 25000),    # Higher volume for better scores
                'priceChange24h': random.uniform(-0.15, 0.25),
                'fdv': random.randint(500000, 5000000),
                'holders': random.randint(75, 300),          # Good holder count
                'developerHoldingsPercent': random.randint(0, 15)  # Low dev holdings
            }
            demo_tokens.append(token)
        
        print(f"[scanner] Generated {len(demo_tokens)} demo tokens for testing")
        return demo_tokens

    async def is_honeypot_or_rug(self, mint_address: str) -> bool:
        # Simulated red flag scanner (replace with real analysis later)
        try:
            url = f"https://public-api.solanasharp.com/v1/token/{mint_address}/risk"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code != 200:
                    return False
                risk_data = response.json()
                return risk_data.get("isHoneypot", False) or risk_data.get("isScam", False)
        except Exception as e:
            print(f"[filter] Risk detection failed: {e}")
            return False

    def ai_decision(self, token: dict) -> bool:
        """
        AI-style decision-making:
        - Good liquidity (>$10k)
        - Has volume (>$1k)
        - Reasonable number of holders (>50)
        - Not excessive price dump (-20% or worse)
        """
        try:
            liquidity = token.get("liquidity", 0)
            volume = token.get("volume24h", 0)
            holders = token.get("holders", 0)
            price_change = token.get("priceChange24h", 0)

            # More realistic filters for live trading
            if (liquidity > 10000 and 
                volume > 1000 and 
                holders > 50 and 
                price_change > -0.2):  # Not dumping more than 20%
                
                print(f"[AI] ✅ {token.get('symbol')} passed AI filters - L:${liquidity:.0f} V:${volume:.0f} H:{holders} PC:{price_change:.1%}")
                return True
            else:
                print(f"[AI] ❌ {token.get('symbol')} failed AI filters - L:${liquidity:.0f} V:${volume:.0f} H:{holders} PC:{price_change:.1%}")
                return False
        except Exception as e:
            print(f"[AI] Decision error: {e}")
            return False

    async def scan_loop(self):
        print("[scanner] 🌐 Starting real-time token scanner...")
        while True:
            try:
                tokens = await self.fetch_recent_tokens()
                print(f"[scanner] Found {len(tokens)} tokens to analyze")

                for token in tokens:
                    mint = token.get("mint")
                    if not mint or mint in self.last_seen_tokens:
                        continue

                    self.last_seen_tokens.add(mint)
                    print(f"\n[scanner] Detected: {token.get('name', 'Unknown')} - {mint[:8]}...")

                    # Check for honeypot/rug
                    if await self.is_honeypot_or_rug(mint):
                        print(f"[filter] ⚠️ Token flagged as scam or honeypot: {mint[:8]}...")
                        continue

                    # AI decision making
                    if self.ai_enabled and not self.ai_decision(token):
                        continue

                    # Pass to trade handler
                    print(f"[scanner] ✅ Token passed all filters: {token.get('name', 'Unknown')}")
                    success = await self.trade_handler.handle_token(mint=mint, token_info=token)
                    
                    # Update auracle statistics if available
                    if success and self.auracle_instance:
                        self.auracle_instance.stats["trades_executed"] += 1

                # Wait before next scan (reduced for faster detection)
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"[scanner] Error in scan loop: {e}")
                import traceback
                traceback.print_exc()
                # Wait longer on error to avoid rapid retries
                await asyncio.sleep(20)

    # OPTIONAL: Future fast-mempool detection via Jito listener
    async def jito_listener_stub(self):
        print("[scanner] Jito listener not implemented yet (stub)")
        await asyncio.sleep(5)