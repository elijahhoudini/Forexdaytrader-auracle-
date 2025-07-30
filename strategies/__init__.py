"""
AURACLE Strategy Engine
======================

This module provides the base interface for creating modular trading strategies.
Users can add custom Python files under strategies/ with a standard format.

All strategies must inherit from the BaseStrategy class and implement the required methods.
"""

from .base_strategy import BaseStrategy
from .strategy_loader import StrategyLoader

__all__ = ['BaseStrategy', 'StrategyLoader']