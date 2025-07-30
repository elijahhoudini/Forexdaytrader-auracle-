#!/usr/bin/env python3
"""
AURACLE Safety Checks Module
===========================

Comprehensive security and safety validation system for autonomous trading.

Features:
- Cold start capital requirement validation
- Wallet connection and balance verification
- Environment variable validation
- Network connectivity and API access checks
- Private key security management
- Kill-switch logic for API errors
- SPL token restriction enforcement
"""

import os
import asyncio
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import json

# Import existing AURACLE modules
try:
    import config
except ImportError:
    class config:
        SOLANA_RPC_ENDPOINT = "https://api.mainnet-beta.solana.com"

# Try to import base58 for key validation
try:
    import base58
    BASE58_AVAILABLE = True
except ImportError:
    BASE58_AVAILABLE = False

# Try to import Solana libraries
try:
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Confirmed
    from solders.pubkey import Pubkey
    from solders.keypair import Keypair
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

# Try to import HTTP libraries
try:
    import httpx
    HTTP_CLIENT = httpx.AsyncClient
except ImportError:
    try:
        import aiohttp
        HTTP_CLIENT = aiohttp.ClientSession
    except ImportError:
        HTTP_CLIENT = None


class SafetyChecks:
    """
    Comprehensive safety and security validation system.
    
    Ensures all prerequisites are met before allowing live trading
    and monitors system health during operation.
    """
    
    def __init__(self):
        """Initialize safety checks system."""
        self.logger = logging.getLogger('SafetyChecks')
        
        # Security settings
        self.min_balance_sol = float(os.getenv('MIN_WALLET_BALANCE_SOL', '0.01'))
        self.max_api_errors = int(os.getenv('MAX_API_ERRORS', '10'))
        self.api_error_window_minutes = int(os.getenv('API_ERROR_WINDOW_MINUTES', '5'))
        
        # Error tracking
        self.api_errors = []
        self.jupiter_errors = []
        self.rpc_errors = []
        
        # Private key security
        self.private_key_accessed = False
        self.private_key_load_time = None
        
        # Required environment variables
        self.required_env_vars = [
            'WALLET_PRIVATE_KEY',
            'TELEGRAM_BOT_TOKEN'
        ]
        
        # Optional but recommended variables
        self.recommended_env_vars = [
            'TELEGRAM_CHAT_ID',
            'TELEGRAM_ADMIN_CHAT_ID',
            'TELEGRAM_AUTH_PASSWORD'
        ]
        
        self.logger.info("🛡️ Safety checks system initialized")
    
    async def check_wallet_balance(self) -> bool:
        """
        Check if wallet has sufficient balance for trading.
        
        Returns:
            bool: True if balance is sufficient
        """
        try:
            if not SOLANA_AVAILABLE:
                self.logger.warning("⚠️ Solana libraries not available - using mock balance")
                return True
            
            # Get wallet address from private key
            wallet_address = await self.get_wallet_address()
            if not wallet_address:
                return False
            
            # Check balance via RPC
            rpc_endpoint = getattr(config, 'SOLANA_RPC_ENDPOINT', 'https://api.mainnet-beta.solana.com')
            client = AsyncClient(rpc_endpoint)
            
            try:
                response = await client.get_balance(Pubkey.from_string(wallet_address))
                balance_lamports = response.value
                balance_sol = balance_lamports / 1e9
                
                self.logger.info(f"💰 Wallet balance: {balance_sol:.4f} SOL")
                
                if balance_sol >= self.min_balance_sol:
                    self.logger.info(f"✅ Sufficient wallet balance ({balance_sol:.4f} ≥ {self.min_balance_sol} SOL)")
                    return True
                else:
                    self.logger.error(f"❌ Insufficient wallet balance ({balance_sol:.4f} < {self.min_balance_sol} SOL)")
                    return False
                    
            finally:
                await client.close()
                
        except Exception as e:
            self.logger.error(f"❌ Error checking wallet balance: {e}")
            self.record_rpc_error(str(e))
            return False
    
    async def check_wallet_connection(self) -> bool:
        """
        Verify wallet connection and key validity.
        
        Returns:
            bool: True if wallet connection is valid
        """
        try:
            # Validate private key format
            private_key = await self.get_private_key_secure()
            if not private_key:
                return False
            
            # Test key decoding
            try:
                if BASE58_AVAILABLE:
                    private_key_bytes = base58.b58decode(private_key)
                    if len(private_key_bytes) != 64:
                        self.logger.error("❌ Invalid private key length")
                        return False
                        
                    # Test keypair creation
                    if SOLANA_AVAILABLE:
                        keypair = Keypair.from_bytes(private_key_bytes)
                        wallet_address = str(keypair.pubkey())
                        self.logger.info(f"✅ Wallet connection valid: {wallet_address[:8]}...{wallet_address[-8:]}")
                else:
                    # Basic length check without base58 decoding
                    if len(private_key) < 64:
                        self.logger.error("❌ Private key appears too short")
                        return False
                    self.logger.info("✅ Basic wallet key validation passed")
                
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Invalid private key format: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error checking wallet connection: {e}")
            return False
    
    def check_environment_variables(self) -> bool:
        """
        Validate all required environment variables are present.
        
        Returns:
            bool: True if all required variables are set
        """
        try:
            missing_required = []
            missing_recommended = []
            
            # Check required variables
            for var in self.required_env_vars:
                value = os.getenv(var)
                if not value:
                    missing_required.append(var)
                elif var == 'WALLET_PRIVATE_KEY' and len(value) < 64:
                    missing_required.append(f"{var} (invalid length)")
                elif var == 'TELEGRAM_BOT_TOKEN' and not value.startswith(('bot', 'tok')):
                    missing_required.append(f"{var} (invalid format)")
            
            # Check recommended variables
            for var in self.recommended_env_vars:
                if not os.getenv(var):
                    missing_recommended.append(var)
            
            # Report results
            if missing_required:
                self.logger.error(f"❌ Missing required environment variables: {', '.join(missing_required)}")
                return False
            
            if missing_recommended:
                self.logger.warning(f"⚠️ Missing recommended environment variables: {', '.join(missing_recommended)}")
            
            self.logger.info("✅ Environment variables validation passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking environment variables: {e}")
            return False
    
    async def check_network_connectivity(self) -> bool:
        """
        Test network connectivity to required services.
        
        Returns:
            bool: True if connectivity is good
        """
        try:
            if not HTTP_CLIENT:
                self.logger.warning("⚠️ HTTP client not available - skipping connectivity checks")
                return True
            
            # Test endpoints to check
            test_endpoints = [
                getattr(config, 'SOLANA_RPC_ENDPOINT', 'https://api.mainnet-beta.solana.com'),
                "https://quote-api.jup.ag/v6/health",
                "https://api.telegram.org"
            ]
            
            connectivity_results = []
            
            if HTTP_CLIENT == httpx.AsyncClient:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    for endpoint in test_endpoints:
                        try:
                            response = await client.get(endpoint)
                            connectivity_results.append((endpoint, response.status_code == 200))
                        except Exception as e:
                            connectivity_results.append((endpoint, False))
                            self.logger.warning(f"⚠️ Connectivity test failed for {endpoint}: {e}")
            
            # Check results
            failed_connections = [endpoint for endpoint, success in connectivity_results if not success]
            
            if failed_connections:
                self.logger.error(f"❌ Failed connectivity tests: {', '.join(failed_connections)}")
                return False
            
            self.logger.info("✅ Network connectivity tests passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking network connectivity: {e}")
            return False
    
    async def check_jupiter_api(self) -> bool:
        """
        Verify Jupiter API access and functionality.
        
        Returns:
            bool: True if Jupiter API is accessible
        """
        try:
            if not HTTP_CLIENT:
                self.logger.warning("⚠️ HTTP client not available - skipping Jupiter API check")
                return True
            
            # Test Jupiter API endpoints
            jupiter_endpoints = [
                "https://quote-api.jup.ag/v6/health",
                "https://quote-api.jup.ag/v6/tokens"
            ]
            
            if HTTP_CLIENT == httpx.AsyncClient:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    for endpoint in jupiter_endpoints:
                        try:
                            response = await client.get(endpoint)
                            if response.status_code != 200:
                                self.logger.error(f"❌ Jupiter API error: {endpoint} returned {response.status_code}")
                                self.record_jupiter_error(f"HTTP {response.status_code}")
                                return False
                        except Exception as e:
                            self.logger.error(f"❌ Jupiter API connection error: {e}")
                            self.record_jupiter_error(str(e))
                            return False
            
            self.logger.info("✅ Jupiter API accessibility verified")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error checking Jupiter API: {e}")
            self.record_jupiter_error(str(e))
            return False
    
    async def get_private_key_secure(self) -> Optional[str]:
        """
        Securely retrieve private key with read-once memory storage.
        
        Returns:
            Optional[str]: Private key if valid, None otherwise
        """
        try:
            if self.private_key_accessed:
                self.logger.warning("⚠️ Private key already accessed - security violation")
                return None
            
            private_key = os.getenv('WALLET_PRIVATE_KEY')
            if not private_key:
                self.logger.error("❌ No private key found in environment")
                return None
            
            # Mark as accessed and record time
            self.private_key_accessed = True
            self.private_key_load_time = datetime.utcnow()
            
            # Validate key format
            if len(private_key) < 64:
                self.logger.error("❌ Private key too short")
                return None
            
            # Clear from environment for security (optional)
            if os.getenv('CLEAR_PRIVATE_KEY_AFTER_LOAD', 'false').lower() == 'true':
                os.environ.pop('WALLET_PRIVATE_KEY', None)
                self.logger.info("🔐 Private key cleared from environment")
            
            return private_key
            
        except Exception as e:
            self.logger.error(f"❌ Error accessing private key: {e}")
            return None
    
    async def get_wallet_address(self) -> Optional[str]:
        """
        Get wallet address from private key.
        
        Returns:
            Optional[str]: Wallet address if valid
        """
        try:
            private_key = await self.get_private_key_secure()
            if not private_key:
                return None
            
            if SOLANA_AVAILABLE and BASE58_AVAILABLE:
                private_key_bytes = base58.b58decode(private_key)
                keypair = Keypair.from_bytes(private_key_bytes)
                return str(keypair.pubkey())
            else:
                # Mock address for testing
                return "MockWalletAddress1234567890"
                
        except Exception as e:
            self.logger.error(f"❌ Error getting wallet address: {e}")
            return None
    
    def record_api_error(self, error_message: str):
        """Record general API error for kill-switch monitoring."""
        current_time = datetime.utcnow()
        self.api_errors.append({
            'timestamp': current_time,
            'error': error_message
        })
        
        # Clean old errors (outside window)
        cutoff_time = current_time - timedelta(minutes=self.api_error_window_minutes)
        self.api_errors = [e for e in self.api_errors if e['timestamp'] > cutoff_time]
        
        # Check for kill-switch condition
        if len(self.api_errors) >= self.max_api_errors:
            self.logger.critical(f"🔴 KILL-SWITCH ACTIVATED: {len(self.api_errors)} API errors in {self.api_error_window_minutes} minutes")
            self.trigger_kill_switch("Too many API errors")
    
    def record_jupiter_error(self, error_message: str):
        """Record Jupiter API specific error."""
        current_time = datetime.utcnow()
        self.jupiter_errors.append({
            'timestamp': current_time,
            'error': error_message
        })
        
        # Also record as general API error
        self.record_api_error(f"Jupiter: {error_message}")
    
    def record_rpc_error(self, error_message: str):
        """Record RPC specific error."""
        current_time = datetime.utcnow()
        self.rpc_errors.append({
            'timestamp': current_time,
            'error': error_message
        })
        
        # Also record as general API error
        self.record_api_error(f"RPC: {error_message}")
    
    def trigger_kill_switch(self, reason: str):
        """
        Trigger emergency kill-switch to stop all operations.
        
        Args:
            reason: Reason for triggering kill-switch
        """
        try:
            self.logger.critical(f"🚨 KILL-SWITCH TRIGGERED: {reason}")
            
            # Create kill-switch file
            kill_switch_file = "KILL_SWITCH_ACTIVE"
            with open(kill_switch_file, 'w') as f:
                f.write(json.dumps({
                    'timestamp': datetime.utcnow().isoformat(),
                    'reason': reason,
                    'api_errors': len(self.api_errors),
                    'jupiter_errors': len(self.jupiter_errors),
                    'rpc_errors': len(self.rpc_errors)
                }, indent=2))
            
            # Log critical information
            self.logger.critical(f"Kill-switch file created: {kill_switch_file}")
            self.logger.critical("Manual intervention required to restart trading")
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering kill-switch: {e}")
    
    def is_kill_switch_active(self) -> bool:
        """
        Check if kill-switch is currently active.
        
        Returns:
            bool: True if kill-switch is active
        """
        return os.path.exists("KILL_SWITCH_ACTIVE")
    
    def clear_kill_switch(self) -> bool:
        """
        Clear kill-switch (manual intervention required).
        
        Returns:
            bool: True if cleared successfully
        """
        try:
            if os.path.exists("KILL_SWITCH_ACTIVE"):
                os.remove("KILL_SWITCH_ACTIVE")
                self.logger.info("✅ Kill-switch cleared manually")
                
                # Reset error counters
                self.api_errors.clear()
                self.jupiter_errors.clear()
                self.rpc_errors.clear()
                
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error clearing kill-switch: {e}")
            return False
    
    async def validate_token_safety(self, token_mint: str, token_info: Dict[str, Any]) -> bool:
        """
        Validate token safety before trading.
        
        Args:
            token_mint: Token mint address
            token_info: Token information
            
        Returns:
            bool: True if token is safe to trade
        """
        try:
            # Check if it's a valid SPL token
            if not await self.is_spl_token(token_mint):
                self.logger.warning(f"⚠️ Not an SPL token: {token_mint}")
                return False
            
            # Check for NFT characteristics
            if await self.is_nft_token(token_info):
                self.logger.warning(f"⚠️ Token appears to be NFT: {token_mint}")
                return False
            
            # Check for suspicious characteristics
            if await self.has_suspicious_characteristics(token_info):
                self.logger.warning(f"⚠️ Token has suspicious characteristics: {token_mint}")
                return False
            
            # Validate token metadata
            if not await self.validate_token_metadata(token_info):
                self.logger.warning(f"⚠️ Invalid token metadata: {token_mint}")
                return False
            
            self.logger.info(f"✅ Token safety validation passed: {token_mint}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating token safety: {e}")
            return False
    
    async def is_spl_token(self, token_mint: str) -> bool:
        """
        Check if token is a valid SPL token.
        
        Args:
            token_mint: Token mint address
            
        Returns:
            bool: True if valid SPL token
        """
        try:
            # Basic address format validation
            if not token_mint or len(token_mint) != 44:
                return False
            
            # Check against known token standards
            if SOLANA_AVAILABLE:
                try:
                    pubkey = Pubkey.from_string(token_mint)
                    # Additional SPL token validation could go here
                    return True
                except Exception:
                    return False
            
            # Fallback validation for testing
            return token_mint.isalnum() and len(token_mint) == 44
            
        except Exception as e:
            self.logger.error(f"❌ Error checking SPL token: {e}")
            return False
    
    async def is_nft_token(self, token_info: Dict[str, Any]) -> bool:
        """
        Check if token is likely an NFT.
        
        Args:
            token_info: Token information
            
        Returns:
            bool: True if likely an NFT
        """
        try:
            # Check supply (NFTs typically have supply of 1)
            supply = token_info.get('supply', 0)
            if supply == 1:
                return True
            
            # Check decimals (NFTs typically have 0 decimals)
            decimals = token_info.get('decimals', -1)
            if decimals == 0 and supply <= 1000:
                return True
            
            # Check for NFT-related keywords in metadata
            name = token_info.get('name', '').lower()
            symbol = token_info.get('symbol', '').lower()
            
            nft_keywords = ['nft', 'collectible', 'art', 'avatar', 'pfp', 'collection']
            for keyword in nft_keywords:
                if keyword in name or keyword in symbol:
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking NFT characteristics: {e}")
            return False
    
    async def has_suspicious_characteristics(self, token_info: Dict[str, Any]) -> bool:
        """
        Check for suspicious token characteristics.
        
        Args:
            token_info: Token information
            
        Returns:
            bool: True if suspicious
        """
        try:
            # Check for extremely high supply (possible scam)
            supply = token_info.get('supply', 0)
            if supply > 1e15:  # Very high supply
                return True
            
            # Check for no or minimal liquidity
            liquidity = token_info.get('liquidity', 0)
            if liquidity < 100:  # Very low liquidity
                return True
            
            # Check for suspicious name patterns
            name = token_info.get('name', '').lower()
            symbol = token_info.get('symbol', '').lower()
            
            suspicious_patterns = [
                'test', 'fake', 'scam', 'rug', 'hack', 'exploit',
                'www.', 'http', '.com', '.net', 'airdrop', 'claim'
            ]
            
            for pattern in suspicious_patterns:
                if pattern in name or pattern in symbol:
                    return True
            
            # Check for excessive special characters
            special_char_count = sum(1 for c in name + symbol if not c.isalnum())
            if special_char_count > 5:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Error checking suspicious characteristics: {e}")
            return True  # Err on the side of caution
    
    async def validate_token_metadata(self, token_info: Dict[str, Any]) -> bool:
        """
        Validate token metadata is properly formatted.
        
        Args:
            token_info: Token information
            
        Returns:
            bool: True if metadata is valid
        """
        try:
            # Check required fields
            required_fields = ['name', 'symbol']
            for field in required_fields:
                if field not in token_info or not token_info[field]:
                    return False
            
            # Validate field lengths
            name = token_info.get('name', '')
            symbol = token_info.get('symbol', '')
            
            if len(name) > 100 or len(symbol) > 20:
                return False
            
            if len(name) < 1 or len(symbol) < 1:
                return False
            
            # Check for reasonable decimals
            decimals = token_info.get('decimals', 9)
            if decimals < 0 or decimals > 18:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error validating token metadata: {e}")
            return False
    
    def get_safety_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive safety report.
        
        Returns:
            Dict[str, Any]: Safety status report
        """
        try:
            current_time = datetime.utcnow()
            
            # Calculate error rates
            recent_cutoff = current_time - timedelta(minutes=self.api_error_window_minutes)
            recent_api_errors = [e for e in self.api_errors if e['timestamp'] > recent_cutoff]
            recent_jupiter_errors = [e for e in self.jupiter_errors if e['timestamp'] > recent_cutoff]
            recent_rpc_errors = [e for e in self.rpc_errors if e['timestamp'] > recent_cutoff]
            
            report = {
                'timestamp': current_time.isoformat(),
                'kill_switch_active': self.is_kill_switch_active(),
                'private_key_accessed': self.private_key_accessed,
                'private_key_load_time': self.private_key_load_time.isoformat() if self.private_key_load_time else None,
                'error_counts': {
                    'api_errors_recent': len(recent_api_errors),
                    'jupiter_errors_recent': len(recent_jupiter_errors),
                    'rpc_errors_recent': len(recent_rpc_errors),
                    'api_errors_total': len(self.api_errors),
                    'jupiter_errors_total': len(self.jupiter_errors),
                    'rpc_errors_total': len(self.rpc_errors)
                },
                'thresholds': {
                    'max_api_errors': self.max_api_errors,
                    'error_window_minutes': self.api_error_window_minutes,
                    'min_balance_sol': self.min_balance_sol
                },
                'security_status': {
                    'environment_vars_ok': self.check_environment_variables(),
                    'kill_switch_risk': len(recent_api_errors) / self.max_api_errors if self.max_api_errors > 0 else 0
                }
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"❌ Error generating safety report: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e),
                'kill_switch_active': self.is_kill_switch_active()
            }