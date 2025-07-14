"""
AURACLE Risk Evaluator Module
============================

Risk assessment and fraud detection for token analysis.
"""

import time
from typing import Dict, Any, List
import config


class RiskEvaluator:
    def __init__(self):
        self.blacklist = set()
        self.risk_patterns = [
            # Common scam patterns
            "scam", "fake", "test", "rug", "honey", "dump", "pump",
            # Suspicious patterns
            "moon", "gem", "100x", "1000x", "safe", "legit",
            # Common bot patterns
            "bot", "automated", "ai", "smart"
        ]
        print("✅ RiskEvaluator initialized - Advanced safety checks enabled")

    def evaluate(self, token: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive risk evaluation for a given token

        Returns:
            Dict with 'safe' boolean and detailed risk assessment
        """
        try:
            mint = token.get("mint", "")
            symbol = token.get("symbol", "").lower()
            name = token.get("name", "").lower()

            # Check blacklist
            if mint in self.blacklist:
                return {"safe": False, "reason": "Blacklisted token"}

            # Check basic token properties
            liquidity = token.get("liquidity", 0)
            holders = token.get("holders", 0)
            dev_holdings = token.get("developerHoldingsPercent", 0)
            volume = token.get("volume24h", 0)
            price_change = token.get("priceChange24h", 0)

            # Enhanced risk assessment
            risk_score = 0
            reasons = []

            # Liquidity checks
            if liquidity < config.MIN_LIQUIDITY_THRESHOLD:
                risk_score += 30
                reasons.append(f"Low liquidity: ${liquidity:,.0f}")

            # Holder distribution checks
            if holders < 20:
                risk_score += 25
                reasons.append(f"Too few holders: {holders}")

            # Developer holdings check
            if dev_holdings > 30:
                risk_score += 35
                reasons.append(f"High dev holdings: {dev_holdings}%")

            # Volume/liquidity ratio check
            if liquidity > 0 and volume / liquidity < 0.01:
                risk_score += 15
                reasons.append("Low volume/liquidity ratio")

            # Price volatility check
            if abs(price_change) > 50:
                risk_score += 20
                reasons.append(f"High volatility: {price_change:.1f}%")

            # Pattern matching for suspicious names/symbols
            for pattern in self.risk_patterns:
                if pattern in symbol or pattern in name:
                    risk_score += 25
                    reasons.append(f"Suspicious pattern: {pattern}")
                    break

            # Age check (if available)
            created_at = token.get("created_at", 0)
            if created_at > 0:
                age_hours = (time.time() - created_at) / 3600
                if age_hours < 1:  # Less than 1 hour old
                    risk_score += 30
                    reasons.append(f"Very new token: {age_hours:.1f}h old")

            # Calculate final safety verdict
            is_safe = risk_score < 50  # Risk score threshold
            
            # Additional safety requirements
            if is_safe:
                # Must meet minimum requirements
                if liquidity < config.MIN_LIQUIDITY_THRESHOLD:
                    is_safe = False
                if holders < 10:
                    is_safe = False
                if dev_holdings > 50:
                    is_safe = False

            result = {
                "safe": is_safe,
                "risk_score": risk_score,
                "reasons": reasons,
                "liquidity": liquidity,
                "holders": holders,
                "dev_holdings": dev_holdings
            }

            if not is_safe:
                result["reason"] = "; ".join(reasons) if reasons else "High risk score"

            return result

        except Exception as e:
            print(f"[risk] Error evaluating token: {e}")
            return {"safe": False, "reason": f"Evaluation error: {e}"}

    def add_to_blacklist(self, mint: str, reason: str = "Manual blacklist"):
        """Add token to blacklist with reason"""
        self.blacklist.add(mint)
        print(f"[risk] Added {mint[:8]}... to blacklist - {reason}")

    def is_blacklisted(self, mint: str) -> bool:
        """Check if token is blacklisted"""
        return mint in self.blacklist

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get risk evaluator summary"""
        return {
            "blacklisted_tokens": len(self.blacklist),
            "risk_patterns": len(self.risk_patterns),
            "safety_checks": [
                "Liquidity validation",
                "Holder distribution",
                "Developer holdings",
                "Volume/liquidity ratio",
                "Price volatility",
                "Pattern matching",
                "Token age verification"
            ]
        }

    def update_risk_patterns(self, new_patterns: List[str]):
        """Update risk patterns for enhanced detection"""
        self.risk_patterns.extend(new_patterns)
        print(f"[risk] Updated risk patterns, now monitoring {len(self.risk_patterns)} patterns")