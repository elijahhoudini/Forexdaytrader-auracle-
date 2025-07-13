"""
AURACLE Risk Evaluator Module
============================

Enhanced risk assessment and fraud detection for token analysis.
Features advanced safety checks and ML-style risk scoring.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class RiskEvaluator:
    """
    Enhanced risk evaluation system with advanced fraud detection.
    
    Features:
    - Multi-factor risk scoring
    - Blacklist management
    - Honeypot detection patterns
    - Developer behavior analysis
    - Liquidity stability checks
    """
    
    def __init__(self):
        self.blacklist = set()
        self.whitelist = set()
        self.risk_cache = {}  # Cache risk evaluations
        self.cache_ttl = 300  # 5 minutes cache
        
        # Risk thresholds
        self.MIN_LIQUIDITY = 5000
        self.MIN_HOLDERS = 50
        self.MAX_DEV_HOLDINGS = 25
        self.MIN_VOLUME_RATIO = 0.1  # Volume/Liquidity ratio
        
        # Fraud detection patterns
        self.suspicious_patterns = [
            "PEPE", "DOGE", "SHIB", "MOON", "SAFE", "BABY", "MINI", 
            "ELONMUSK", "TESLA", "TWITTER", "META", "GOOGLE", "APPLE",
            "PUMP", "DUMP", "SCAM", "RUG", "HONEYPOT"
        ]
        
        print("✅ Enhanced RiskEvaluator initialized - Advanced safety checks enabled")

    def evaluate(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced risk evaluation with comprehensive safety checks.
        
        Args:
            token (Dict): Token data
            
        Returns:
            Dict: Risk assessment with safety flag and detailed scoring
        """
        try:
            mint = token.get("mint", "")
            
            # Check cache first
            if mint in self.risk_cache:
                cached_result, cache_time = self.risk_cache[mint]
                if time.time() - cache_time < self.cache_ttl:
                    return cached_result
            
            # Start with neutral risk score
            risk_score = 0.5
            risk_flags = []
            
            # Check whitelist first
            if mint in self.whitelist:
                result = {"safe": True, "score": 0.9, "reason": "Whitelisted token"}
                self.risk_cache[mint] = (result, time.time())
                return result
            
            # Check blacklist
            if mint in self.blacklist:
                result = {"safe": False, "score": 0.0, "reason": "Blacklisted token"}
                self.risk_cache[mint] = (result, time.time())
                return result
            
            # 1. Basic token property checks
            liquidity = token.get("liquidity", 0)
            holders = token.get("holders", 0)
            volume = token.get("volume24h", 0)
            dev_holdings = token.get("developerHoldingsPercent", 0)
            price_change = token.get("priceChange24h", 0)
            
            # 2. Critical safety checks
            if liquidity < self.MIN_LIQUIDITY:
                risk_flags.append("Low liquidity")
                risk_score -= 0.3
            
            if holders < self.MIN_HOLDERS:
                risk_flags.append("Too few holders")
                risk_score -= 0.2
            
            if dev_holdings > self.MAX_DEV_HOLDINGS:
                risk_flags.append("High developer holdings")
                risk_score -= 0.4
            
            # 3. Volume/liquidity ratio check
            if liquidity > 0:
                volume_ratio = volume / liquidity
                if volume_ratio < self.MIN_VOLUME_RATIO:
                    risk_flags.append("Low volume ratio")
                    risk_score -= 0.1
                elif volume_ratio > 5.0:  # Suspiciously high volume
                    risk_flags.append("Suspiciously high volume")
                    risk_score -= 0.2
            
            # 4. Price manipulation detection
            if abs(price_change) > 0.5:  # More than 50% change
                risk_flags.append("High price volatility")
                risk_score -= 0.1
            
            # 5. Name-based fraud detection
            symbol = token.get("symbol", "").upper()
            name = token.get("name", "").upper()
            
            for pattern in self.suspicious_patterns:
                if pattern in symbol or pattern in name:
                    risk_flags.append(f"Suspicious name pattern: {pattern}")
                    risk_score -= 0.3
                    break
            
            # 6. Token age estimation (simplified)
            # In a real implementation, this would check on-chain creation time
            age_risk = self._estimate_token_age_risk(token)
            risk_score += age_risk
            
            # 7. Liquidity stability check
            stability_score = self._check_liquidity_stability(token)
            risk_score += stability_score
            
            # Normalize risk score
            risk_score = max(0.0, min(1.0, risk_score))
            
            # Final safety determination
            is_safe = risk_score >= 0.4 and len(risk_flags) == 0
            
            # Add to blacklist if very risky
            if risk_score < 0.2:
                self.blacklist.add(mint)
                print(f"[risk] ⚠️ Token {mint[:8]}... added to blacklist - Risk score: {risk_score:.2f}")
            
            result = {
                "safe": is_safe,
                "score": risk_score,
                "flags": risk_flags,
                "reason": "Risk assessment completed"
            }
            
            # Cache result
            self.risk_cache[mint] = (result, time.time())
            
            return result
            
        except Exception as e:
            print(f"[risk] Error evaluating token: {e}")
            return {"safe": False, "score": 0.0, "reason": f"Evaluation error: {str(e)}"}

    def _estimate_token_age_risk(self, token: Dict[str, Any]) -> float:
        """
        Estimate token age risk based on available data.
        Newer tokens are riskier.
        """
        try:
            # This is a simplified implementation
            # In reality, we'd check the token's creation timestamp on-chain
            
            # For now, use a simple heuristic based on holder count
            holders = token.get("holders", 0)
            
            if holders > 1000:
                return 0.1  # Likely older token
            elif holders > 500:
                return 0.05  # Medium age
            elif holders > 100:
                return 0.0  # Neutral
            else:
                return -0.1  # Likely very new token
                
        except:
            return 0.0

    def _check_liquidity_stability(self, token: Dict[str, Any]) -> float:
        """
        Check liquidity stability patterns.
        """
        try:
            liquidity = token.get("liquidity", 0)
            volume = token.get("volume24h", 0)
            
            # Good liquidity-to-volume ratio indicates stability
            if liquidity > 0 and volume > 0:
                ratio = volume / liquidity
                if 0.2 <= ratio <= 2.0:  # Healthy range
                    return 0.1
                elif ratio < 0.1:  # Very low activity
                    return -0.05
                else:  # High activity might indicate manipulation
                    return -0.1
            
            return 0.0
            
        except:
            return 0.0

    def add_to_blacklist(self, mint: str, reason: str = "Manual"):
        """Add token to blacklist"""
        self.blacklist.add(mint)
        print(f"[risk] Added {mint[:8]}... to blacklist - Reason: {reason}")

    def add_to_whitelist(self, mint: str, reason: str = "Manual"):
        """Add token to whitelist"""
        self.whitelist.add(mint)
        print(f"[risk] Added {mint[:8]}... to whitelist - Reason: {reason}")

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk evaluation summary"""
        return {
            "blacklisted_tokens": len(self.blacklist),
            "whitelisted_tokens": len(self.whitelist),
            "cached_evaluations": len(self.risk_cache),
            "risk_thresholds": {
                "min_liquidity": self.MIN_LIQUIDITY,
                "min_holders": self.MIN_HOLDERS,
                "max_dev_holdings": self.MAX_DEV_HOLDINGS
            }
        }

    def clear_cache(self):
        """Clear risk evaluation cache"""
        self.risk_cache.clear()
        print("[risk] Risk evaluation cache cleared")

    def cleanup_expired_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            mint for mint, (_, cache_time) in self.risk_cache.items() 
            if current_time - cache_time > self.cache_ttl
        ]
        
        for mint in expired_keys:
            del self.risk_cache[mint]
        
        if expired_keys:
            print(f"[risk] Cleaned up {len(expired_keys)} expired cache entries")
            return {"safe": False, "reason": f"Evaluation error: {e}"}

    def add_to_blacklist(self, mint: str):
        """Add token to blacklist"""
        self.blacklist.add(mint)
        print(f"[risk] Added {mint[:8]}... to blacklist")