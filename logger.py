"""
AURACLE Logger Module
====================

Comprehensive logging system for trades, errors, and system events.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any


class AuracleLogger:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()

        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)

        print("[SYSTEM] AURACLE Logger initialized")

    def log_system(self, message: str, data: Dict[str, Any] = None):
        """Log system events"""
        try:
            log_entry = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "data": data or {},
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
            }

            # Append to system logs
            self._append_to_file("data/system_logs.json", log_entry)

        except Exception as e:
            print(f"[logger] Error logging system event: {e}")

    def log_trade(self, action: str, token: Dict[str, Any], amount: float):
        """Log trading activities"""
        try:
            log_entry = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "token_mint": token.get("mint", ""),
                "token_symbol": token.get("symbol", ""),
                "amount_sol": amount,
                "token_data": token
            }

            self._append_to_file("data/trade_logs.json", log_entry)

        except Exception as e:
            print(f"[logger] Error logging trade: {e}")

    def log_error(self, message: str, error_data: Dict[str, Any] = None):
        """Log errors and exceptions"""
        try:
            log_entry = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "error_message": message,
                "error_data": error_data or {}
            }

            self._append_to_file("data/error_logs.json", log_entry)

        except Exception as e:
            print(f"[logger] Error logging error: {e}")

    def log_flag(self, mint: str, reason: str, token_data: Dict[str, Any]):
        """Log flagged tokens and suspicious activity"""
        try:
            log_entry = {
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat(),
                "flagged_mint": mint,
                "flag_reason": reason,
                "token_data": token_data
            }

            self._append_to_file("data/flag_logs.json", log_entry)

        except Exception as e:
            print(f"[logger] Error logging flag: {e}")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds()
        }

    def _append_to_file(self, filepath: str, data: Dict[str, Any]):
        """Append data to JSON file"""
        try:
            # Read existing data
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    existing_data = json.load(f)
            else:
                existing_data = []

            # Append new data
            existing_data.append(data)

            # Write back to file
            with open(filepath, 'w') as f:
                json.dump(existing_data, f, indent=2)

        except Exception as e:
            print(f"[logger] Error writing to {filepath}: {e}")