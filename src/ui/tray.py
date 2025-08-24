import sys
import os
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, QtGui, QtCore
from utils.helpers import resource_path
from auth.oauth import OAuthHandler
from ui.setup_wizard import SetupWizard
from ui.notifications import NotificationManager
from ui.task_display import TaskDisplayWindow
from calendar_api.client import GoogleCalendarClient
from config.settings import SettingsManager

class MainWindow(QtWidgets.QMainWindow):
    """Main application window for calendar view"""
    
    def __init__(self, oauth_handler, parent=None):
        super().__init__(parent)
        self.oauth_handler = oauth_handler
        self.settings_manager = SettingsManager()
        self.calendar_client = None
        
    self.setWindowTitle("Calendar Now - Calendar View")
        self.setGeometry(100, 100, 900, 700)
        self.setWindowIcon(QtGui.QIcon(resource_path("resources/icons/app_icon.png")))
        self.setMinimumSize(600, 400)
        
        # Apply modern window styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                color: #333333;
            }
        """)
        
        self.init_ui()
        self.init_calendar_client()
        self.load_events()
    
    def init_ui(self):
        """Initialize the UI components"""
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Apply modern styling to central widget
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)
        
        # Header section with modern card design
        header_widget = QtWidgets.QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #4285F4, stop:1 #34A853);
                border-radius: 12px;
                padding: 20px;
                margin: 0px;
            }
            QLabel {
                color: white;
                background: transparent;
                border: none;
                margin: 0px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        header_layout = QtWidgets.QHBoxLayout()
        header_layout.setContentsMargins(20, 15, 20, 15)
        header_widget.setLayout(header_layout)
        
        # Header content
        header_content = QtWidgets.QVBoxLayout()
        
        title = QtWidgets.QLabel("📅 Google Calendar Events")
        title.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            margin: 0px;
            color: white;
        """)
        header_content.addWidget(title)
        
        subtitle = QtWidgets.QLabel("Stay organized with your upcoming events")
        subtitle.setStyleSheet("""
            font-size: 14px; 
            margin: 5px 0px 0px 0px;
            color: rgba(255, 255, 255, 0.9);
        """)
        header_content.addWidget(subtitle)
        
        header_layout.addLayout(header_content)
        header_layout.addStretch()
        
        # Action buttons container
        buttons_layout = QtWidgets.QVBoxLayout()
        
        # Refresh button with icon
        self.refresh_btn = QtWidgets.QPushButton("🔄 Refresh Events")
        self.refresh_btn.clicked.connect(self.load_events)
        buttons_layout.addWidget(self.refresh_btn)
        
        header_layout.addLayout(buttons_layout)
        main_layout.addWidget(header_widget)
        
        # Events section
        events_section = QtWidgets.QWidget()
        events_section.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 12px;
                margin: 0px;
            }
        """)
        
        events_layout = QtWidgets.QVBoxLayout()
        events_layout.setContentsMargins(20, 20, 20, 20)
        events_section.setLayout(events_layout)
        
        # Events header
        events_header = QtWidgets.QLabel("📋 Upcoming Events")
        events_header.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #333333;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        """)
        events_layout.addWidget(events_header)
        
        # Events list with modern styling
        self.events_list = QtWidgets.QListWidget()
        self.events_list.setStyleSheet("""
            QListWidget {
                background-color: #fafafa;
                border: none;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #e3f2fd;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px 0px;
                font-size: 14px;
                line-height: 1.4;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border-color: #4285F4;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #4285F4;
                color: #1565C0;
            }
            QListWidget::item:disabled {
                background-color: #f9f9f9;
                color: #999999;
                border-color: #f0f0f0;
            }
        """)
        self.events_list.setAlternatingRowColors(False)
        self.events_list.setSpacing(2)
        events_layout.addWidget(self.events_list)
        
        main_layout.addWidget(events_section)
        
        # Status bar with modern styling
        self.statusbar = self.statusBar()
        self.statusbar.setStyleSheet("""
            QStatusBar {
                background-color: #f8f9fa;
                border-top: 1px solid #e9ecef;
                color: #6c757d;
                font-size: 12px;
                padding: 5px 15px;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        self.statusbar.showMessage("🔄 Ready - Click refresh to load events")
    
    def init_calendar_client(self):
        """Initialize Google Calendar client"""
        try:
            credentials = self.oauth_handler.get_credentials()
            if credentials:
                self.calendar_client = GoogleCalendarClient(credentials)
                self.statusbar.showMessage("✅ Connected to Google Calendar")
            else:
                self.statusbar.showMessage("⚠️ Not connected to Google Calendar - Please check authentication")
        except Exception as e:
            self.statusbar.showMessage(f"❌ Error connecting to Google Calendar: {e}")
    
    def load_events(self):
        """Load and display calendar events"""
        if not self.calendar_client:
            self.init_calendar_client()
            if not self.calendar_client:
                return
        
        try:
            self.statusbar.showMessage("🔄 Loading events...")
            self.refresh_btn.setText("🔄 Loading...")
            self.refresh_btn.setEnabled(False)
            
            # Use QTimer to make UI responsive during loading
            QtCore.QTimer.singleShot(100, self._load_events_async)
            
        except Exception as e:
            self.statusbar.showMessage(f"❌ Error loading events: {e}")
            self.refresh_btn.setText("🔄 Refresh Events")
            self.refresh_btn.setEnabled(True)
    
    def _load_events_async(self):
        """Async helper for loading events"""
        try:
            events = self.calendar_client.list_events(max_results=20)
            
            self.events_list.clear()
            
            if not events:
                item = QtWidgets.QListWidgetItem("📭 No upcoming events found")
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEnabled)
                # Style for empty state
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
                self.events_list.addItem(item)
                self.statusbar.showMessage("📭 No upcoming events")
            else:
                from datetime import datetime, timezone
                import dateutil.parser
                
                for event in events:
                    summary = event.get('summary', 'Untitled Event')
                    start = event.get('start', {})
                    start_time_str = start.get('dateTime', start.get('date', ''))
                    
                    # Parse and format the time
                    time_display = "No time"
                    date_display = ""
                    time_icon = "🕐"
                    
                    if start_time_str:
                        try:
                            if 'T' in start_time_str:  # DateTime format
                                parsed_time = dateutil.parser.isoparse(start_time_str)
                                if parsed_time.tzinfo is None:
                                    parsed_time = parsed_time.replace(tzinfo=timezone.utc)
                                
                                local_time = parsed_time.astimezone()
                                now = datetime.now(timezone.utc).astimezone()
                                
                                # Determine time icon based on time of day
                                hour = local_time.hour
                                if 6 <= hour < 12:
                                    time_icon = "🌅"
                                elif 12 <= hour < 18:
                                    time_icon = "☀️"
                                elif 18 <= hour < 22:
                                    time_icon = "🌆"
                                else:
                                    time_icon = "🌙"
                                
                                # Format date and time
                                if local_time.date() == now.date():
                                    date_display = "Today"
                                elif local_time.date() == (now.date() + timedelta(days=1)):
                                    date_display = "Tomorrow"
                                else:
                                    date_display = local_time.strftime("%A, %B %d")
                                
                                time_display = local_time.strftime("%I:%M %p").lstrip('0')
                                
                            else:  # Date only format (all-day event)
                                parsed_date = dateutil.parser.isoparse(start_time_str).date()
                                now_date = datetime.now().date()
                                time_icon = "📅"
                                
                                if parsed_date == now_date:
                                    date_display = "Today"
                                elif parsed_date == now_date + timedelta(days=1):
                                    date_display = "Tomorrow"
                                else:
                                    date_display = parsed_date.strftime("%A, %B %d")
                                
                                time_display = "All day"
                                
                        except Exception as parse_error:
                            print(f"Error parsing time: {parse_error}")
                            time_display = start_time_str
                    
                    # Create rich text for the item
                    item_text = f"{time_icon} {summary}\n📍 {date_display} at {time_display}"
                    
                    item = QtWidgets.QListWidgetItem(item_text)
                    
                    # Add tooltip with full event details
                    description = event.get('description', '')
                    location = event.get('location', '')
                    tooltip_parts = [f"Event: {summary}"]
                    if location:
                        tooltip_parts.append(f"Location: {location}")
                    if description:
                        tooltip_parts.append(f"Description: {description[:100]}{'...' if len(description) > 100 else ''}")
                    item.setToolTip('\n'.join(tooltip_parts))
                    
                    self.events_list.addItem(item)
                
                self.statusbar.showMessage(f"✅ Loaded {len(events)} events successfully")
            
            self.refresh_btn.setText("🔄 Refresh Events")
            self.refresh_btn.setEnabled(True)
            
        except Exception as e:
            self.events_list.clear()
            error_item = QtWidgets.QListWidgetItem(f"❌ Error loading events: {str(e)}")
            error_item.setFlags(error_item.flags() & ~QtCore.Qt.ItemIsEnabled)
            self.events_list.addItem(error_item)
            
            self.statusbar.showMessage(f"❌ Error loading events: {e}")
            self.refresh_btn.setText("🔄 Retry")
            self.refresh_btn.setEnabled(True)
    
    def closeEvent(self, event):
        """Override close event to hide instead of closing"""
        event.ignore()
        self.hide()

class SystemTray(QtWidgets.QSystemTrayIcon):
    """System tray implementation for Calendar Now"""
    
    def __init__(self, oauth_handler, parent=None):
        # Load tray icon
        icon_path = resource_path('resources/icons/tray_icon.png')
        if not os.path.exists(icon_path):
            # fallback to svg during dev if png not present
            alt_path = resource_path('resources/icons/tray_icon.svg')
            if os.path.exists(alt_path):
                icon = QtGui.QIcon(alt_path)
            else:
                # Create a simple default icon if file doesn't exist
                pixmap = QtGui.QPixmap(16, 16)
                pixmap.fill(QtGui.QColor('blue'))
                icon = QtGui.QIcon(pixmap)
        else:
            icon = QtGui.QIcon(icon_path)
        
        super().__init__(icon, parent)

        self.oauth_handler = oauth_handler
        self.settings_manager = SettingsManager()
        # Share the same SettingsManager with NotificationManager so changes take effect immediately
        self.notification_manager = NotificationManager(self, settings_manager=self.settings_manager)
        
        # Main window and task display
        self.main_window = None
        self.task_display = None
        self.calendar_client = None
        
        # Initialize calendar client
        self.init_calendar_client()
        
        # Calendar sync timer
        self.sync_timer = QtCore.QTimer()
        self.sync_timer.timeout.connect(self.sync_calendar)
        
        self.setup_context_menu()
        self.setup_signals()
        self.start_sync_timer()
        
        # Show tray icon
        self.show()
        
        # Show initial notification
        if self.isSystemTrayAvailable():
            self.showMessage(
                "Calendar Now",
                "Application started and running in system tray",
                QtWidgets.QSystemTrayIcon.Information,
                3000
            )
    
    def init_calendar_client(self):
        """Initialize Google Calendar client"""
        try:
            credentials = self.oauth_handler.get_credentials()
            if credentials:
                self.calendar_client = GoogleCalendarClient(credentials)
                print("Calendar client initialized successfully")
            else:
                print("No valid credentials found for calendar client")
        except Exception as e:
            print(f"Error initializing calendar client: {e}")
    
    def show_task_display(self):
        """Show or create the task display window"""
        if self.task_display is None and self.calendar_client:
            # Run the task display in a separate thread
            import threading
            
            def run_task_display():
                self.task_display = TaskDisplayWindow(self.calendar_client, self.settings_manager)
                self.task_display.run()
            
            thread = threading.Thread(target=run_task_display)
            thread.daemon = True
            thread.start()
            
        elif self.task_display:
            self.task_display.show_window()
    
    def hide_task_display(self):
        """Hide the task display window"""
        if self.task_display:
            self.task_display.hide_window()
    
    def setup_context_menu(self):
        """Setup the context menu for tray icon"""
        self.context_menu = QtWidgets.QMenu()

        # Show/Hide task display
        task_display_action = self.context_menu.addAction("Show Task Display")
        task_display_action.triggered.connect(self.show_task_display)

        # Open calendar action
        open_action = self.context_menu.addAction("Open Calendar")
        open_action.setIcon(QtGui.QIcon(resource_path("resources/icons/app_icon.png")))
        open_action.triggered.connect(self.show_main_window)

        self.context_menu.addSeparator()

        # Quick sync action
        sync_action = self.context_menu.addAction("Sync Now")
        sync_action.triggered.connect(self.sync_calendar)

        # Settings submenu
        settings_menu = self.context_menu.addMenu("Settings")

        # Account settings
        account_action = settings_menu.addAction("Account Settings")
        account_action.triggered.connect(self.show_account_settings)

        # Notification settings
        notification_action = settings_menu.addAction("Notifications")
        notification_action.triggered.connect(self.show_notification_settings)

        # General settings
        general_action = settings_menu.addAction("General")
        general_action.triggered.connect(self.show_general_settings)

        self.context_menu.addSeparator()

        # About action
        about_action = self.context_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

        # Exit action
        exit_action = self.context_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)

        self.setContextMenu(self.context_menu)
    
    def setup_signals(self):
        """Setup signal connections"""
        self.activated.connect(self.on_tray_icon_activated)
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QtWidgets.QSystemTrayIcon.Trigger:  # Left click
            self.show_main_window()
        elif reason == QtWidgets.QSystemTrayIcon.DoubleClick:  # Double click
            self.show_main_window()
    
    def show_main_window(self):
        """Show or create the main window"""
        if self.main_window is None:
            self.main_window = MainWindow(self.oauth_handler)
        
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()
    
    def hide_main_window(self):
        """Hide the main window"""
        if self.main_window:
            self.main_window.hide()
    
    def start_sync_timer(self):
        """Start the automatic calendar sync timer"""
        sync_interval_ms = 1 * 60 * 1000  # 1 minute
        self.sync_timer.start(sync_interval_ms)
    
    def sync_calendar(self):
        """Sync calendar data and check for updates"""
        try:
            credentials = self.oauth_handler.get_credentials()
            if not credentials:
                return
            
            # Refresh credentials if needed
            if credentials.expired and credentials.refresh_token:
                self.oauth_handler.refresh_credentials()
                credentials = self.oauth_handler.get_credentials()
            
            # Initialize calendar client if needed
            calendar_client = GoogleCalendarClient(credentials)
            
            # Get upcoming events (next hour)
            events = calendar_client.get_upcoming_events(hours=1)
            
            # Check for notifications
            self.notification_manager.check_event_notifications(events)
            
            # Update main window if visible
            if self.main_window and self.main_window.isVisible():
                self.main_window.load_events()
                
        except Exception as e:
            print(f"Sync error: {e}")
    
    def show_account_settings(self):
        """Show account settings dialog"""
        dialog = AccountSettingsDialog(self.oauth_handler, self.context_menu)
        dialog.exec_()
    
    def show_notification_settings(self):
        """Show notification settings dialog"""
        dialog = NotificationSettingsDialog(self.settings_manager, self.context_menu)
        dialog.exec_()
    
    def show_general_settings(self):
        """Show general settings dialog"""
        dialog = GeneralSettingsDialog(self.settings_manager, self.context_menu)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Ask the existing Tk overlay to reload settings on its own thread
            if self.task_display:
                try:
                    self.task_display.request_settings_reload()
                except Exception:
                    # Fallback: recreate if reload command cannot be enqueued
                    try:
                        self.task_display.close_window()
                    except Exception:
                        pass
                    self.task_display = None
                    self.show_task_display()
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            None,
            "About Calendar Now",
            """
            <h3>Calendar Now</h3>
            <p>Version 1.0.0</p>
            <p>A user-friendly application for managing Google Calendar events.</p>
            <p>Built with PyQt5 and Google Calendar API</p>
            """
        )
    
    def exit_application(self):
        """Exit the application"""
        self.sync_timer.stop()
        if self.main_window:
            self.main_window.close()
        QtWidgets.QApplication.quit()

class AccountSettingsDialog(QtWidgets.QDialog):
    """Dialog for managing account settings"""
    
    def __init__(self, oauth_handler, parent=None):
        super().__init__(parent)
        self.oauth_handler = oauth_handler
        self.setWindowTitle("Account Settings")
        self.setFixedSize(400, 300)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Account info
        credentials = oauth_handler.get_credentials()
        if credentials:
            info_label = QtWidgets.QLabel("✓ Google account connected")
            info_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            info_label = QtWidgets.QLabel("✗ No Google account connected")
            info_label.setStyleSheet("color: red; font-weight: bold;")
        
        layout.addWidget(info_label)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        
        if credentials:
            disconnect_btn = QtWidgets.QPushButton("Disconnect Account")
            disconnect_btn.clicked.connect(self.disconnect_account)
            btn_layout.addWidget(disconnect_btn)
        
        reconnect_btn = QtWidgets.QPushButton("Connect/Reconnect Account")
        reconnect_btn.clicked.connect(self.reconnect_account)
        btn_layout.addWidget(reconnect_btn)
        
        layout.addLayout(btn_layout)
        
        # Close button
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def disconnect_account(self):
        """Disconnect Google account"""
        reply = QtWidgets.QMessageBox.question(
            self, "Disconnect Account",
            "Are you sure you want to disconnect your Google account?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.oauth_handler.revoke_credentials()
            self.accept()
    
    def reconnect_account(self):
        """Reconnect Google account"""
        wizard = SetupWizard(self.oauth_handler)
        wizard.exec_()
        self.accept()

class NotificationSettingsDialog(QtWidgets.QDialog):
    """Dialog for notification settings"""

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Notification Settings")
        self.setFixedSize(300, 200)

        layout = QtWidgets.QVBoxLayout()

        # Enable notifications checkbox
        self.enable_notifications = QtWidgets.QCheckBox("Enable notifications")
        self.enable_notifications.setChecked(settings_manager.get_setting('notifications_enabled', True))
        layout.addWidget(self.enable_notifications)

        # Notification time
        time_layout = QtWidgets.QHBoxLayout()
        time_layout.addWidget(QtWidgets.QLabel("Notify before event:"))

        self.notify_minutes = QtWidgets.QSpinBox()
        # Allow 0 minutes to support notifications at the exact event start time
        self.notify_minutes.setRange(0, 60)
        self.notify_minutes.setSpecialValueText("At start")
        self.notify_minutes.setValue(settings_manager.get_setting('notification_minutes', 15))
        self.notify_minutes.setSuffix(" minutes")
        time_layout.addWidget(self.notify_minutes)

        layout.addLayout(time_layout)

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()

        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def save_settings(self):
        """Save notification settings"""
        self.settings_manager.set_setting('notifications_enabled', self.enable_notifications.isChecked())
        self.settings_manager.set_setting('notification_minutes', self.notify_minutes.value())
        self.accept()

class GeneralSettingsDialog(QtWidgets.QDialog):
    """Dialog for general settings with per-section overlay styles"""
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("General Settings")
        self.resize(420, 520)

        main_layout = QtWidgets.QVBoxLayout(self)

        # Run on startup and sync interval
        top_group = QtWidgets.QGroupBox("General")
        top_form = QtWidgets.QFormLayout()

        self.run_on_startup = QtWidgets.QCheckBox("Run on system startup")
        self.run_on_startup.setChecked(settings_manager.get_setting('start_with_windows', False))
        top_form.addRow(self.run_on_startup)

        self.sync_interval = QtWidgets.QSpinBox()
        self.sync_interval.setRange(1, 60)
        current_interval = settings_manager.get_setting('sync_interval', 60000) // 60000
        self.sync_interval.setValue(current_interval)
        self.sync_interval.setSuffix(" minutes")
        top_form.addRow("Sync interval:", self.sync_interval)

        top_group.setLayout(top_form)
        main_layout.addWidget(top_group)

        # Background color
        bg_group = QtWidgets.QGroupBox("Background")
        bg_form = QtWidgets.QFormLayout()
        self.bg_color_label = QtWidgets.QLabel(settings_manager.get_setting('bg_color', '#000000'))
        self.bg_color_btn = QtWidgets.QPushButton("Select Color")
        self.bg_color_btn.clicked.connect(self._pick_bg_color)
        bg_form.addRow("Background Color:", self.bg_color_btn)
        bg_form.addRow(self.bg_color_label)
        bg_group.setLayout(bg_form)
        main_layout.addWidget(bg_group)

        # Section styles
        self.section_controls = {}
        sections = [
            ("Time", 'overlay_time', {'font_family': 'Segoe UI', 'font_size': 14, 'bold': False, 'color': '#FFFFFF'}),
            ("Task", 'overlay_task', {'font_family': 'Segoe UI', 'font_size': 14, 'bold': True, 'color': '#FFFFFF'}),
            ("Ending", 'overlay_ending', {'font_family': 'Segoe UI', 'font_size': 11, 'bold': False, 'color': '#FFFFFF'})
        ]

        for title, key, defaults in sections:
            group = QtWidgets.QGroupBox(f"{title} Style")
            form = QtWidgets.QFormLayout()

            # Font family
            font_combo = QtWidgets.QFontComboBox()
            font_family = settings_manager.get_setting(key, {}).get('font_family', defaults['font_family'])
            font_combo.setCurrentFont(QtGui.QFont(font_family))
            form.addRow("Font:", font_combo)

            # Font size
            size_spin = QtWidgets.QSpinBox()
            size_spin.setRange(8, 72)
            size_spin.setValue(settings_manager.get_setting(key, {}).get('font_size', defaults['font_size']))
            form.addRow("Size:", size_spin)

            # Bold
            bold_chk = QtWidgets.QCheckBox("Bold")
            bold_chk.setChecked(settings_manager.get_setting(key, {}).get('bold', defaults['bold']))
            form.addRow(bold_chk)

            # Color
            color_label = QtWidgets.QLabel(settings_manager.get_setting(key, {}).get('color', defaults['color']))
            color_btn = QtWidgets.QPushButton("Select Color")
            color_btn.clicked.connect(lambda _=None, lbl=color_label: self._pick_color(lbl))
            form.addRow("Text Color:", color_btn)
            form.addRow(color_label)

            group.setLayout(form)
            main_layout.addWidget(group)

            self.section_controls[key] = {
                'font_combo': font_combo,
                'size_spin': size_spin,
                'bold_chk': bold_chk,
                'color_label': color_label
            }

        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch(1)
        reset_btn = QtWidgets.QPushButton("Reset to Defaults")
        reset_btn.setToolTip("Revert all fields to app defaults (does not save until you click Save)")
        reset_btn.clicked.connect(self.reset_to_defaults)
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(reset_btn)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        main_layout.addLayout(btn_layout)

    def reset_to_defaults(self):
        # Reset general
        self.run_on_startup.setChecked(False)
        self.sync_interval.setValue(1)
        # Reset background
        self.bg_color_label.setText('#000000')
        # Reset sections
        defaults = {
            'overlay_time': {'font_family': 'Segoe UI', 'font_size': 14, 'bold': False, 'color': '#FFFFFF'},
            'overlay_task': {'font_family': 'Segoe UI', 'font_size': 14, 'bold': True, 'color': '#FFFFFF'},
            'overlay_ending': {'font_family': 'Segoe UI', 'font_size': 11, 'bold': False, 'color': '#FFFFFF'},
        }
        for key, ctrls in self.section_controls.items():
            d = defaults[key]
            ctrls['font_combo'].setCurrentFont(QtGui.QFont(d['font_family']))
            ctrls['size_spin'].setValue(d['font_size'])
            ctrls['bold_chk'].setChecked(d['bold'])
            ctrls['color_label'].setText(d['color'])

    def _pick_bg_color(self):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            self.bg_color_label.setText(color.name())

    def _pick_color(self, label_widget: QtWidgets.QLabel):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            label_widget.setText(color.name())

    def save_settings(self):
        updates = {
            'start_with_windows': self.run_on_startup.isChecked(),
            'sync_interval': int(self.sync_interval.value()) * 60000,
            'bg_color': self.bg_color_label.text(),
        }
        for key, ctrls in self.section_controls.items():
            updates[key] = {
                'font_family': ctrls['font_combo'].currentFont().family(),
                'font_size': ctrls['size_spin'].value(),
                'bold': ctrls['bold_chk'].isChecked(),
                'color': ctrls['color_label'].text(),
            }
        # Backward-compat legacy fields follow task style
        task_payload = updates.get('overlay_task')
        if task_payload:
            updates['text_color'] = task_payload['color']
            updates['font_size'] = task_payload['font_size']

        self.settings_manager.set_settings_bulk(updates)
        self.accept()