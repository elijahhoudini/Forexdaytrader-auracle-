"""
Retry Decorator Module
======================

Provides retry functionality for blockchain operations with exponential backoff
and customizable retry conditions.
"""

import time
import random
from functools import wraps
from typing import Callable, Optional, Union, List, Type, Any
from .blockchain_logger import logger


def retry_decorator(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Optional[Union[Type[Exception], List[Type[Exception]]]] = None,
    on_retry: Optional[Callable] = None,
    on_failure: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter to delays
        exceptions: Exception types to retry on (default: all exceptions)
        on_retry: Callback function called on each retry
        on_failure: Callback function called on final failure
    """
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry this exception
                    if exceptions is not None:
                        if isinstance(exceptions, (list, tuple)):
                            if not any(isinstance(e, exc_type) for exc_type in exceptions):
                                raise
                        elif not isinstance(e, exceptions):
                            raise
                    
                    # If this is the last attempt, raise the exception
                    if attempt == max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} retries", {
                            'function': func.__name__,
                            'attempts': attempt + 1,
                            'final_error': str(e)
                        })
                        if on_failure:
                            on_failure(e, attempt + 1)
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (exponential_base ** attempt), max_delay)
                    
                    # Add jitter if enabled
                    if jitter:
                        delay = delay * (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Function {func.__name__} failed, retrying in {delay:.2f}s", {
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'max_retries': max_retries,
                        'delay': delay,
                        'error': str(e)
                    })
                    
                    if on_retry:
                        on_retry(e, attempt + 1, delay)
                    
                    time.sleep(delay)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator


# Specialized retry decorators for common blockchain operations
def retry_rpc_call(max_retries: int = 5, initial_delay: float = 0.5):
    """Retry decorator specifically for RPC calls."""
    return retry_decorator(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=30.0,
        exceptions=(ConnectionError, TimeoutError, Exception),
        on_retry=lambda e, attempt, delay: logger.debug(f"RPC call failed, retry {attempt}")
    )


def retry_transaction(max_retries: int = 3, initial_delay: float = 2.0):
    """Retry decorator specifically for transaction operations."""
    return retry_decorator(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=60.0,
        exceptions=(ConnectionError, TimeoutError, Exception),
        on_retry=lambda e, attempt, delay: logger.warning(f"Transaction failed, retry {attempt}")
    )


def retry_api_call(max_retries: int = 4, initial_delay: float = 1.0):
    """Retry decorator specifically for API calls."""
    return retry_decorator(
        max_retries=max_retries,
        initial_delay=initial_delay,
        max_delay=45.0,
        exceptions=(ConnectionError, TimeoutError, Exception),
        on_retry=lambda e, attempt, delay: logger.debug(f"API call failed, retry {attempt}")
    )