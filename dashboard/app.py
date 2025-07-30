"""
AURACLE Forex Dashboard
======================

Local Flask-powered dashboard for real-time monitoring and control
of the AURACLE Forex trading system.

Features:
- Real-time positions and P&L display
- Trading logs browser
- Manual trade override controls  
- Performance charts
- Risk metrics monitoring
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time


class AuracleDashboard:
    """Flask-based web dashboard for AURACLE Forex trading."""
    
    def __init__(self, config: Dict):
        """
        Initialize the dashboard.
        
        Args:
            config: Dashboard configuration
        """
        self.config = config
        self.app = Flask(__name__, 
                        template_folder='dashboard/templates',
                        static_folder='dashboard/static')
        CORS(self.app)
        
        # Configuration
        self.port = config.get('port', 5000)
        self.host = config.get('host', '127.0.0.1')
        self.debug = config.get('debug', False)
        
        # Data storage
        self.data_dir = config.get('data_dir', 'data')
        self.positions = {}
        self.trades_history = []
        self.risk_metrics = {}
        self.performance_data = {}
        
        # Setup routes
        self._setup_routes()
        
        # Start background data updater
        self.update_thread = threading.Thread(target=self._update_data_loop, daemon=True)
        self.running = False
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status."""
            return jsonify({
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'mode': 'forex_only'
            })
        
        @self.app.route('/api/positions')
        def api_positions():
            """Get current positions."""
            return jsonify(self.positions)
        
        @self.app.route('/api/trades')
        def api_trades():
            """Get trades history."""
            limit = request.args.get('limit', 100, type=int)
            return jsonify(self.trades_history[-limit:])
        
        @self.app.route('/api/risk')
        def api_risk():
            """Get risk metrics."""
            return jsonify(self.risk_metrics)
        
        @self.app.route('/api/performance')
        def api_performance():
            """Get performance data."""
            return jsonify(self.performance_data)
        
        @self.app.route('/api/logs')
        def api_logs():
            """Get system logs."""
            log_type = request.args.get('type', 'all')
            limit = request.args.get('limit', 50, type=int)
            
            logs = self._get_logs(log_type, limit)
            return jsonify(logs)
        
        @self.app.route('/api/close_position', methods=['POST'])
        def api_close_position():
            """Close a specific position."""
            data = request.get_json()
            position_id = data.get('position_id')
            
            if position_id in self.positions:
                # Signal to close position (would integrate with trading engine)
                result = self._signal_close_position(position_id)
                return jsonify(result)
            else:
                return jsonify({'error': 'Position not found'}), 404
        
        @self.app.route('/api/manual_trade', methods=['POST'])
        def api_manual_trade():
            """Execute manual trade."""
            data = request.get_json()
            
            # Validate trade data
            required_fields = ['pair', 'direction', 'size']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Signal manual trade (would integrate with trading engine)
            result = self._signal_manual_trade(data)
            return jsonify(result)
        
        @self.app.route('/api/strategy_status')
        def api_strategy_status():
            """Get strategy status."""
            return jsonify({
                'active_strategies': self._get_active_strategies(),
                'loaded_strategies': self._get_loaded_strategies(),
                'last_signal_time': self._get_last_signal_time()
            })
        
        @self.app.route('/dashboard/charts/<chart_type>')
        def serve_charts(chart_type):
            """Serve chart images."""
            charts_dir = os.path.join(self.data_dir, 'backtests')
            return send_from_directory(charts_dir, f'{chart_type}.png')
    
    def _update_data_loop(self):
        """Background thread to update dashboard data."""
        while self.running:
            try:
                self._update_positions()
                self._update_trades_history()
                self._update_risk_metrics()
                self._update_performance_data()
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Dashboard update error: {e}")
                time.sleep(10)
    
    def _update_positions(self):
        """Update current positions data."""
        try:
            # Load from risk manager state
            state_file = os.path.join(self.data_dir, 'risk_manager_state.json')
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    state = json.load(f)
                    self.positions = state.get('positions', {})
        except Exception as e:
            print(f"Error updating positions: {e}")
    
    def _update_trades_history(self):
        """Update trades history."""
        try:
            # Load from trade logs
            trades_file = os.path.join(self.data_dir, 'trade_logs.json')
            if os.path.exists(trades_file):
                with open(trades_file, 'r') as f:
                    self.trades_history = json.load(f)
        except Exception as e:
            print(f"Error updating trades history: {e}")
    
    def _update_risk_metrics(self):
        """Update risk metrics."""
        try:
            # Calculate current risk metrics
            total_unrealized_pnl = 0
            margin_used = 0
            
            for position in self.positions.values():
                # Calculate unrealized P&L (simplified)
                if 'unrealized_pnl' in position:
                    total_unrealized_pnl += position['unrealized_pnl']
                
                # Calculate margin used (simplified)
                margin_used += position.get('size', 0) * 1000  # Simplified calculation
            
            self.risk_metrics = {
                'total_positions': len(self.positions),
                'total_unrealized_pnl': total_unrealized_pnl,
                'margin_used': margin_used,
                'free_margin': 10000 - margin_used,  # Simplified
                'daily_trades': self._get_daily_trades_count(),
                'daily_pnl': self._get_daily_pnl(),
                'max_drawdown': self._get_max_drawdown(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error updating risk metrics: {e}")
    
    def _update_performance_data(self):
        """Update performance data."""
        try:
            # Load recent performance data
            performance_file = os.path.join(self.data_dir, 'performance_logs.json')
            if os.path.exists(performance_file):
                with open(performance_file, 'r') as f:
                    performance_logs = json.load(f)
                    
                    # Calculate performance metrics
                    total_trades = len(self.trades_history)
                    winning_trades = len([t for t in self.trades_history if t.get('pnl', 0) > 0])
                    
                    self.performance_data = {
                        'total_trades': total_trades,
                        'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                        'total_pnl': sum(t.get('pnl', 0) for t in self.trades_history),
                        'best_trade': max((t.get('pnl', 0) for t in self.trades_history), default=0),
                        'worst_trade': min((t.get('pnl', 0) for t in self.trades_history), default=0),
                        'avg_trade_duration': self._calculate_avg_duration(),
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Error updating performance data: {e}")
    
    def _get_logs(self, log_type: str, limit: int) -> List[Dict]:
        """Get system logs."""
        logs = []
        
        try:
            if log_type in ['all', 'trades']:
                # Trade logs
                for trade in self.trades_history[-limit:]:
                    logs.append({
                        'timestamp': trade.get('timestamp', ''),
                        'type': 'trade',
                        'level': 'info',
                        'message': f"Trade {trade.get('direction', '')} {trade.get('pair', '')} - P&L: ${trade.get('pnl', 0):.2f}"
                    })
            
            if log_type in ['all', 'errors']:
                # Error logs
                error_log_file = os.path.join(self.data_dir, 'error_logs.json')
                if os.path.exists(error_log_file):
                    with open(error_log_file, 'r') as f:
                        error_logs = json.load(f)
                        for error in error_logs[-limit:]:
                            logs.append({
                                'timestamp': error.get('timestamp', ''),
                                'type': 'error',
                                'level': 'error',
                                'message': error.get('message', '')
                            })
            
            # Sort by timestamp
            logs.sort(key=lambda x: x['timestamp'], reverse=True)
            
        except Exception as e:
            print(f"Error getting logs: {e}")
        
        return logs[:limit]
    
    def _signal_close_position(self, position_id: str) -> Dict:
        """Signal to close a position."""
        # This would integrate with the actual trading engine
        # For now, just log the request
        signal_file = os.path.join(self.data_dir, 'dashboard_signals.json')
        
        signal = {
            'type': 'close_position',
            'position_id': position_id,
            'timestamp': datetime.now().isoformat(),
            'source': 'dashboard'
        }
        
        try:
            signals = []
            if os.path.exists(signal_file):
                with open(signal_file, 'r') as f:
                    signals = json.load(f)
            
            signals.append(signal)
            
            with open(signal_file, 'w') as f:
                json.dump(signals, f, indent=2)
            
            return {'success': True, 'message': 'Close position signal sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _signal_manual_trade(self, trade_data: Dict) -> Dict:
        """Signal a manual trade."""
        # This would integrate with the actual trading engine
        signal_file = os.path.join(self.data_dir, 'dashboard_signals.json')
        
        signal = {
            'type': 'manual_trade',
            'trade_data': trade_data,
            'timestamp': datetime.now().isoformat(),
            'source': 'dashboard'
        }
        
        try:
            signals = []
            if os.path.exists(signal_file):
                with open(signal_file, 'r') as f:
                    signals = json.load(f)
            
            signals.append(signal)
            
            with open(signal_file, 'w') as f:
                json.dump(signals, f, indent=2)
            
            return {'success': True, 'message': 'Manual trade signal sent'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_active_strategies(self) -> List[str]:
        """Get list of active strategies."""
        # This would integrate with the strategy loader
        return ['RSI_MACD_Combo']  # Placeholder
    
    def _get_loaded_strategies(self) -> List[str]:
        """Get list of loaded strategies."""
        strategies_dir = 'strategies'
        loaded = []
        
        if os.path.exists(strategies_dir):
            for filename in os.listdir(strategies_dir):
                if filename.endswith('.py') and not filename.startswith('_'):
                    loaded.append(filename[:-3])  # Remove .py extension
        
        return loaded
    
    def _get_last_signal_time(self) -> str:
        """Get timestamp of last trading signal."""
        # This would integrate with the trading engine
        return datetime.now().isoformat()  # Placeholder
    
    def _get_daily_trades_count(self) -> int:
        """Get count of trades today."""
        today = datetime.now().date()
        count = 0
        
        for trade in self.trades_history:
            trade_date_str = trade.get('timestamp', '')
            try:
                trade_date = datetime.fromisoformat(trade_date_str.replace('Z', '+00:00')).date()
                if trade_date == today:
                    count += 1
            except:
                continue
        
        return count
    
    def _get_daily_pnl(self) -> float:
        """Get today's P&L."""
        today = datetime.now().date()
        daily_pnl = 0.0
        
        for trade in self.trades_history:
            trade_date_str = trade.get('timestamp', '')
            try:
                trade_date = datetime.fromisoformat(trade_date_str.replace('Z', '+00:00')).date()
                if trade_date == today:
                    daily_pnl += trade.get('pnl', 0)
            except:
                continue
        
        return daily_pnl
    
    def _get_max_drawdown(self) -> float:
        """Get maximum drawdown."""
        # This would be calculated from equity curve
        return 0.0  # Placeholder
    
    def _calculate_avg_duration(self) -> str:
        """Calculate average trade duration."""
        if not self.trades_history:
            return "0h 0m"
        
        total_duration = timedelta(0)
        count = 0
        
        for trade in self.trades_history:
            if 'entry_time' in trade and 'exit_time' in trade:
                try:
                    entry = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
                    exit = datetime.fromisoformat(trade['exit_time'].replace('Z', '+00:00'))
                    total_duration += exit - entry
                    count += 1
                except:
                    continue
        
        if count == 0:
            return "0h 0m"
        
        avg_duration = total_duration / count
        hours = int(avg_duration.total_seconds() // 3600)
        minutes = int((avg_duration.total_seconds() % 3600) // 60)
        
        return f"{hours}h {minutes}m"
    
    def start(self):
        """Start the dashboard server."""
        self.running = True
        self.update_thread.start()
        
        print(f"🌐 Starting AURACLE Dashboard on http://{self.host}:{self.port}")
        self.app.run(host=self.host, port=self.port, debug=self.debug)
    
    def stop(self):
        """Stop the dashboard server."""
        self.running = False


def create_dashboard(config: Dict = None) -> AuracleDashboard:
    """
    Create a new dashboard instance.
    
    Args:
        config: Dashboard configuration
        
    Returns:
        AuracleDashboard instance
    """
    default_config = {
        'port': 5000,
        'host': '127.0.0.1',
        'debug': False,
        'data_dir': 'data'
    }
    
    if config:
        default_config.update(config)
    
    return AuracleDashboard(default_config)


if __name__ == "__main__":
    # Example usage
    dashboard = create_dashboard({
        'port': 5000,
        'debug': True
    })
    dashboard.start()