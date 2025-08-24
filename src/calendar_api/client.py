import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class GoogleCalendarClient:
    """Google Calendar API client for calendar operations"""
    
    def __init__(self, credentials):
        self.credentials = credentials
        self.service = self.create_service()

    def create_service(self):
        """Create Google Calendar service"""
        try:
            # Refresh credentials if needed
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            
            service = build('calendar', 'v3', credentials=self.credentials)
            return service
        except Exception as e:
            print(f"Failed to create calendar service: {e}")
            raise

    def list_events(self, calendar_id='primary', max_results=10, days_ahead=7):
        """List upcoming events"""
        try:
            # Calculate time range
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Failed to list events: {e}")
            return []

    def get_upcoming_events(self, calendar_id='primary', hours=1):
        """Get events coming up within specified hours"""
        try:
            now = datetime.utcnow()
            time_min = now.isoformat() + 'Z'
            time_max = (now + timedelta(hours=hours)).isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Failed to get upcoming events: {e}")
            return []

    def get_today_events(self, calendar_id='primary'):
        """Get today's events"""
        try:
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Failed to get today's events: {e}")
            return []

    def create_event(self, calendar_id='primary', event_body=None):
        """Create a new event"""
        if event_body is None:
            raise ValueError("Event body must be provided")
        
        try:
            event = self.service.events().insert(
                calendarId=calendar_id, 
                body=event_body
            ).execute()
            return event
        except Exception as e:
            print(f"Failed to create event: {e}")
            raise

    def update_event(self, calendar_id='primary', event_id=None, event_body=None):
        """Update an existing event"""
        if event_id is None or event_body is None:
            raise ValueError("Event ID and body must be provided")
        
        try:
            event = self.service.events().update(
                calendarId=calendar_id, 
                eventId=event_id, 
                body=event_body
            ).execute()
            return event
        except Exception as e:
            print(f"Failed to update event: {e}")
            raise

    def delete_event(self, calendar_id='primary', event_id=None):
        """Delete an event"""
        if event_id is None:
            raise ValueError("Event ID must be provided")
        
        try:
            self.service.events().delete(
                calendarId=calendar_id, 
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Failed to delete event: {e}")
            return False

    def get_calendars(self):
        """Get list of user's calendars"""
        try:
            calendars_result = self.service.calendarList().list().execute()
            return calendars_result.get('items', [])
        except Exception as e:
            print(f"Failed to get calendars: {e}")
            return []

    def get_user_info(self):
        """Get basic user information"""
        try:
            # Get primary calendar to extract user info
            calendar = self.service.calendars().get(calendarId='primary').execute()
            return {
                'email': calendar.get('id'),
                'summary': calendar.get('summary', 'Unknown'),
                'timezone': calendar.get('timeZone', 'UTC')
            }
        except Exception as e:
            print(f"Failed to get user info: {e}")
            return None

    def search_events(self, query, calendar_id='primary', max_results=25):
        """Search for events by text query"""
        try:
            events_result = self.service.events().list(
                calendarId=calendar_id,
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except Exception as e:
            print(f"Failed to search events: {e}")
            return []

    def quick_add_event(self, text, calendar_id='primary'):
        """Quick add event using natural language"""
        try:
            event = self.service.events().quickAdd(
                calendarId=calendar_id,
                text=text
            ).execute()
            return event
        except Exception as e:
            print(f"Failed to quick add event: {e}")
            raise