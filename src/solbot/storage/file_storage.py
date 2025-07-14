"""
File-based storage system to replace database dependency.
Provides the same interface as the database module but stores data in JSON files.
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class FileStorage:
    def __init__(self, storage_dir: str = "data/storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize storage files
        self.files = {
            'priv_keys': self.storage_dir / 'priv_keys.json',
            'referrals': self.storage_dir / 'referrals.json',
            'fees': self.storage_dir / 'fees.json',
            'volumes': self.storage_dir / 'volumes.json',
            'rewards': self.storage_dir / 'rewards.json',
            'orders': self.storage_dir / 'orders.json',
            'hot_tokens': self.storage_dir / 'hot_tokens.json',
            'strategies': self.storage_dir / 'strategies.json',
            'watchlists': self.storage_dir / 'watchlists.json',
        }
        
        # Initialize empty files if they don't exist
        for file_path in self.files.values():
            if not file_path.exists():
                self._save_data(file_path, {})
    
    def _load_data(self, file_path: Path) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, file_path: Path, data: Dict[str, Any]) -> None:
        """Save data to JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {e}")
    
    # Private key management
    def store_priv_key(self, tg_id: int, priv_key: str) -> None:
        """Store encrypted private key for user"""
        data = self._load_data(self.files['priv_keys'])
        data[str(tg_id)] = priv_key
        self._save_data(self.files['priv_keys'], data)
    
    def get_priv_key(self, tg_id: int) -> Optional[str]:
        """Get private key for user"""
        data = self._load_data(self.files['priv_keys'])
        return data.get(str(tg_id))
    
    def delete_priv_key(self, tg_id: int) -> None:
        """Delete private key for user"""
        data = self._load_data(self.files['priv_keys'])
        if str(tg_id) in data:
            del data[str(tg_id)]
            self._save_data(self.files['priv_keys'], data)
    
    # Referral system
    def set_referral(self, tg_id: int, referrer_id: int) -> None:
        """Set referral relationship"""
        if tg_id != referrer_id:
            data = self._load_data(self.files['referrals'])
            data[str(tg_id)] = referrer_id
            self._save_data(self.files['referrals'], data)
    
    def get_referral_list(self, id_list: List[int]) -> List[int]:
        """Get list of users who were referred by the given users"""
        data = self._load_data(self.files['referrals'])
        result = []
        for tg_id, referrer_id in data.items():
            if referrer_id in id_list:
                result.append(int(tg_id))
        return result
    
    # Fee configuration
    def get_fee_tip_info(self, tg_id: int) -> Tuple[str, str]:
        """Get fee and tip info for user"""
        data = self._load_data(self.files['fees'])
        user_data = data.get(str(tg_id), {"fee": 2, "tip": 2})  # Default to STANDARD
        return user_data.get("fee", 2), user_data.get("tip", 2)
    
    def update_fee_info(self, tg_id: int, fee: int) -> Tuple[str, str]:
        """Update fee info for user"""
        data = self._load_data(self.files['fees'])
        if str(tg_id) not in data:
            data[str(tg_id)] = {"fee": fee, "tip": 2}
        else:
            data[str(tg_id)]["fee"] = fee
        self._save_data(self.files['fees'], data)
        return self.get_fee_tip_info(tg_id)
    
    def update_tip_info(self, tg_id: int, tip: int) -> Tuple[str, str]:
        """Update tip info for user"""
        data = self._load_data(self.files['fees'])
        if str(tg_id) not in data:
            data[str(tg_id)] = {"fee": 2, "tip": tip}
        else:
            data[str(tg_id)]["tip"] = tip
        self._save_data(self.files['fees'], data)
        return self.get_fee_tip_info(tg_id)
    
    # Volume tracking
    def store_trading_volume_info(self, tg_id: int, amount: float) -> None:
        """Store trading volume for user"""
        data = self._load_data(self.files['volumes'])
        if str(tg_id) not in data:
            data[str(tg_id)] = []
        data[str(tg_id)].append({
            "amount": amount,
            "timestamp": json.dumps(None)  # Simplified for now
        })
        self._save_data(self.files['volumes'], data)
    
    # Order management
    def get_token_order(self, tg_id: int, token_address: str) -> List[List[Any]]:
        """Get token orders for user"""
        data = self._load_data(self.files['orders'])
        user_orders = data.get(str(tg_id), {})
        token_orders = user_orders.get(token_address, [])
        
        # Return 8 empty order slots if no orders exist
        if not token_orders:
            return [[0, 0, 0, 0] for _ in range(8)]
        
        return token_orders
    
    def get_token_order_list(self, tg_id: int) -> List[str]:
        """Get list of tokens with orders for user"""
        data = self._load_data(self.files['orders'])
        user_orders = data.get(str(tg_id), {})
        return sorted(user_orders.keys())
    
    def get_order(self, tg_id: int, token: str, order_id: int) -> Tuple[float, float]:
        """Get specific order details"""
        data = self._load_data(self.files['orders'])
        user_orders = data.get(str(tg_id), {})
        token_orders = user_orders.get(token, [])
        
        if order_id < len(token_orders) and len(token_orders[order_id]) >= 4:
            return token_orders[order_id][2], token_orders[order_id][3]  # price, amount
        return 0.0, 0.0
    
    def delete_all_orders(self, tg_id: int, token_address: str) -> None:
        """Delete all orders for a token"""
        data = self._load_data(self.files['orders'])
        user_orders = data.get(str(tg_id), {})
        if token_address in user_orders:
            del user_orders[token_address]
            data[str(tg_id)] = user_orders
            self._save_data(self.files['orders'], data)
    
    def delete_order(self, tg_id: int, token_address: str, order_id: int) -> None:
        """Delete specific order"""
        data = self._load_data(self.files['orders'])
        user_orders = data.get(str(tg_id), {})
        token_orders = user_orders.get(token_address, [])
        
        if order_id < len(token_orders):
            token_orders[order_id] = [0, 0, 0, 0]
            user_orders[token_address] = token_orders
            data[str(tg_id)] = user_orders
            self._save_data(self.files['orders'], data)
    
    # Order type specific updates
    def _update_order(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Generic order update method"""
        data = self._load_data(self.files['orders'])
        if str(tg_id) not in data:
            data[str(tg_id)] = {}
        
        user_orders = data[str(tg_id)]
        if token_address not in user_orders:
            user_orders[token_address] = [[0, 0, 0, 0] for _ in range(8)]
        
        # Ensure we have enough slots
        while len(user_orders[token_address]) <= order_id:
            user_orders[token_address].append([0, 0, 0, 0])
        
        user_orders[token_address][order_id] = [order_id + 1, tg_id, price, amount]
        self._save_data(self.files['orders'], data)
    
    def sell_for_profit_order_update(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update sell for profit order"""
        self._update_order(tg_id, token_address, order_id, price, amount)
    
    def sell_for_loss_order_update(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update sell for loss order"""
        self._update_order(tg_id, token_address, order_id, price, amount)
    
    def buy_higher_order_update(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update buy higher order"""
        self._update_order(tg_id, token_address, order_id, price, amount)
    
    def buy_lower_order_update(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update buy lower order"""
        self._update_order(tg_id, token_address, order_id, price, amount)
    
    # Hot token management
    def add_hot_token(self, tg_id: int, token: str) -> bool:
        """Add hot token for user"""
        data = self._load_data(self.files['hot_tokens'])
        data[str(tg_id)] = token
        self._save_data(self.files['hot_tokens'], data)
        return True
    
    def remove_hot_token(self, tg_id: int, token: str) -> bool:
        """Remove hot token for user"""
        data = self._load_data(self.files['hot_tokens'])
        if str(tg_id) in data and data[str(tg_id)] == token:
            del data[str(tg_id)]
            self._save_data(self.files['hot_tokens'], data)
            return True
        return False
    
    def check_hot_token(self, tg_id: int, token: str) -> bool:
        """Check if token is hot for user"""
        data = self._load_data(self.files['hot_tokens'])
        return data.get(str(tg_id)) == token
    
    # Strategy/preset management
    def check_preset(self, tg_id: int) -> Optional[Tuple]:
        """Check preset strategy for user"""
        data = self._load_data(self.files['strategies'])
        strategy = data.get(str(tg_id))
        if strategy:
            return tuple(strategy.values())
        # Return default preset
        return (tg_id, None, 5.0, 25.0, 10.0, 50.0, 15.0, 75.0, 20.0, 100.0)
    
    def update_preset(self, tg_id: int, price0: float, amount0: float, price1: float, amount1: float,
                     price2: float, amount2: float, price3: float, amount3: float) -> None:
        """Update preset strategy"""
        data = self._load_data(self.files['strategies'])
        data[str(tg_id)] = {
            "price0": price0, "amount0": amount0,
            "price1": price1, "amount1": amount1,
            "price2": price2, "amount2": amount2,
            "price3": price3, "amount3": amount3
        }
        self._save_data(self.files['strategies'], data)
    
    def apply_preset(self, tg_id: int, token: str) -> Optional[Tuple]:
        """Apply preset strategy to token"""
        try:
            # This would need token price - for now return defaults
            return (1.0, 25.0, 1.1, 50.0, 1.2, 75.0, 0.9, 100.0)
        except Exception:
            logger.exception("Failed to apply preset")
            return None
    
    def update_as_preset_sell_for_profit(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update preset sell for profit order"""
        self.sell_for_profit_order_update(tg_id, token_address, order_id, price, amount)
    
    def update_as_preset_sell_for_loss(self, tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
        """Update preset sell for loss order"""
        self.sell_for_loss_order_update(tg_id, token_address, order_id, price, amount)
    
    # Watchlist management
    def add_watch_list(self, tg_id: int, token: str) -> None:
        """Add token to watchlist"""
        data = self._load_data(self.files['watchlists'])
        if str(tg_id) not in data:
            data[str(tg_id)] = []
        if token not in data[str(tg_id)]:
            data[str(tg_id)].append(token)
        self._save_data(self.files['watchlists'], data)
    
    def remove_watch_list(self, tg_id: int, token: str) -> None:
        """Remove token from watchlist"""
        data = self._load_data(self.files['watchlists'])
        if str(tg_id) in data and token in data[str(tg_id)]:
            data[str(tg_id)].remove(token)
            self._save_data(self.files['watchlists'], data)
    
    def get_watch_list(self, tg_id: int) -> Optional[List[str]]:
        """Get watchlist for user"""
        data = self._load_data(self.files['watchlists'])
        return data.get(str(tg_id))
    
    # Reward system stubs (simplified)
    def get_level_one_info(self, tg_id: int) -> Tuple[float, int]:
        """Get level one referral info"""
        return 0.0, 0
    
    def get_level_two_info(self, tg_id: int) -> Tuple[float, Any, float, float, int]:
        """Get level two referral info"""
        return 0.0, None, 0.0, 0.0, 0

# Global instance
_storage = None

def get_storage() -> FileStorage:
    """Get the global storage instance"""
    global _storage
    if _storage is None:
        _storage = FileStorage()
    return _storage

# Database compatibility functions
def connect_db():
    """Initialize storage (compatibility function)"""
    get_storage()

def get_priv_key(tg_id: int) -> Optional[str]:
    return get_storage().get_priv_key(tg_id)

def delete_priv_key(tg_id: int) -> None:
    get_storage().delete_priv_key(tg_id)

def set_referral(tg_id: int, referrer_id: int) -> None:
    get_storage().set_referral(tg_id, referrer_id)

def get_referral_list(id_list: List[int]) -> List[int]:
    return get_storage().get_referral_list(id_list)

def get_fee_tip_info(tg_id: int) -> Tuple[str, str]:
    return get_storage().get_fee_tip_info(tg_id)

def update_fee_info(tg_id: int, fee: int) -> Tuple[str, str]:
    return get_storage().update_fee_info(tg_id, fee)

def update_tip_info(tg_id: int, tip: int) -> Tuple[str, str]:
    return get_storage().update_tip_info(tg_id, tip)

def store_trading_volume_info(tg_id: int, amount: float) -> None:
    get_storage().store_trading_volume_info(tg_id, amount)

def get_token_order(tg_id: int, token_address: str) -> List[List[Any]]:
    return get_storage().get_token_order(tg_id, token_address)

def get_token_order_list(tg_id: int) -> List[str]:
    return get_storage().get_token_order_list(tg_id)

def get_order(tg_id: int, token: str, order_id: int) -> Tuple[float, float]:
    return get_storage().get_order(tg_id, token, order_id)

def delete_all_orders(tg_id: int, token_address: str) -> None:
    get_storage().delete_all_orders(tg_id, token_address)

def delete_order(tg_id: int, token_address: str, order_id: int) -> None:
    get_storage().delete_order(tg_id, token_address, order_id)

def sell_for_profit_order_update(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().sell_for_profit_order_update(tg_id, token_address, order_id, price, amount)

def sell_for_loss_order_update(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().sell_for_loss_order_update(tg_id, token_address, order_id, price, amount)

def buy_higher_order_update(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().buy_higher_order_update(tg_id, token_address, order_id, price, amount)

def buy_lower_order_update(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().buy_lower_order_update(tg_id, token_address, order_id, price, amount)

def add_hot_token(tg_id: int, token: str) -> bool:
    return get_storage().add_hot_token(tg_id, token)

def remove_hot_token(tg_id: int, token: str) -> bool:
    return get_storage().remove_hot_token(tg_id, token)

def check_hot_token(tg_id: int, token: str) -> bool:
    return get_storage().check_hot_token(tg_id, token)

def check_preset(tg_id: int) -> Optional[Tuple]:
    return get_storage().check_preset(tg_id)

def update_preset(tg_id: int, price0: float, amount0: float, price1: float, amount1: float,
                 price2: float, amount2: float, price3: float, amount3: float) -> None:
    get_storage().update_preset(tg_id, price0, amount0, price1, amount1, price2, amount2, price3, amount3)

def apply_preset(tg_id: int, token: str) -> Optional[Tuple]:
    return get_storage().apply_preset(tg_id, token)

def update_as_preset_sell_for_profit(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().update_as_preset_sell_for_profit(tg_id, token_address, order_id, price, amount)

def update_as_preset_sell_for_loss(tg_id: int, token_address: str, order_id: int, price: float, amount: float) -> None:
    get_storage().update_as_preset_sell_for_loss(tg_id, token_address, order_id, price, amount)

def add_watch_list(tg_id: int, token: str) -> None:
    get_storage().add_watch_list(tg_id, token)

def remove_watch_list(tg_id: int, token: str) -> None:
    get_storage().remove_watch_list(tg_id, token)

def get_watch_list(tg_id: int) -> Optional[List[str]]:
    return get_storage().get_watch_list(tg_id)

def get_level_one_info(tg_id: int) -> Tuple[float, int]:
    return get_storage().get_level_one_info(tg_id)

def get_level_two_info(tg_id: int) -> Tuple[float, Any, float, float, int]:
    return get_storage().get_level_two_info(tg_id)

# Additional compatibility functions
def encode_string(data: str) -> str:
    """Encode string for storage"""
    import base64
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def decode_password(encoded_text: str, password: str) -> str:
    """Decode password from storage"""
    try:
        import base64
        base64_bytes = encoded_text.encode('utf-8')
        message_bytes = base64.b64decode(base64_bytes)
        decoded_str = message_bytes.decode('utf-8')
        main_str = decoded_str[len('dog') if decoded_str.startswith('dog') else 0 : -len(password) if decoded_str.endswith(password) else None].strip()
        return main_str[::-1]
    except Exception:
        return ''