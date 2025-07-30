"""
Forex Market Data Integration Module
===================================

Provides real-time and historical Forex market data using multiple API sources:
- Alpha Vantage (free tier available)
- Twelve Data (free tier available)
- OANDA REST API (demo accounts available)

Supports major currency pairs: EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, etc.
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ForexMarketData:
    """
    Forex market data provider supporting multiple APIs with automatic failover.
    """
    
    # Major currency pairs supported
    MAJOR_PAIRS = [
        'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD'
    ]
    
    # Timeframes supported (in minutes)
    TIMEFRAMES = {
        '1min': 1,
        '5min': 5,
        '15min': 15,
        '30min': 30,
        '1hour': 60,
        '4hour': 240,
        '1day': 1440
    }
    
    def __init__(self):
        """Initialize Forex market data provider."""
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.twelve_data_key = os.getenv('TWELVE_DATA_API_KEY') 
        self.oanda_token = os.getenv('OANDA_API_TOKEN')
        self.oanda_account_id = os.getenv('OANDA_ACCOUNT_ID')
        
        # API endpoints
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        self.twelve_data_base = "https://api.twelvedata.com"
        self.oanda_base = "https://api-fxtrade.oanda.com"  # Live
        self.oanda_demo_base = "https://api-fxpractice.oanda.com"  # Demo
        
        # Use demo by default for safety
        self.use_demo = os.getenv('FOREX_DEMO_MODE', 'true').lower() == 'true'
        self.oanda_url = self.oanda_demo_base if self.use_demo else self.oanda_base
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
        logger.info(f"ForexMarketData initialized - Demo mode: {self.use_demo}")
        if self.alpha_vantage_key:
            logger.info("Alpha Vantage API key configured")
        if self.twelve_data_key:
            logger.info("Twelve Data API key configured")
        if self.oanda_token:
            logger.info("OANDA API token configured")
    
    async def _rate_limit(self, api_name: str):
        """Implement rate limiting for API calls."""
        now = time.time()
        if api_name in self.last_request_time:
            time_since_last = now - self.last_request_time[api_name]
            if time_since_last < self.min_request_interval:
                await asyncio.sleep(self.min_request_interval - time_since_last)
        self.last_request_time[api_name] = time.time()
    
    async def get_current_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """
        Get current real-time price for a currency pair.
        
        Args:
            pair: Currency pair (e.g., 'EURUSD')
            
        Returns:
            Dict with bid, ask, spread, timestamp
        """
        try:
            # Try OANDA first (most reliable for real-time)
            if self.oanda_token:
                price = await self._get_oanda_price(pair)
                if price:
                    return price
            
            # Fallback to Twelve Data
            if self.twelve_data_key:
                price = await self._get_twelve_data_price(pair)
                if price:
                    return price
            
            # Final fallback to Alpha Vantage
            if self.alpha_vantage_key:
                price = await self._get_alpha_vantage_price(pair)
                if price:
                    return price
            
            logger.warning(f"Could not get price for {pair} from any API")
            return None
            
        except Exception as e:
            logger.error(f"Error getting current price for {pair}: {e}")
            return None
    
    async def _get_oanda_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get current price from OANDA API."""
        try:
            await self._rate_limit('oanda')
            
            # Format pair for OANDA (EUR_USD instead of EURUSD)
            oanda_pair = f"{pair[:3]}_{pair[3:]}"
            
            headers = {
                'Authorization': f'Bearer {self.oanda_token}',
                'Content-Type': 'application/json'
            }
            
            url = f"{self.oanda_url}/v3/accounts/{self.oanda_account_id}/pricing"
            params = {'instruments': oanda_pair}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'prices' in data and len(data['prices']) > 0:
                            price_data = data['prices'][0]
                            bid = float(price_data['bids'][0]['price'])
                            ask = float(price_data['asks'][0]['price'])
                            return {
                                'pair': pair,
                                'bid': bid,
                                'ask': ask,
                                'mid': (bid + ask) / 2,
                                'spread': ask - bid,
                                'timestamp': datetime.now(),
                                'source': 'oanda'
                            }
                    else:
                        logger.warning(f"OANDA API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"OANDA price fetch error: {e}")
        
        return None
    
    async def _get_twelve_data_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get current price from Twelve Data API."""
        try:
            await self._rate_limit('twelve_data')
            
            url = f"{self.twelve_data_base}/price"
            params = {
                'symbol': pair,
                'apikey': self.twelve_data_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'price' in data:
                            price = float(data['price'])
                            # Twelve Data gives mid price, estimate bid/ask
                            spread = price * 0.0001  # Estimate 1 pip spread
                            return {
                                'pair': pair,
                                'bid': price - spread/2,
                                'ask': price + spread/2,
                                'mid': price,
                                'spread': spread,
                                'timestamp': datetime.now(),
                                'source': 'twelve_data'
                            }
                    else:
                        logger.warning(f"Twelve Data API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Twelve Data price fetch error: {e}")
        
        return None
    
    async def _get_alpha_vantage_price(self, pair: str) -> Optional[Dict[str, Any]]:
        """Get current price from Alpha Vantage API."""
        try:
            await self._rate_limit('alpha_vantage')
            
            params = {
                'function': 'CURRENCY_EXCHANGE_RATE',
                'from_currency': pair[:3],
                'to_currency': pair[3:],
                'apikey': self.alpha_vantage_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.alpha_vantage_base, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'Realtime Currency Exchange Rate' in data:
                            rate_data = data['Realtime Currency Exchange Rate']
                            price = float(rate_data['5. Exchange Rate'])
                            # Alpha Vantage gives mid price, estimate bid/ask
                            spread = price * 0.0001  # Estimate 1 pip spread
                            return {
                                'pair': pair,
                                'bid': price - spread/2,
                                'ask': price + spread/2,
                                'mid': price,
                                'spread': spread,
                                'timestamp': datetime.now(),
                                'source': 'alpha_vantage'
                            }
                    else:
                        logger.warning(f"Alpha Vantage API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Alpha Vantage price fetch error: {e}")
        
        return None
    
    async def get_historical_data(self, pair: str, timeframe: str = '1hour', 
                                 periods: int = 100) -> Optional[pd.DataFrame]:
        """
        Get historical OHLCV data for technical analysis.
        
        Args:
            pair: Currency pair (e.g., 'EURUSD')
            timeframe: Data timeframe ('1min', '5min', '15min', '1hour', etc.)
            periods: Number of periods to fetch
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Try Twelve Data first (good historical data)
            if self.twelve_data_key:
                data = await self._get_twelve_data_historical(pair, timeframe, periods)
                if data is not None:
                    return data
            
            # Fallback to Alpha Vantage
            if self.alpha_vantage_key:
                data = await self._get_alpha_vantage_historical(pair, timeframe, periods)
                if data is not None:
                    return data
            
            logger.warning(f"Could not get historical data for {pair}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting historical data for {pair}: {e}")
            return None
    
    async def _get_twelve_data_historical(self, pair: str, timeframe: str, 
                                        periods: int) -> Optional[pd.DataFrame]:
        """Get historical data from Twelve Data API."""
        try:
            await self._rate_limit('twelve_data')
            
            url = f"{self.twelve_data_base}/time_series"
            params = {
                'symbol': pair,
                'interval': timeframe,
                'outputsize': periods,
                'apikey': self.twelve_data_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'values' in data:
                            df = pd.DataFrame(data['values'])
                            df['datetime'] = pd.to_datetime(df['datetime'])
                            df = df.set_index('datetime')
                            
                            # Convert to numeric
                            for col in ['open', 'high', 'low', 'close']:
                                df[col] = pd.to_numeric(df[col])
                            
                            # Sort by datetime (oldest first)
                            df = df.sort_index()
                            
                            return df
                    else:
                        logger.warning(f"Twelve Data historical API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Twelve Data historical fetch error: {e}")
        
        return None
    
    async def _get_alpha_vantage_historical(self, pair: str, timeframe: str, 
                                          periods: int) -> Optional[pd.DataFrame]:
        """Get historical data from Alpha Vantage API."""
        try:
            await self._rate_limit('alpha_vantage')
            
            # Map timeframes to Alpha Vantage functions
            function_map = {
                '1min': 'FX_INTRADAY',
                '5min': 'FX_INTRADAY',
                '15min': 'FX_INTRADAY',
                '30min': 'FX_INTRADAY',
                '1hour': 'FX_INTRADAY',
                '1day': 'FX_DAILY'
            }
            
            if timeframe not in function_map:
                logger.error(f"Unsupported timeframe for Alpha Vantage: {timeframe}")
                return None
            
            params = {
                'function': function_map[timeframe],
                'from_symbol': pair[:3],
                'to_symbol': pair[3:],
                'apikey': self.alpha_vantage_key
            }
            
            if timeframe != '1day':
                params['interval'] = timeframe
            
            async with aiohttp.ClientSession() as session:
                async with session.get(self.alpha_vantage_base, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Find time series data
                        time_series_key = None
                        for key in data.keys():
                            if 'Time Series' in key:
                                time_series_key = key
                                break
                        
                        if time_series_key and time_series_key in data:
                            time_series = data[time_series_key]
                            
                            # Convert to DataFrame
                            df_data = []
                            for timestamp, values in time_series.items():
                                df_data.append({
                                    'datetime': pd.to_datetime(timestamp),
                                    'open': float(values['1. open']),
                                    'high': float(values['2. high']),
                                    'low': float(values['3. low']),
                                    'close': float(values['4. close'])
                                })
                            
                            df = pd.DataFrame(df_data)
                            df = df.set_index('datetime')
                            df = df.sort_index()
                            
                            # Limit to requested periods
                            if len(df) > periods:
                                df = df.tail(periods)
                            
                            return df
                        else:
                            logger.warning("No time series data in Alpha Vantage response")
                    else:
                        logger.warning(f"Alpha Vantage historical API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Alpha Vantage historical fetch error: {e}")
        
        return None
    
    async def get_multiple_prices(self, pairs: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get current prices for multiple currency pairs simultaneously.
        
        Args:
            pairs: List of currency pairs
            
        Returns:
            Dict mapping pair names to price data
        """
        tasks = [self.get_current_price(pair) for pair in pairs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        price_data = {}
        for pair, result in zip(pairs, results):
            if isinstance(result, dict):
                price_data[pair] = result
            else:
                logger.warning(f"Failed to get price for {pair}: {result}")
                price_data[pair] = None
        
        return price_data
    
    async def is_market_open(self) -> bool:
        """
        Check if Forex market is currently open.
        Forex market is open 24/5 (Monday to Friday).
        """
        try:
            now = datetime.utcnow()
            
            # Check if it's weekend
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Forex market opens Sunday 5pm EST and closes Friday 5pm EST
            # For simplicity, assume it's open Monday-Friday
            return True
            
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            return True  # Default to open

    def get_supported_pairs(self) -> List[str]:
        """Get list of supported currency pairs."""
        return self.MAJOR_PAIRS.copy()
    
    def get_supported_timeframes(self) -> List[str]:
        """Get list of supported timeframes."""
        return list(self.TIMEFRAMES.keys())

# Example usage and testing
async def test_forex_data():
    """Test function to verify Forex market data functionality."""
    print("🧪 Testing Forex Market Data Integration...")
    
    forex_data = ForexMarketData()
    
    # Test current price
    print("\n📊 Testing current price fetching...")
    price = await forex_data.get_current_price('EURUSD')
    if price:
        print(f"✅ EURUSD Current Price: {price}")
    else:
        print("❌ Failed to get EURUSD current price")
    
    # Test multiple prices
    print("\n📊 Testing multiple price fetching...")
    pairs = ['EURUSD', 'GBPUSD', 'USDJPY']
    prices = await forex_data.get_multiple_prices(pairs)
    for pair, price_data in prices.items():
        if price_data:
            print(f"✅ {pair}: {price_data['mid']:.5f} (Source: {price_data['source']})")
        else:
            print(f"❌ Failed to get price for {pair}")
    
    # Test historical data
    print("\n📊 Testing historical data fetching...")
    historical = await forex_data.get_historical_data('EURUSD', '1hour', 10)
    if historical is not None:
        print(f"✅ Historical data retrieved: {len(historical)} periods")
        print(historical.tail())
    else:
        print("❌ Failed to get historical data")
    
    # Test market status
    market_open = await forex_data.is_market_open()
    print(f"\n🕐 Market Status: {'Open' if market_open else 'Closed'}")
    
    print("\n✅ Forex market data testing completed!")

if __name__ == "__main__":
    asyncio.run(test_forex_data())