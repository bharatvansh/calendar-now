import os
import sys
import json
import platform
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path

def get_system_info() -> Dict[str, str]:
    """Get system information"""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'platform_release': platform.release(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'python_executable': sys.executable,
    }

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.
    When bundled by PyInstaller, resources are unpacked to a temp folder
    accessible via sys._MEIPASS. Otherwise, resolve relative to project root.
    """
    try:
        base_path = getattr(sys, '_MEIPASS')  # type: ignore[attr-defined]
    except Exception:
        # Resolve relative to the repository root (where this file is located)
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.normpath(os.path.join(base_path, relative_path))

def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == 'Windows'

def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system() == 'Darwin'

def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system() == 'Linux'

def format_datetime(dt: datetime, format_type: str = 'friendly') -> str:
    """Format datetime in various ways"""
    if not dt:
        return "No date"
    
    now = datetime.now()
    
    if format_type == 'friendly':
        # Friendly format like "Today at 2:30 PM" or "Tomorrow at 9:00 AM"
        if dt.date() == now.date():
            return f"Today at {dt.strftime('%I:%M %p')}"
        elif dt.date() == (now + timedelta(days=1)).date():
            return f"Tomorrow at {dt.strftime('%I:%M %p')}"
        elif dt.date() == (now - timedelta(days=1)).date():
            return f"Yesterday at {dt.strftime('%I:%M %p')}"
        elif dt.year == now.year:
            return dt.strftime('%B %d at %I:%M %p')
        else:
            return dt.strftime('%B %d, %Y at %I:%M %p')
    
    elif format_type == 'short':
        return dt.strftime('%m/%d %I:%M %p')
    
    elif format_type == 'long':
        return dt.strftime('%A, %B %d, %Y at %I:%M %p')
    
    elif format_type == 'iso':
        return dt.isoformat()
    
    else:
        return dt.strftime('%Y-%m-%d %H:%M:%S')

def format_duration(start: datetime, end: datetime) -> str:
    """Format duration between two times"""
    if not start or not end:
        return "Unknown duration"
    
    duration = end - start
    
    if duration.total_seconds() < 0:
        return "Invalid duration"
    
    days = duration.days
    hours, remainder = divmod(duration.seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if not parts:
        return "Less than a minute"
    
    return ", ".join(parts)

def time_until(target: datetime) -> str:
    """Get human-readable time until target datetime"""
    if not target:
        return "Unknown"
    
    now = datetime.now()
    if target.tzinfo:
        target = target.replace(tzinfo=None)  # Simplified timezone handling
    
    if target <= now:
        return "Now"
    
    diff = target - now
    return format_timedelta(diff)

def format_timedelta(td: timedelta) -> str:
    """Format timedelta in human-readable format"""
    total_seconds = int(td.total_seconds())
    
    if total_seconds < 60:
        return "Less than a minute"
    elif total_seconds < 3600:
        minutes = total_seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif total_seconds < 86400:
        hours = total_seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = total_seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"

def safe_json_load(file_path: str, default=None) -> Any:
    """Safely load JSON file with fallback"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return default if default is not None else {}

def safe_json_save(file_path: str, data: Any) -> bool:
    """Safely save data to JSON file"""
    try:
        # Ensure directory exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")
        return False

def debug_log(message: str, level: str = "INFO") -> None:
    """Log debug message if debug mode is enabled"""
    if os.environ.get('DEBUG_MODE'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")

def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard"""
    try:
        from PyQt5.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        return True
    except Exception as e:
        debug_log(f"Failed to copy to clipboard: {e}", "ERROR")
        return False

def open_url(url: str) -> bool:
    """Open URL in default browser"""
    try:
        import webbrowser
        webbrowser.open(url)
        return True
    except Exception as e:
        debug_log(f"Failed to open URL {url}: {e}", "ERROR")
        return False

# Legacy functions for backward compatibility
def format_date(date):
    return date.strftime("%Y-%m-%d")

def format_time(time):
    return time.strftime("%H:%M")

def is_valid_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def show_error_message(message):
    """Show error message using PyQt5"""
    try:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.critical(None, "Error", message)
    except:
        print(f"Error: {message}")

def show_info_message(message):
    """Show info message using PyQt5"""
    try:
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(None, "Information", message)
    except:
        print(f"Info: {message}")