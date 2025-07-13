import time
from scanner import TokenScanner
from trade import TradeHandler
from risk import RiskEvaluator
from logger import AuracleLogger
from wallet import Wallet

class Auracle:
    def __init__(self):
        self.wallet = Wallet()
        self.scanner = TokenScanner()
        self.risk = RiskEvaluator()
        self.trade = TradeHandler(self.wallet)
        self.logger = AuracleLogger()
        self.loop_interval = 30
        self.buy_amount_sol = 0.025
        self.symbol_anomaly_log = "data/anomalies.txt"

    def log_status(self, msg):
        print(f"[AURACLE] {msg}")
        self.logger.log_system(msg)

    def detect_symbol_anomaly(self, symbol):
        # Look for suspicious or placeholder-style symbols
        if not symbol or symbol.strip() == "" or len(symbol) < 3:
            return True
        if any(char in symbol for char in ["?", "#", "$", "%", ".", " "]):
            return True
        return False

    def log_anomaly(self, token):
        with open(self.symbol_anomaly_log, "a") as f:
            f.write(f"{time.ctime()} | Suspicious Symbol: {token.get('symbol', '?')} — {token['mint']}\n")

    def run(self):
        self.log_status("Launching AURACLE — Hardened Phase Directive Active")
        while True:
            try:
                new_tokens = self.scanner.scan()
                self.log_status(f"Scanned {len(new_tokens)} tokens")

                for token in new_tokens:
                    symbol = token.get("symbol", "???")
                    mint = token["mint"]

                    if self.detect_symbol_anomaly(symbol):
                        self.log_status(f"[⚠️ ANOMALY DETECTED] {symbol} — logging")
                        self.log_anomaly(token)

                    if self.risk.is_blacklisted(mint):
                        self.logger.log_flag(mint, reason="Blacklist")
                        continue

                    if self.risk.is_suspicious(token):
                        self.logger.log_flag(mint, reason="Suspicious token detected")
                        continue

                    if not self.trade.should_buy(token):
                        self.log_status(f"Skipped {symbol} — Did not meet buy criteria")
                        continue

                    success = self.trade.buy_token(token, self.buy_amount_sol)

                    if success:
                        self.logger.log_trade("BUY", token, self.buy_amount_sol)
                    else:
                        self.logger.log_trade("BUY_FAILED", token, 0)

                self.trade.monitor_positions()
                time.sleep(self.loop_interval)

            except Exception as e:
                self.logger.log_error(str(e))
                self.log_status(f"ERROR — {str(e)}")
                time.sleep(10)

if __name__ == "__main__":
    bot = Auracle()
    bot.run()
