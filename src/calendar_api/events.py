from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CalendarEvent:
    """Represents a calendar event with helper methods"""
    
    def __init__(self, event_data: Dict):
        self.raw_data = event_data
        self.id = event_data.get('id')
        self.summary = event_data.get('summary', 'Untitled Event')
        self.description = event_data.get('description', '')
        self.location = event_data.get('location', '')
        self.start = event_data.get('start', {})
        self.end = event_data.get('end', {})
        self.attendees = event_data.get('attendees', [])
        self.created = event_data.get('created')
        self.updated = event_data.get('updated')
        self.status = event_data.get('status', 'confirmed')
        self.html_link = event_data.get('htmlLink')
    
    @property
    def start_time(self) -> Optional[datetime]:
        """Get event start time as datetime object"""
        start_str = self.start.get('dateTime') or self.start.get('date')
        if not start_str:
            return None
        
        try:
            if 'T' in start_str:  # DateTime format
                return datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            else:  # Date format (all-day event)
                return datetime.fromisoformat(start_str)
        except:
            return None
    
    @property
    def end_time(self) -> Optional[datetime]:
        """Get event end time as datetime object"""
        end_str = self.end.get('dateTime') or self.end.get('date')
        if not end_str:
            return None
        
        try:
            if 'T' in end_str:  # DateTime format
                return datetime.fromisoformat(end_str.replace('Z', '+00:00'))
            else:  # Date format (all-day event)
                return datetime.fromisoformat(end_str)
        except:
            return None
    
    @property
    def is_all_day(self) -> bool:
        """Check if this is an all-day event"""
        return 'date' in self.start and 'dateTime' not in self.start
    
    @property
    def is_upcoming(self) -> bool:
        """Check if event is upcoming"""
        start = self.start_time
        if start:
            return start > datetime.now()
        return False
    
    @property
    def is_today(self) -> bool:
        """Check if event is today"""
        start = self.start_time
        if start:
            today = datetime.now().date()
            return start.date() == today
        return False
    
    def formatted_time_range(self) -> str:
        """Get formatted time range string"""
        start = self.start_time
        end = self.end_time
        
        if not start:
            return "No time specified"
        
        if self.is_all_day:
            return "All day"
        
        start_str = start.strftime("%I:%M %p")
        if end:
            end_str = end.strftime("%I:%M %p")
            if start.date() == end.date():
                return f"{start_str} - {end_str}"
            else:
                return f"{start.strftime('%m/%d %I:%M %p')} - {end.strftime('%m/%d %I:%M %p')}"
        else:
            return start_str
    
    def __str__(self) -> str:
        return f"{self.summary} ({self.formatted_time_range()})"

class EventManager:
    """Manages calendar events with additional functionality"""
    
    def __init__(self, calendar_client):
        self.calendar_client = calendar_client
    
    def get_events_as_objects(self, calendar_id='primary', **kwargs) -> List[CalendarEvent]:
        """Get events as CalendarEvent objects"""
        events_data = self.calendar_client.list_events(calendar_id=calendar_id, **kwargs)
        return [CalendarEvent(event) for event in events_data]
    
    def get_upcoming_events(self, hours=24, calendar_id='primary') -> List[CalendarEvent]:
        """Get upcoming events within specified hours"""
        events_data = self.calendar_client.get_upcoming_events(hours=hours, calendar_id=calendar_id)
        return [CalendarEvent(event) for event in events_data]

# Legacy class for backward compatibility
class CalendarEvents:
    def __init__(self, service):
        self.service = service

    def create_event(self, summary, start_time, end_time, description='', location=''):
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',
            },
        }

        try:
            from googleapiclient.errors import HttpError
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f'Event created: {event.get("htmlLink")}')
            return event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def list_events(self, time_min=None, time_max=None, max_results=10):
        events_result = self.service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max,
                                                   maxResults=max_results, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def get_upcoming_events(self, max_results=10):
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        return self.list_events(time_min=now, max_results=max_results)