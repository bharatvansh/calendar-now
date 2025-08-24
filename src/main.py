import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from auth.oauth import OAuthHandler
from auth.credentials import CredentialsManager
from ui.setup_wizard import SetupWizard
from ui.tray import SystemTray
from config.settings import SettingsManager, Config

def check_system_tray_available():
    """Check if system tray is available"""
    from PyQt5.QtWidgets import QSystemTrayIcon
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            "System Tray",
            "System tray is not available on this system."
        )
        return False
    return True

def main():
    """Main application entry point"""
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(Config.APP_NAME)
    app.setApplicationVersion(Config.APP_VERSION)
    app.setOrganizationName(Config.APP_AUTHOR)
    
    # Don't quit when last window is closed (for tray app)
    app.setQuitOnLastWindowClosed(False)
    
    # Check if system tray is available
    if not check_system_tray_available():
        return 1
    
    try:
        # Initialize components
        settings_manager = SettingsManager()
        credentials_manager = CredentialsManager()
        oauth_handler = OAuthHandler(credentials_manager)
        
        # Bypass Setup Wizard: auto-authenticate using bundled credentials if needed
        if oauth_handler.is_first_run():
            # Attempt authentication silently (will open browser for Google consent on first run)
            ok = oauth_handler.perform_authentication()
            if not ok or not oauth_handler.credentials_manager.has_valid_credentials():
                QMessageBox.critical(
                    None,
                    "Authentication Error",
                    "Failed to authenticate with Google Calendar. Please check your internet connection or try again later."
                )
                return 1
        
        # Create system tray and task display
        system_tray = SystemTray(oauth_handler)
        
        if not system_tray.isVisible():
            QMessageBox.critical(
                None,
                "System Tray",
                "Could not create system tray icon."
            )
            return 1
        
        # Show the main task display window
        system_tray.show_task_display()
        
        # Handle startup settings
        handle_startup_settings(settings_manager)
        
        # Start the application event loop
        return app.exec_()
        
    except Exception as e:
        QMessageBox.critical(
            None,
            "Application Error",
            f"An unexpected error occurred:\n{str(e)}\n\nThe application will now exit."
        )
        return 1

def handle_startup_settings(settings_manager):
    """Handle settings that need to be applied on startup"""
    # Handle Windows startup setting
    if settings_manager.get_setting('start_with_windows', False):
        setup_windows_startup(True)

def setup_windows_startup(enable=True):
    """Setup or remove Windows startup registry entry"""
    if os.name != 'nt':  # Only for Windows
        return
    
    try:
        import winreg
        
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = Config.APP_NAME.replace(' ', '')
        executable_path = sys.executable
        
        # If running from Python script, use the script path
        if executable_path.endswith('python.exe') or executable_path.endswith('pythonw.exe'):
            script_path = os.path.abspath(__file__)
            executable_path = f'"{executable_path}" "{script_path}"'
        else:
            executable_path = f'"{executable_path}"'
        
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
            if enable:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, executable_path)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass  # Value doesn't exist, which is fine
                    
    except Exception as e:
        print(f"Error setting up Windows startup: {e}")

def create_desktop_shortcut():
    """Create a desktop shortcut (Windows only)"""
    if os.name != 'nt':
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{Config.APP_NAME}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        
        # Set shortcut properties
        if sys.executable.endswith('python.exe') or sys.executable.endswith('pythonw.exe'):
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{os.path.abspath(__file__)}"'
        else:
            shortcut.Targetpath = sys.executable
        
        shortcut.WorkingDirectory = os.path.dirname(os.path.abspath(__file__))
        shortcut.IconLocation = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'app_icon.ico')
        shortcut.Description = Config.APP_DESCRIPTION
        
        shortcut.save()
        return True
        
    except Exception as e:
        print(f"Error creating desktop shortcut: {e}")
        return False

def show_help():
    """Show command line help"""
    help_text = f"""
{Config.APP_NAME} v{Config.APP_VERSION}

Usage: python main.py [options]

Options:
  --help, -h          Show this help message
  --version, -v       Show version information
  --reset-settings    Reset all settings to defaults
  --reset-auth        Reset authentication (force re-login)
  --debug             Enable debug mode
  --create-shortcut   Create desktop shortcut (Windows only)

Examples:
  python main.py                    # Start the application normally
  python main.py --reset-auth       # Reset authentication and restart setup
  python main.py --debug            # Start with debug mode enabled

For more information, visit: {Config.PROJECT_WEBSITE}
"""
    print(help_text)

def handle_command_line_args():
    """Handle command line arguments"""
    args = sys.argv[1:]
    
    if '--help' in args or '-h' in args:
        show_help()
        return False
    
    if '--version' in args or '-v' in args:
        print(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        return False
    
    if '--reset-settings' in args:
        settings_manager = SettingsManager()
        settings_manager.reset_all_settings()
        print("Settings reset to defaults.")
    
    if '--reset-auth' in args:
        credentials_manager = CredentialsManager()
        oauth_handler = OAuthHandler(credentials_manager)
        oauth_handler.revoke_credentials()
        print("Authentication reset. Please restart the application to set up again.")
        return False
    
    if '--create-shortcut' in args:
        if create_desktop_shortcut():
            print("Desktop shortcut created successfully.")
        else:
            print("Failed to create desktop shortcut.")
        return False
    
    if '--debug' in args:
        os.environ['DEBUG_MODE'] = '1'
    
    return True

if __name__ == "__main__":
    # Handle command line arguments
    if not handle_command_line_args():
        sys.exit(0)
    
    # Start the main application
    exit_code = main()
    sys.exit(exit_code)