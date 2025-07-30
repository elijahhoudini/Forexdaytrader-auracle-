"""
Economic Calendar Integration
============================

Integrates with free Forex calendar APIs to automatically pause trading 
during high-impact economic events.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from dataclasses import dataclass
import pytz


@dataclass
class EconomicEvent:
    """Represents an economic calendar event."""
    title: str
    country: str
    date: datetime
    time: str
    impact: str  # 'Low', 'Medium', 'High'
    forecast: Optional[str]
    previous: Optional[str]
    actual: Optional[str]
    currency: str


class EconomicCalendar:
    """
    Economic calendar integration for Forex trading.
    
    Features:
    - Fetches economic events from free APIs
    - Filters events by impact level and currency
    - Automatically pauses trading during high-impact events
    - Caches calendar data to minimize API calls
    """
    
    def __init__(self, config: Dict):
        """
        Initialize economic calendar.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.api_key = config.get('api_key')
        self.enabled = config.get('enabled', False)
        self.high_impact_pause_minutes = config.get('high_impact_pause_minutes', 30)
        self.medium_impact_pause_minutes = config.get('medium_impact_pause_minutes', 15)
        self.monitored_currencies = config.get('monitored_currencies', ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'])
        self.cache_file = config.get('cache_file', 'data/economic_calendar_cache.json')
        self.cache_hours = config.get('cache_hours', 6)
        
        # API endpoints (using free services)
        self.api_endpoints = {
            'fcsapi': 'https://fcsapi.com/api-v3/forex/economy_calendar',
            'investing': 'https://api.investing.com/api/financialdata/calendar',
            'forexfactory': 'https://nfs.faireconomy.media/ff_calendar_thisweek.json'
        }
        
        self.events_cache = []
        self.last_fetch = None
        
        # Load cached data
        self._load_cache()
    
    def fetch_events(self, days_ahead: int = 7) -> List[EconomicEvent]:
        """
        Fetch economic events for the next N days.
        
        Args:
            days_ahead: Number of days to fetch events for
            
        Returns:
            List of economic events
        """
        if not self.enabled:
            return []
        
        # Check if cache is still valid
        if self._is_cache_valid():
            return self.events_cache
        
        print("📅 Fetching economic calendar events...")
        
        events = []
        
        # Try different API sources
        for api_name, endpoint in self.api_endpoints.items():
            try:
                if api_name == 'fcsapi':
                    events = self._fetch_from_fcsapi(days_ahead)
                elif api_name == 'forexfactory':
                    events = self._fetch_from_forexfactory()
                
                if events:
                    break
                    
            except Exception as e:
                print(f"Warning: Failed to fetch from {api_name}: {e}")
                continue
        
        if not events:
            print("Warning: Could not fetch economic calendar data from any source")
            return self.events_cache  # Return cached data if available
        
        # Filter and process events
        filtered_events = self._filter_events(events)
        
        # Update cache
        self.events_cache = filtered_events
        self.last_fetch = datetime.now()
        self._save_cache()
        
        print(f"📅 Fetched {len(filtered_events)} relevant economic events")
        
        return filtered_events
    
    def _fetch_from_fcsapi(self, days_ahead: int) -> List[EconomicEvent]:
        """Fetch events from FCS API (requires API key)."""
        if not self.api_key:
            return []
        
        params = {
            'access_key': self.api_key,
            'from': datetime.now().strftime('%Y-%m-%d'),
            'to': (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        }
        
        response = requests.get(self.api_endpoints['fcsapi'], params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') != 200:
            raise Exception(f"API error: {data.get('msg', 'Unknown error')}")
        
        events = []
        for event_data in data.get('response', []):
            try:
                event = EconomicEvent(
                    title=event_data.get('name', ''),
                    country=event_data.get('country', ''),
                    date=datetime.strptime(event_data.get('date', ''), '%Y-%m-%d'),
                    time=event_data.get('time', ''),
                    impact=event_data.get('impact', 'Low'),
                    forecast=event_data.get('forecast'),
                    previous=event_data.get('previous'),
                    actual=event_data.get('actual'),
                    currency=event_data.get('currency', '')
                )
                events.append(event)
            except Exception as e:
                print(f"Warning: Could not parse event: {e}")
                continue
        
        return events
    
    def _fetch_from_forexfactory(self) -> List[EconomicEvent]:
        """Fetch events from Forex Factory free JSON feed."""
        response = requests.get(self.api_endpoints['forexfactory'], timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        events = []
        for event_data in data:
            try:
                # Parse date and time
                date_str = event_data.get('date', '')
                time_str = event_data.get('time', '')
                
                if date_str and time_str:
                    datetime_str = f"{date_str} {time_str}"
                    event_datetime = datetime.strptime(datetime_str, '%m-%d-%Y %I:%M%p')
                else:
                    event_datetime = datetime.now()
                
                # Map impact levels
                impact_mapping = {
                    'Non-Economic': 'Low',
                    'Low Impact Expected': 'Low',
                    'Medium Impact Expected': 'Medium',
                    'High Impact Expected': 'High'
                }
                
                impact = impact_mapping.get(event_data.get('impact', ''), 'Low')
                
                event = EconomicEvent(
                    title=event_data.get('title', ''),
                    country=event_data.get('country', ''),
                    date=event_datetime,
                    time=time_str,
                    impact=impact,
                    forecast=event_data.get('forecast'),
                    previous=event_data.get('previous'),
                    actual=event_data.get('actual'),
                    currency=event_data.get('currency', '')
                )
                events.append(event)
                
            except Exception as e:
                print(f"Warning: Could not parse Forex Factory event: {e}")
                continue
        
        return events
    
    def _filter_events(self, events: List[EconomicEvent]) -> List[EconomicEvent]:
        """Filter events by currency and impact level."""
        filtered = []
        
        for event in events:
            # Filter by monitored currencies
            if event.currency not in self.monitored_currencies:
                continue
            
            # Filter by time (only future events)
            if event.date < datetime.now():
                continue
            
            # Filter by impact (at least medium)
            if event.impact in ['Medium', 'High']:
                filtered.append(event)
        
        return filtered
    
    def should_pause_trading(self, current_time: datetime = None) -> Tuple[bool, Optional[EconomicEvent]]:
        """
        Check if trading should be paused due to economic events.
        
        Args:
            current_time: Current time (defaults to now)
            
        Returns:
            Tuple of (should_pause, causing_event)
        """
        if not self.enabled:
            return False, None
        
        if current_time is None:
            current_time = datetime.now()
        
        # Get current events
        events = self.fetch_events()
        
        for event in events:
            # Calculate time difference
            time_diff = (event.date - current_time).total_seconds() / 60  # minutes
            
            # Check if we're in the pause window
            pause_minutes = 0
            if event.impact == 'High':
                pause_minutes = self.high_impact_pause_minutes
            elif event.impact == 'Medium':
                pause_minutes = self.medium_impact_pause_minutes
            
            # Pause trading before and after the event
            if -pause_minutes <= time_diff <= pause_minutes:
                return True, event
        
        return False, None
    
    def get_upcoming_events(self, hours_ahead: int = 24) -> List[EconomicEvent]:
        """
        Get upcoming events within the next N hours.
        
        Args:
            hours_ahead: Number of hours to look ahead
            
        Returns:
            List of upcoming events
        """
        events = self.fetch_events()
        current_time = datetime.now()
        cutoff_time = current_time + timedelta(hours=hours_ahead)
        
        upcoming = []
        for event in events:
            if current_time <= event.date <= cutoff_time:
                upcoming.append(event)
        
        return sorted(upcoming, key=lambda x: x.date)
    
    def get_high_impact_events_today(self) -> List[EconomicEvent]:
        """Get high impact events for today."""
        events = self.fetch_events()
        today = datetime.now().date()
        
        high_impact_today = []
        for event in events:
            if event.date.date() == today and event.impact == 'High':
                high_impact_today.append(event)
        
        return sorted(high_impact_today, key=lambda x: x.date)
    
    def get_next_trading_pause(self) -> Optional[Dict]:
        """
        Get information about the next trading pause.
        
        Returns:
            Dictionary with pause information or None
        """
        events = self.fetch_events()
        current_time = datetime.now()
        
        next_pause = None
        for event in events:
            if event.date > current_time and event.impact in ['Medium', 'High']:
                pause_minutes = (self.high_impact_pause_minutes if event.impact == 'High' 
                               else self.medium_impact_pause_minutes)
                
                pause_start = event.date - timedelta(minutes=pause_minutes)
                pause_end = event.date + timedelta(minutes=pause_minutes)
                
                if not next_pause or pause_start < next_pause['start_time']:
                    next_pause = {
                        'event': event,
                        'start_time': pause_start,
                        'end_time': pause_end,
                        'duration_minutes': pause_minutes * 2
                    }
        
        return next_pause
    
    def _is_cache_valid(self) -> bool:
        """Check if the cached data is still valid."""
        if not self.last_fetch or not self.events_cache:
            return False
        
        hours_since_fetch = (datetime.now() - self.last_fetch).total_seconds() / 3600
        return hours_since_fetch < self.cache_hours
    
    def _save_cache(self):
        """Save events cache to file."""
        try:
            cache_data = {
                'last_fetch': self.last_fetch.isoformat() if self.last_fetch else None,
                'events': []
            }
            
            for event in self.events_cache:
                cache_data['events'].append({
                    'title': event.title,
                    'country': event.country,
                    'date': event.date.isoformat(),
                    'time': event.time,
                    'impact': event.impact,
                    'forecast': event.forecast,
                    'previous': event.previous,
                    'actual': event.actual,
                    'currency': event.currency
                })
            
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not save calendar cache: {e}")
    
    def _load_cache(self):
        """Load events cache from file."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                if cache_data.get('last_fetch'):
                    self.last_fetch = datetime.fromisoformat(cache_data['last_fetch'])
                
                self.events_cache = []
                for event_data in cache_data.get('events', []):
                    event = EconomicEvent(
                        title=event_data['title'],
                        country=event_data['country'],
                        date=datetime.fromisoformat(event_data['date']),
                        time=event_data['time'],
                        impact=event_data['impact'],
                        forecast=event_data['forecast'],
                        previous=event_data['previous'],
                        actual=event_data['actual'],
                        currency=event_data['currency']
                    )
                    self.events_cache.append(event)
                    
        except Exception as e:
            print(f"Warning: Could not load calendar cache: {e}")
    
    def get_calendar_summary(self) -> Dict:
        """Get a summary of calendar data and status."""
        events = self.fetch_events()
        
        summary = {
            'enabled': self.enabled,
            'total_events': len(events),
            'high_impact_events': len([e for e in events if e.impact == 'High']),
            'medium_impact_events': len([e for e in events if e.impact == 'Medium']),
            'monitored_currencies': self.monitored_currencies,
            'last_fetch': self.last_fetch.isoformat() if self.last_fetch else None,
            'cache_valid': self._is_cache_valid()
        }
        
        # Check current trading status
        should_pause, causing_event = self.should_pause_trading()
        summary['currently_paused'] = should_pause
        if causing_event:
            summary['pause_reason'] = {
                'event_title': causing_event.title,
                'event_time': causing_event.date.isoformat(),
                'impact': causing_event.impact,
                'currency': causing_event.currency
            }
        
        # Next pause information
        next_pause = self.get_next_trading_pause()
        if next_pause:
            summary['next_pause'] = {
                'event_title': next_pause['event'].title,
                'start_time': next_pause['start_time'].isoformat(),
                'end_time': next_pause['end_time'].isoformat(),
                'duration_minutes': next_pause['duration_minutes']
            }
        
        return summary


def create_economic_calendar(config: Dict = None) -> EconomicCalendar:
    """
    Create economic calendar instance.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        EconomicCalendar instance
    """
    default_config = {
        'enabled': False,
        'api_key': None,
        'high_impact_pause_minutes': 30,
        'medium_impact_pause_minutes': 15,
        'monitored_currencies': ['USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD'],
        'cache_file': 'data/economic_calendar_cache.json',
        'cache_hours': 6
    }
    
    if config:
        default_config.update(config)
    
    return EconomicCalendar(default_config)


# Example usage and testing
if __name__ == "__main__":
    # Test the economic calendar
    calendar = create_economic_calendar({
        'enabled': True,
        'high_impact_pause_minutes': 30
    })
    
    # Fetch events
    events = calendar.fetch_events(days_ahead=7)
    print(f"Found {len(events)} economic events")
    
    # Check if trading should be paused
    should_pause, event = calendar.should_pause_trading()
    print(f"Should pause trading: {should_pause}")
    if event:
        print(f"Reason: {event.title} at {event.date}")
    
    # Get upcoming events
    upcoming = calendar.get_upcoming_events(hours_ahead=24)
    print(f"\nUpcoming events in next 24 hours:")
    for event in upcoming:
        print(f"  {event.date.strftime('%Y-%m-%d %H:%M')} - {event.title} ({event.impact} impact)")
    
    # Get calendar summary
    summary = calendar.get_calendar_summary()
    print(f"\nCalendar summary: {summary}")