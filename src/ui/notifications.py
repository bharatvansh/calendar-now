import sys
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, QtCore
from config.settings import SettingsManager

class NotificationManager(QtCore.QObject):
    """Manages event notifications for calendar events"""
    
    def __init__(self, tray_icon, parent=None, settings_manager: SettingsManager | None = None):
        super().__init__(parent)
        self.tray_icon = tray_icon
        # Allow injection so we share the instance with the tray
        self.settings_manager = settings_manager or SettingsManager()
        self.notified_events = set()  # Track already notified events
    
    def check_event_notifications(self, events):
        """Check events and send notifications if needed"""
        if not self.settings_manager.get_setting('notifications_enabled', True):
            return
        
        notification_minutes = self.settings_manager.get_setting('notification_minutes', 15)
        current_time = datetime.now()
        # Determine tolerance window (in minutes) when the threshold is 0, to fire near event start
        # We use a 1-minute tolerance to account for sync cadence.
        start_tolerance_minutes = 1 if notification_minutes == 0 else 0
        
        for event in events:
            event_id = event.get('id')
            if event_id in self.notified_events:
                continue
            
            # Parse event start time
            start = event.get('start', {})
            start_time_str = start.get('dateTime') or start.get('date')
            
            if not start_time_str:
                continue
            
            try:
                # Parse the start time
                if 'T' in start_time_str:  # DateTime format
                    # Parse ISO time and convert to local naive time for comparison consistency
                    event_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                    if event_time.tzinfo:
                        # Convert to local time then drop tzinfo for naive comparison
                        event_time = event_time.astimezone().replace(tzinfo=None)
                else:  # Date format (all-day event)
                    continue  # Skip all-day events for notifications
                
                # Check if we should notify
                time_until_event = event_time - current_time
                minutes_until_event = time_until_event.total_seconds() / 60
                
                # Fire when we are within the pre-event window. If set to 0, allow a small tolerance around start time.
                if notification_minutes > 0 and 0 <= minutes_until_event <= notification_minutes:
                    self.show_event_notification(event, minutes_until_event)
                    self.notified_events.add(event_id)
                # For 'At start', only notify at or after the start time (no early heads-up).
                # Allow a small late tolerance window to account for sync cadence.
                elif notification_minutes == 0 and -start_tolerance_minutes <= minutes_until_event <= 0:
                    self.show_event_notification(event, minutes_until_event)
                    self.notified_events.add(event_id)
                    
            except Exception as e:
                print(f"Error parsing event time: {e}")
                continue
    
    def show_event_notification(self, event, minutes_until):
        """Show notification for an upcoming event"""
        title = "Calendar Event"
        summary = event.get('summary', 'Untitled Event')
        minutes_setting = self.settings_manager.get_setting('notification_minutes', 15)
        # Improve message for at-start notifications
        if minutes_setting == 0:
            # If we're close to start time, say "Starting now"; otherwise if we somehow ran slightly early, show minutes
            if abs(minutes_until) <= 1:
                message = f"{summary}\nStarting now"
            else:
                message = f"{summary}\nStarting in {int(round(minutes_until))} minutes"
        else:
            if minutes_until <= 1:
                message = f"{summary}\nStarting now"
            else:
                message = f"{summary}\nStarting in {int(minutes_until)} minutes"
        
        # Show system tray notification
        if self.tray_icon.isSystemTrayAvailable():
            self.tray_icon.showMessage(
                title,
                message,
                QtWidgets.QSystemTrayIcon.Information,
                5000  # 5 seconds
            )
        
        # Log for debugging
        print(f"Notification: {message}")
    
    def clear_notified_events(self):
        """Clear the list of notified events (call daily or when refreshing)"""
        self.notified_events.clear()

class DesktopNotification(QtWidgets.QDialog):
    """Custom desktop notification widget"""
    
    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(350, 120)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        
        # Position in bottom-right corner
        screen = QtWidgets.QApplication.desktop().screenGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 100)
        
        self.setup_ui(title, message)
        self.setup_timer()
    
    def setup_ui(self, title, message):
        """Setup the notification UI"""
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Title
        title_label = QtWidgets.QLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        layout.addWidget(title_label)
        
        # Message
        message_label = QtWidgets.QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(message_label)
        
        # Close button
        close_btn = QtWidgets.QPushButton("×")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #ccc;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #999;
            }
        """)
        close_btn.clicked.connect(self.close)
        
        # Position close button in top-right
        close_layout = QtWidgets.QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_btn)
        layout.insertLayout(0, close_layout)
        
        self.setLayout(layout)
        
        # Style the dialog
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 2px solid #ddd;
                border-radius: 8px;
            }
        """)
    
    def setup_timer(self):
        """Setup auto-close timer"""
        self.close_timer = QtCore.QTimer()
        self.close_timer.timeout.connect(self.close)
        self.close_timer.start(5000)  # Auto-close after 5 seconds
    
    def mousePressEvent(self, event):
        """Close on click"""
        self.close()
    
    def closeEvent(self, event):
        """Clean up timer on close"""
        if hasattr(self, 'close_timer'):
            self.close_timer.stop()
        super().closeEvent(event)

# Legacy functions for backward compatibility
def show_notification(title, message):
    """Show a simple notification (legacy function)"""
    print(f"Notification: {title} - {message}")

def notify_upcoming_event(event_title, event_time):
    """Notify about upcoming event (legacy function)"""
    title = f'Upcoming Event: {event_title}'
    message = f'Event starts at: {event_time}'
    show_notification(title, message)