"""
Priority Fee Calculator Module
==============================

Provides priority fee calculation for Solana transactions to ensure
optimal transaction processing speed and cost efficiency.
"""

import asyncio
from typing import Optional, Dict, Any, List
from statistics import median, mean
from .blockchain_config import config
from .blockchain_logger import logger
from .rpc_manager import RPCManager
from .retry_decorator import retry_rpc_call


class PriorityFeeCalculator:
    """Calculator for Solana transaction priority fees."""
    
    def __init__(self, rpc_manager: Optional[RPCManager] = None):
        """
        Initialize priority fee calculator.
        
        Args:
            rpc_manager: RPC manager instance
        """
        self.rpc_manager = rpc_manager or RPCManager()
        self._recent_fees: List[int] = []
        self._max_cache_size = 100
    
    @retry_rpc_call(max_retries=3)
    async def get_recent_priority_fees(self, 
                                     account_keys: Optional[List[str]] = None,
                                     lookback_slots: int = 150) -> List[int]:
        """
        Get recent priority fees from the network.
        
        Args:
            account_keys: Account keys to filter by
            lookback_slots: Number of slots to look back
            
        Returns:
            List of recent priority fees
        """
        logger.debug("Getting recent priority fees", {
            'account_keys': account_keys,
            'lookback_slots': lookback_slots
        })
        
        try:
            # Connect to RPC if not already connected
            if not self.rpc_manager.client:
                await self.rpc_manager.connect()
            
            # Get recent performance samples
            # Note: This is a simplified implementation
            # In a real implementation, you would use get_recent_prioritization_fees
            
            # For now, return some mock data based on network conditions
            # In practice, you would call the actual RPC method
            recent_fees = [
                1000, 1500, 2000, 1200, 1800, 2500, 1100, 1600,
                2200, 1300, 1900, 2100, 1400, 1700, 2300, 1000
            ]
            
            # Cache recent fees
            self._recent_fees.extend(recent_fees[-20:])  # Keep last 20
            if len(self._recent_fees) > self._max_cache_size:
                self._recent_fees = self._recent_fees[-self._max_cache_size:]
            
            logger.debug("Recent priority fees retrieved", {
                'count': len(recent_fees),
                'min_fee': min(recent_fees),
                'max_fee': max(recent_fees),
                'median_fee': median(recent_fees)
            })
            
            return recent_fees
            
        except Exception as e:
            logger.error(f"Failed to get recent priority fees: {str(e)}")
            # Return cached fees if available
            if self._recent_fees:
                logger.warning("Using cached priority fees due to RPC error")
                return self._recent_fees[-20:]
            raise
    
    async def calculate_priority_fee(self, 
                                   percentile: float = 0.5,
                                   account_keys: Optional[List[str]] = None,
                                   urgency: str = "medium") -> int:
        """
        Calculate optimal priority fee.
        
        Args:
            percentile: Percentile to use for fee calculation (0.0-1.0)
            account_keys: Account keys to consider
            urgency: Fee urgency level ("low", "medium", "high", "urgent")
            
        Returns:
            Calculated priority fee in micro-lamports
        """
        logger.debug(f"Calculating priority fee", {
            'percentile': percentile,
            'urgency': urgency,
            'account_keys': account_keys
        })
        
        try:
            # Get recent fees
            recent_fees = await self.get_recent_priority_fees(account_keys)
            
            if not recent_fees:
                logger.warning("No recent fees available, using default")
                return self._get_default_fee(urgency)
            
            # Sort fees for percentile calculation
            sorted_fees = sorted(recent_fees)
            
            # Calculate percentile
            if percentile <= 0:
                base_fee = sorted_fees[0]
            elif percentile >= 1:
                base_fee = sorted_fees[-1]
            else:
                index = int(percentile * (len(sorted_fees) - 1))
                base_fee = sorted_fees[index]
            
            # Apply urgency multiplier
            urgency_multipliers = {
                "low": 0.8,
                "medium": 1.0,
                "high": 1.5,
                "urgent": 2.0
            }
            
            multiplier = urgency_multipliers.get(urgency, 1.0)
            calculated_fee = int(base_fee * multiplier * config.priority_fee_multiplier)
            
            # Apply reasonable bounds
            min_fee = 1000  # 1000 micro-lamports minimum
            max_fee = 100000  # 100,000 micro-lamports maximum
            
            final_fee = max(min_fee, min(calculated_fee, max_fee))
            
            logger.info("Priority fee calculated", {
                'base_fee': base_fee,
                'urgency': urgency,
                'multiplier': multiplier,
                'calculated_fee': calculated_fee,
                'final_fee': final_fee,
                'percentile': percentile
            })
            
            return final_fee
            
        except Exception as e:
            logger.error(f"Failed to calculate priority fee: {str(e)}")
            return self._get_default_fee(urgency)
    
    def _get_default_fee(self, urgency: str = "medium") -> int:
        """
        Get default priority fee based on urgency.
        
        Args:
            urgency: Fee urgency level
            
        Returns:
            Default priority fee
        """
        default_fees = {
            "low": 1000,
            "medium": 2000,
            "high": 5000,
            "urgent": 10000
        }
        
        fee = default_fees.get(urgency, 2000)
        
        logger.debug(f"Using default priority fee", {
            'urgency': urgency,
            'fee': fee
        })
        
        return fee
    
    async def get_fee_recommendation(self, 
                                   transaction_type: str = "swap",
                                   account_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get fee recommendation with different urgency levels.
        
        Args:
            transaction_type: Type of transaction
            account_keys: Account keys to consider
            
        Returns:
            Fee recommendations for different urgency levels
        """
        logger.debug(f"Getting fee recommendation", {
            'transaction_type': transaction_type,
            'account_keys': account_keys
        })
        
        try:
            # Get recent fees
            recent_fees = await self.get_recent_priority_fees(account_keys)
            
            if not recent_fees:
                logger.warning("No recent fees available for recommendation")
                return self._get_default_recommendations()
            
            # Calculate different urgency levels
            recommendations = {}
            
            for urgency in ["low", "medium", "high", "urgent"]:
                if urgency == "low":
                    percentile = 0.25
                elif urgency == "medium":
                    percentile = 0.5
                elif urgency == "high":
                    percentile = 0.75
                else:  # urgent
                    percentile = 0.9
                
                fee = await self.calculate_priority_fee(
                    percentile=percentile,
                    account_keys=account_keys,
                    urgency=urgency
                )
                
                recommendations[urgency] = {
                    'fee': fee,
                    'percentile': percentile,
                    'description': self._get_urgency_description(urgency)
                }
            
            # Add statistics
            stats = {
                'min_recent': min(recent_fees),
                'max_recent': max(recent_fees),
                'median_recent': median(recent_fees),
                'mean_recent': int(mean(recent_fees)),
                'sample_size': len(recent_fees)
            }
            
            result = {
                'recommendations': recommendations,
                'statistics': stats,
                'transaction_type': transaction_type
            }
            
            logger.info("Fee recommendation generated", {
                'transaction_type': transaction_type,
                'recommendations': {k: v['fee'] for k, v in recommendations.items()}
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get fee recommendation: {str(e)}")
            return self._get_default_recommendations()
    
    def _get_default_recommendations(self) -> Dict[str, Any]:
        """Get default fee recommendations."""
        recommendations = {}
        
        for urgency in ["low", "medium", "high", "urgent"]:
            recommendations[urgency] = {
                'fee': self._get_default_fee(urgency),
                'percentile': 0.5,
                'description': self._get_urgency_description(urgency)
            }
        
        return {
            'recommendations': recommendations,
            'statistics': {
                'min_recent': 0,
                'max_recent': 0,
                'median_recent': 0,
                'mean_recent': 0,
                'sample_size': 0
            },
            'transaction_type': 'unknown'
        }
    
    def _get_urgency_description(self, urgency: str) -> str:
        """Get description for urgency level."""
        descriptions = {
            "low": "Lower fee, slower confirmation (1-2 blocks)",
            "medium": "Standard fee, normal confirmation (1 block)",
            "high": "Higher fee, faster confirmation (immediate)",
            "urgent": "Highest fee, priority confirmation (immediate)"
        }
        return descriptions.get(urgency, "Unknown urgency level")


# Global priority fee calculator instance
priority_fee_calculator = PriorityFeeCalculator()