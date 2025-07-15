"""
Blockchain Logger Module
=========================

Provides structured logging for blockchain operations with different
log levels and formatting for better debugging and monitoring.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class BlockchainLogger:
    """Enhanced logger for blockchain operations."""
    
    def __init__(self, 
                 name: str = "blockchain",
                 log_file: Optional[str] = None,
                 log_level: str = "INFO"):
        """
        Initialize the blockchain logger.
        
        Args:
            name: Logger name
            log_file: Optional file path for logging
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log debug message."""
        self.logger.debug(self._format_message(message, extra))
    
    def info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log info message."""
        self.logger.info(self._format_message(message, extra))
    
    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log warning message."""
        self.logger.warning(self._format_message(message, extra))
    
    def error(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log error message."""
        self.logger.error(self._format_message(message, extra))
    
    def critical(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """Log critical message."""
        self.logger.critical(self._format_message(message, extra))
    
    def transaction_start(self, tx_signature: str, operation: str):
        """Log transaction start."""
        self.info(f"Transaction {operation} started", {
            'tx_signature': tx_signature,
            'operation': operation,
            'timestamp': datetime.now().isoformat()
        })
    
    def transaction_success(self, tx_signature: str, operation: str, 
                          result: Optional[Dict[str, Any]] = None):
        """Log transaction success."""
        self.info(f"Transaction {operation} succeeded", {
            'tx_signature': tx_signature,
            'operation': operation,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
    
    def transaction_error(self, tx_signature: str, operation: str, 
                         error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log transaction error."""
        self.error(f"Transaction {operation} failed: {str(error)}", {
            'tx_signature': tx_signature,
            'operation': operation,
            'error': str(error),
            'error_type': type(error).__name__,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
    
    def rpc_request(self, method: str, params: Optional[Dict[str, Any]] = None):
        """Log RPC request."""
        self.debug(f"RPC Request: {method}", {
            'method': method,
            'params': params,
            'timestamp': datetime.now().isoformat()
        })
    
    def rpc_response(self, method: str, success: bool, 
                    response: Optional[Dict[str, Any]] = None):
        """Log RPC response."""
        level = "debug" if success else "error"
        getattr(self, level)(f"RPC Response: {method}", {
            'method': method,
            'success': success,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })
    
    def _format_message(self, message: str, extra: Optional[Dict[str, Any]] = None) -> str:
        """Format message with extra context."""
        if extra:
            extra_str = " | ".join([f"{k}={v}" for k, v in extra.items()])
            return f"{message} | {extra_str}"
        return message


# Global logger instance
logger = BlockchainLogger()