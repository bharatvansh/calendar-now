import os
import json
from pathlib import Path
from typing import Any, Dict

class SettingsManager:
    """Manages application settings and user preferences"""
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_dir()
        self.settings_file = self.app_data_dir / 'settings.json'
        
        # Ensure app data directory exists
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Default settings
        self.default_settings = {
            'notifications_enabled': True,
            # Default to notify at the exact start time
            'notification_minutes': 0,
            'sync_interval': 60000,  # 1 minute in milliseconds
            'start_with_windows': False,
            'minimize_to_tray': True,
            'show_all_day_events': True,
            'default_event_duration': 60,  # minutes
            'working_hours_start': 9,
            'working_hours_end': 17,
            'timezone': 'UTC',
            'theme': 'system',  # light, dark, system
            'window_position': {'x': 100, 'y': 100},
            'window_size': {'width': 800, 'height': 600},
            'calendar_view': 'week',  # day, week, month
            'show_weekends': True,
            'first_day_of_week': 0,  # 0 = Sunday, 1 = Monday
            'date_format': '%Y-%m-%d',
            'time_format': '%I:%M %p',
            'quick_add_enabled': True,
            'debug_mode': False,
            # Legacy/general appearance settings (kept for backward compat)
            'font_size': 14,
            'bg_color': '#000000',
            'text_color': '#FFFFFF',
            # New: per-section overlay appearance settings
            'overlay_time': {
                'font_family': 'Segoe UI',
                'font_size': 14,
                'bold': False,
                'color': '#FFFFFF'
            },
            'overlay_task': {
                'font_family': 'Segoe UI',
                'font_size': 14,
                'bold': True,
                'color': '#FFFFFF'
            },
            'overlay_ending': {
                'font_family': 'Segoe UI',
                'font_size': 11,
                'bold': False,
                'color': '#FFFFFF'
            }
        }
        
        # Load existing settings
        self.settings = self.load_settings()
    
    def _get_app_data_dir(self):
        """Get the application data directory based on OS"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', ''))
        else:  # macOS/Linux
            base_dir = Path.home() / '.local' / 'share'
        
    return base_dir / 'CalendarNow'
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or return defaults"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    saved_settings = json.load(f)
                
                # Merge with defaults (in case new settings were added)
                settings = self.default_settings.copy()
                settings.update(saved_settings)

                # Migration/normalization for overlay styles
                changed = False
                # Helper to ensure complete style dict
                def hydrate_style(style: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
                    if not isinstance(style, dict):
                        return fallback.copy()
                    hydrated = fallback.copy()
                    hydrated.update({k: v for k, v in style.items() if k in fallback})
                    return hydrated

                # Determine a base style from existing settings
                legacy_color = saved_settings.get('text_color', settings.get('text_color', '#FFFFFF'))
                legacy_size = saved_settings.get('font_size', settings.get('font_size', 14))
                base_task = settings.get('overlay_task') or {
                    'font_family': 'Segoe UI',
                    'font_size': legacy_size,
                    'bold': True,
                    'color': legacy_color,
                }
                # If none of overlay_* existed at all, seed all from legacy/base
                if not any(k in saved_settings for k in ('overlay_time', 'overlay_task', 'overlay_ending')):
                    settings['overlay_task'] = base_task
                    # Time seeded from base but not bold by default
                    settings['overlay_time'] = {**base_task, 'bold': False}
                    settings['overlay_ending'] = {
                        **base_task,
                        'bold': False,
                        # Keep ending a bit smaller if legacy size is int; else use default 11
                        'font_size': max(11, int(legacy_size) - 3) if isinstance(legacy_size, int) else 11,
                    }
                    changed = True
                else:
                    # Ensure all three exist; if missing, copy from task/base
                    if 'overlay_task' not in settings:
                        settings['overlay_task'] = base_task
                        changed = True
                    if 'overlay_time' not in settings:
                        settings['overlay_time'] = settings['overlay_task'].copy()
                        changed = True
                    if 'overlay_ending' not in settings:
                        # similar to task but not bold and maybe smaller
                        end_style = settings['overlay_task'].copy()
                        end_style['bold'] = False
                        if isinstance(legacy_size, int):
                            end_style['font_size'] = max(11, int(legacy_size) - 3)
                        settings['overlay_ending'] = end_style
                        changed = True

                # Hydrate subkeys to avoid None/missing
                defaults_time = self.default_settings['overlay_time']
                defaults_task = self.default_settings['overlay_task']
                defaults_end = self.default_settings['overlay_ending']
                new_time = hydrate_style(settings.get('overlay_time'), defaults_time)
                new_task = hydrate_style(settings.get('overlay_task'), defaults_task)
                new_end = hydrate_style(settings.get('overlay_ending'), defaults_end)
                if new_time != settings.get('overlay_time'):
                    settings['overlay_time'] = new_time
                    changed = True
                if new_task != settings.get('overlay_task'):
                    settings['overlay_task'] = new_task
                    changed = True
                if new_end != settings.get('overlay_ending'):
                    settings['overlay_ending'] = new_end
                    changed = True

                if changed:
                    self.settings = settings.copy()
                    self.save_settings()

                # Additional migration: if the three overlay styles look like the old palette
                # (yellow for time/task and gray for ending), auto-update to white defaults once.
                # This covers users who were on an interim build with old defaults but had not
                # explicitly customized per-section styles yet.
                def looks_like_old_palette(t, a, e):
                    try:
                        return (
                            t.get('color') in ('#FFFF00', '#ffff00') and
                            a.get('color') in ('#FFFF00', '#ffff00') and
                            e.get('color') in ('#CCCCCC', '#cccccc') and
                            isinstance(t.get('bold'), bool) and isinstance(a.get('bold'), bool) and isinstance(e.get('bold'), bool)
                        )
                    except Exception:
                        return False

                ot, oa, oe = settings.get('overlay_time', {}), settings.get('overlay_task', {}), settings.get('overlay_ending', {})
                if looks_like_old_palette(ot, oa, oe):
                    settings['overlay_time'] = {**defaults_time}
                    settings['overlay_task'] = {**defaults_task}
                    settings['overlay_ending'] = {**defaults_end}
                    self.settings = settings.copy()
                    self.save_settings()

                return settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self) -> bool:
        """Save current settings to file"""
        try:
            # Write atomically to avoid partial/corrupt files read by other threads
            tmp_path = self.settings_file.with_suffix('.tmp')
            with open(tmp_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
                f.flush()
                os.fsync(f.fileno()) if hasattr(os, 'fsync') else None
            os.replace(tmp_path, self.settings_file)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key: str, default=None) -> Any:
        """Get a setting value"""
        return self.settings.get(key, default if default is not None else self.default_settings.get(key))
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a setting value and save"""
        self.settings[key] = value
        return self.save_settings()

    def set_settings_bulk(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings at once and save atomically.
        This reduces the risk of partial writes when many keys change together."""
        self.settings.update(updates)
        return self.save_settings()
    
    def reset_setting(self, key: str) -> bool:
        """Reset a setting to its default value"""
        if key in self.default_settings:
            self.settings[key] = self.default_settings[key]
            return self.save_settings()
        return False
    
    def reset_all_settings(self) -> bool:
        """Reset all settings to defaults"""
        self.settings = self.default_settings.copy()
        return self.save_settings()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self.settings.copy()
    
    def import_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """Import settings from a dictionary"""
        try:
            # Validate settings against defaults
            for key, value in settings_dict.items():
                if key in self.default_settings:
                    self.settings[key] = value
            
            return self.save_settings()
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
    
    def export_settings(self) -> Dict[str, Any]:
        """Export current settings"""
        return self.settings.copy()
    
    def backup_settings(self, backup_path: str = None) -> bool:
        """Create a backup of current settings"""
        try:
            if not backup_path:
                backup_path = str(self.app_data_dir / 'settings_backup.json')
            
            with open(backup_path, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error backing up settings: {e}")
            return False
    
    def restore_settings(self, backup_path: str) -> bool:
        """Restore settings from backup"""
        try:
            with open(backup_path, 'r') as f:
                backup_settings = json.load(f)
            
            return self.import_settings(backup_settings)
        except Exception as e:
            print(f"Error restoring settings: {e}")
            return False

# Configuration constants
class Config:
    """Static configuration constants"""
    
    # Application info
    APP_NAME = 'Calendar Now'
    APP_VERSION = '1.0.1'
    APP_AUTHOR = 'Calendar Now Team'
    APP_DESCRIPTION = 'A user-friendly application for managing Google Calendar events from the system tray.'
    
    # OAuth settings
    OAUTH_SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    OAUTH_REDIRECT_URI = 'http://localhost:8080/callback'
    OAUTH_TIMEOUT = 120  # seconds
    
    # API settings
    CALENDAR_API_VERSION = 'v3'
    DEFAULT_TIMEZONE = 'UTC'
    
    # UI settings
    TRAY_ICON_SIZE = (16, 16)
    NOTIFICATION_DURATION = 5000  # milliseconds
    
    # Sync settings
    MIN_SYNC_INTERVAL = 60000  # 1 minute in milliseconds
    MAX_SYNC_INTERVAL = 3600000  # 1 hour in milliseconds
    DEFAULT_SYNC_INTERVAL = 60000  # 1 minute in milliseconds
    
    # Event settings
    MAX_EVENTS_PER_REQUEST = 250
    DEFAULT_EVENT_DURATION = 60  # minutes
    
    # File extensions
    SUPPORTED_EXPORT_FORMATS = ['.ics', '.csv', '.json']
    
    # URLs
    GOOGLE_CALENDAR_URL = 'https://calendar.google.com'
    GOOGLE_CLOUD_CONSOLE_URL = 'https://console.cloud.google.com'
    PROJECT_WEBSITE = 'https://github.com/your-username/calendar-now'
    
    @classmethod
    def get_user_agent(cls):
        """Get user agent string for API requests"""
        return f"{cls.APP_NAME}/{cls.APP_VERSION}"