import sys
import json
from PyQt5 import QtWidgets, QtCore, QtGui
from utils.helpers import resource_path
from auth.oauth import OAuthHandler
from auth.credentials import CredentialsManager

class SetupWizard(QtWidgets.QWizard):
    """Setup wizard for first-time users to configure Google Calendar integration"""
    
    def __init__(self, oauth_handler=None):
        super().__init__()
        if oauth_handler is None:
            credentials_manager = CredentialsManager()
            self.oauth_handler = OAuthHandler(credentials_manager)
        else:
            self.oauth_handler = oauth_handler

    self.setWindowTitle("Calendar Now - Setup")
        self.setFixedSize(500, 400)
        # Use resource_path so it works in frozen builds
        self.setWindowIcon(QtGui.QIcon(resource_path("resources/icons/app_icon.png")))

        # Add pages
        self.addPage(self.create_welcome_page())
        self.addPage(self.create_oauth_config_page())
        self.addPage(self.create_auth_page())
        self.addPage(self.create_completion_page())

        # Initially disable finish button
        self.button(QtWidgets.QWizard.FinishButton).setEnabled(False)

        # Connect page changed signal
        self.currentIdChanged.connect(self.on_page_changed)
    
    def create_welcome_page(self):
        """Create welcome page"""
        page = QtWidgets.QWizardPage()
    page.setTitle("Welcome to Calendar Now")
        page.setSubTitle("This wizard will help you set up your Google Calendar integration.")
        
        layout = QtWidgets.QVBoxLayout()
        
        # Welcome message
        welcome_text = QtWidgets.QLabel("""
        <h3>Welcome!</h3>
    <p>Calendar Now helps you manage your Google Calendar events directly from your system tray.</p>
        
        <p><b>What you'll need:</b></p>
        <ul>
            <li>A Google account with Google Calendar</li>
            <li>OAuth credentials from Google Cloud Console (we'll help you set this up)</li>
        </ul>
        
        <p>Click <b>Next</b> to begin setup.</p>
        """)
        welcome_text.setWordWrap(True)
        layout.addWidget(welcome_text)
        
        page.setLayout(layout)
        return page
    
    def create_oauth_config_page(self):
        """Create OAuth configuration page"""
        page = QtWidgets.QWizardPage()
        page.setTitle("OAuth Configuration")
        page.setSubTitle("Configure your Google OAuth credentials")
        
        layout = QtWidgets.QVBoxLayout()
        
        # Instructions
        instructions = QtWidgets.QLabel("""
        <h4>Setting up OAuth credentials:</h4>
        <ol>
            <li>Go to <a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
            <li>Create a new project or select existing one</li>
            <li>Enable the Google Calendar API</li>
            <li>Create OAuth 2.0 credentials (Desktop application)</li>
            <li>Download the credentials JSON file</li>
            <li>Either upload the file below or enter details manually</li>
        </ol>
        """)
        instructions.setWordWrap(True)
        instructions.setOpenExternalLinks(True)
        layout.addWidget(instructions)
        
        # File upload option
        file_group = QtWidgets.QGroupBox("Option 1: Upload Credentials File")
        file_layout = QtWidgets.QHBoxLayout()
        
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setPlaceholderText("Select credentials JSON file...")
        self.file_browse_btn = QtWidgets.QPushButton("Browse")
        self.file_browse_btn.clicked.connect(self.browse_credentials_file)
        
        file_layout.addWidget(self.file_path_edit)
        file_layout.addWidget(self.file_browse_btn)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Manual entry option
        manual_group = QtWidgets.QGroupBox("Option 2: Enter Manually")
        manual_layout = QtWidgets.QFormLayout()
        
        self.client_id_edit = QtWidgets.QLineEdit()
        self.client_secret_edit = QtWidgets.QLineEdit()
        self.client_secret_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        
        manual_layout.addRow("Client ID:", self.client_id_edit)
        manual_layout.addRow("Client Secret:", self.client_secret_edit)
        
        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)
        
        # Test configuration button
        self.test_config_btn = QtWidgets.QPushButton("Test Configuration")
        self.test_config_btn.clicked.connect(self.test_oauth_config)
        layout.addWidget(self.test_config_btn)
        
        # Status label
        self.config_status_label = QtWidgets.QLabel("")
        layout.addWidget(self.config_status_label)
        
        page.setLayout(layout)
        
        # Check for existing credentials.json in root directory
        self.check_existing_credentials()
        
        return page
    
    def create_auth_page(self):
        """Create authentication page"""
        page = QtWidgets.QWizardPage()
        page.setTitle("Google Authentication")
        page.setSubTitle("Authenticate with your Google account")
        
        layout = QtWidgets.QVBoxLayout()
        
        # Instructions
        auth_instructions = QtWidgets.QLabel("""
        <p>Click the button below to authenticate with your Google account.</p>
    <p>This will open your web browser where you can sign in and grant permissions to Calendar Now.</p>
        """)
        auth_instructions.setWordWrap(True)
        layout.addWidget(auth_instructions)
        
        # Authentication button
        self.auth_button = QtWidgets.QPushButton("Authenticate with Google")
        self.auth_button.setMinimumHeight(40)
        self.auth_button.clicked.connect(self.perform_authentication)
        layout.addWidget(self.auth_button)
        
        # Progress indicator
        self.auth_progress = QtWidgets.QProgressBar()
        self.auth_progress.setVisible(False)
        layout.addWidget(self.auth_progress)
        
        # Status label
        self.auth_status_label = QtWidgets.QLabel("")
        layout.addWidget(self.auth_status_label)
        
        layout.addStretch()
        page.setLayout(layout)
        return page
    
    def create_completion_page(self):
        """Create completion page"""
        page = QtWidgets.QWizardPage()
        page.setTitle("Setup Complete")
        page.setSubTitle("Your Google Calendar integration is ready!")
        
        layout = QtWidgets.QVBoxLayout()
        
        completion_text = QtWidgets.QLabel("""
        <h3>Congratulations!</h3>
    <p>Your Calendar Now has been successfully configured.</p>
        
        <p><b>What happens next:</b></p>
        <ul>
            <li>The app will start in your system tray</li>
            <li>Right-click the tray icon to access options</li>
            <li>Your calendar events will sync automatically</li>
        </ul>
        
        <p>Click <b>Finish</b> to complete setup and start using the app.</p>
        """)
        completion_text.setWordWrap(True)
        layout.addWidget(completion_text)
        
        page.setLayout(layout)
        return page
    
    def check_existing_credentials(self):
        """Check for existing credentials.json file in project root"""
        import os
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        credentials_path = os.path.join(project_root, "credentials.json")
        
        if os.path.exists(credentials_path):
            self.file_path_edit.setText(credentials_path)
            self.load_credentials_from_file(credentials_path)
            self.config_status_label.setText("✓ Found existing credentials.json file")
            self.config_status_label.setStyleSheet("color: green;")
    
    def browse_credentials_file(self):
        """Browse for credentials JSON file"""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Google OAuth Credentials", "", "JSON Files (*.json)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
            self.load_credentials_from_file(file_path)
    
    def load_credentials_from_file(self, file_path):
        """Load credentials from JSON file"""
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
            
            # Extract client info (handles both web and installed app types)
            client_info = config.get('web') or config.get('installed', {})
            
            if not client_info:
                self.config_status_label.setText("✗ Invalid credentials file format")
                self.config_status_label.setStyleSheet("color: red;")
                return
            
            self.client_id_edit.setText(client_info.get('client_id', ''))
            self.client_secret_edit.setText(client_info.get('client_secret', ''))
            
            # Auto-save the configuration
            self.test_oauth_config()
            
        except Exception as e:
            self.config_status_label.setText(f"✗ Error loading file: {str(e)}")
            self.config_status_label.setStyleSheet("color: red;")
    
    def test_oauth_config(self):
        """Test OAuth configuration"""
        client_id = self.client_id_edit.text().strip()
        client_secret = self.client_secret_edit.text().strip()
        
        if not client_id or not client_secret:
            self.config_status_label.setText("✗ Please enter both Client ID and Client Secret")
            self.config_status_label.setStyleSheet("color: red;")
            return
        
        try:
            # Save configuration in web format (works for desktop apps)
            config = {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "project_id": "calendar-now",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "redirect_uris": ["http://localhost:8080/callback"]
                }
            }
            
            success = self.oauth_handler.credentials_manager.save_client_config(config)
            if success:
                self.config_status_label.setText("✓ Configuration saved successfully")
                self.config_status_label.setStyleSheet("color: green;")
                # Enable the Next button
                self.button(QtWidgets.QWizard.NextButton).setEnabled(True)
            else:
                self.config_status_label.setText("✗ Failed to save configuration")
                self.config_status_label.setStyleSheet("color: red;")
                
        except Exception as e:
            self.config_status_label.setText(f"✗ Error: {str(e)}")
            self.config_status_label.setStyleSheet("color: red;")
    
    def perform_authentication(self):
        """Start authentication process"""
        self.auth_button.setEnabled(False)
        self.auth_progress.setVisible(True)
        self.auth_status_label.setText("Starting authentication...")
        
        # Use QThread instead of QTimer for better threading
        from PyQt5.QtCore import QThread, pyqtSignal
        
        class AuthThread(QThread):
            finished = pyqtSignal(bool)
            
            def __init__(self, oauth_handler):
                super().__init__()
                self.oauth_handler = oauth_handler
            
            def run(self):
                try:
                    success = self.oauth_handler.perform_authentication()
                    self.finished.emit(success)
                except Exception as e:
                    print(f"Auth thread error: {e}")
                    self.finished.emit(False)
        
        self.auth_thread = AuthThread(self.oauth_handler)
        self.auth_thread.finished.connect(self._on_authentication_finished)
        self.auth_thread.start()
    
    def _on_authentication_finished(self, success):
        """Handle authentication completion"""
        try:
            print(f"Setup wizard: Authentication thread finished with result: {success}")  # Debug
            
            self.auth_progress.setVisible(False)
            self.auth_button.setEnabled(True)
            
            if success:
                print("Setup wizard: Checking if credentials were saved...")  # Debug
                # Double-check that credentials were actually saved
                has_valid_creds = self.oauth_handler.credentials_manager.has_valid_credentials()
                print(f"Setup wizard: Has valid credentials: {has_valid_creds}")  # Debug
                
                if has_valid_creds:
                    print("Setup wizard: Authentication successful!")  # Debug
                    self.auth_status_label.setText("✓ Authentication successful!")
                    self.auth_status_label.setStyleSheet("color: green;")
                    self.button(QtWidgets.QWizard.NextButton).setEnabled(True)
                else:
                    print("Setup wizard: Authentication completed but credentials not saved!")  # Debug
                    self.auth_status_label.setText("✗ Authentication completed but credentials not saved properly.")
                    self.auth_status_label.setStyleSheet("color: red;")
            else:
                print("Setup wizard: Authentication failed")  # Debug
                self.auth_status_label.setText("✗ Authentication failed. Please try again.")
                self.auth_status_label.setStyleSheet("color: red;")
                
        except Exception as e:
            print(f"Setup wizard: Exception in authentication finished handler: {e}")  # Debug
            self.auth_progress.setVisible(False)
            self.auth_button.setEnabled(True)
            self.auth_status_label.setText(f"✗ Error: {str(e)}")
            self.auth_status_label.setStyleSheet("color: red;")
    
    def on_page_changed(self, page_id):
        """Handle page changes"""
        if page_id == 2:  # Auth page
            # Check if OAuth config is ready
            if not self.oauth_handler.credentials_manager.has_client_config():
                self.auth_button.setEnabled(False)
                self.auth_status_label.setText("Please configure OAuth credentials first")
                self.auth_status_label.setStyleSheet("color: orange;")
            elif self.oauth_handler.credentials_manager.has_valid_credentials():
                # Already authenticated
                self.auth_button.setText("Re-authenticate")
                self.auth_button.setEnabled(True)
                self.auth_status_label.setText("✓ Already authenticated! You can continue or re-authenticate if needed.")
                self.auth_status_label.setStyleSheet("color: green;")
                self.button(QtWidgets.QWizard.NextButton).setEnabled(True)
            else:
                self.auth_button.setEnabled(True)
                self.auth_status_label.setText("Click to authenticate with your Google account")
                self.auth_status_label.setStyleSheet("color: black;")
        elif page_id == 3:  # Completion page
            self.button(QtWidgets.QWizard.FinishButton).setEnabled(True)

