"""
Strategy Loader
===============

Dynamically loads and manages trading strategies from the strategies/ directory.
"""

import os
import importlib.util
import inspect
from typing import Dict, List, Type
from strategies.base_strategy import BaseStrategy


class StrategyLoader:
    """Loads and manages trading strategies dynamically."""
    
    def __init__(self, strategies_dir: str = "strategies"):
        """
        Initialize the strategy loader.
        
        Args:
            strategies_dir: Directory containing strategy files
        """
        self.strategies_dir = strategies_dir
        self.loaded_strategies: Dict[str, Type[BaseStrategy]] = {}
        self.strategy_instances: Dict[str, BaseStrategy] = {}
    
    def load_all_strategies(self) -> Dict[str, Type[BaseStrategy]]:
        """
        Load all strategy classes from the strategies directory.
        
        Returns:
            Dictionary mapping strategy names to strategy classes
        """
        self.loaded_strategies.clear()
        
        if not os.path.exists(self.strategies_dir):
            return {}
        
        for filename in os.listdir(self.strategies_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                strategy_path = os.path.join(self.strategies_dir, filename)
                module_name = filename[:-3]  # Remove .py extension
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(module_name, strategy_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find strategy classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseStrategy) and 
                            obj != BaseStrategy):
                            self.loaded_strategies[obj.get_strategy_name(obj)] = obj
                            
                except Exception as e:
                    print(f"Warning: Failed to load strategy from {filename}: {e}")
        
        return self.loaded_strategies
    
    def get_strategy(self, strategy_name: str, params: Dict = None) -> BaseStrategy:
        """
        Get an instance of a specific strategy.
        
        Args:
            strategy_name: Name of the strategy to load
            params: Parameters to pass to the strategy
            
        Returns:
            Strategy instance
        """
        if strategy_name not in self.loaded_strategies:
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {list(self.loaded_strategies.keys())}")
        
        strategy_class = self.loaded_strategies[strategy_name]
        instance_key = f"{strategy_name}_{id(params) if params else 'default'}"
        
        if instance_key not in self.strategy_instances:
            self.strategy_instances[instance_key] = strategy_class(params)
        
        return self.strategy_instances[instance_key]
    
    def list_available_strategies(self) -> List[Dict[str, str]]:
        """
        List all available strategies with their descriptions.
        
        Returns:
            List of dictionaries with strategy info
        """
        strategies = []
        for name, strategy_class in self.loaded_strategies.items():
            # Create a temporary instance to get description
            temp_instance = strategy_class()
            strategies.append({
                'name': name,
                'description': temp_instance.get_strategy_description(),
                'required_indicators': temp_instance.get_required_indicators(),
                'timeframe_requirements': temp_instance.get_timeframe_requirements()
            })
        return strategies
    
    def reload_strategies(self) -> int:
        """
        Reload all strategies from disk.
        
        Returns:
            Number of strategies loaded
        """
        self.strategy_instances.clear()
        self.load_all_strategies()
        return len(self.loaded_strategies)
    
    def validate_strategy_file(self, filepath: str) -> bool:
        """
        Validate that a strategy file follows the correct format.
        
        Args:
            filepath: Path to the strategy file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Load the module
            spec = importlib.util.spec_from_file_location("temp_strategy", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for BaseStrategy subclass
            strategy_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseStrategy) and 
                    obj != BaseStrategy):
                    strategy_classes.append(obj)
            
            if not strategy_classes:
                return False
            
            # Validate that the strategy implements required methods
            strategy_class = strategy_classes[0]
            temp_instance = strategy_class()
            
            # Check required methods exist and are callable
            required_methods = ['generate_signals', 'get_strategy_name', 'get_strategy_description']
            for method in required_methods:
                if not hasattr(temp_instance, method) or not callable(getattr(temp_instance, method)):
                    return False
            
            return True
            
        except Exception:
            return False