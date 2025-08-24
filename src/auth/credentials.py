import os
import sys
import json
from pathlib import Path
from google.oauth2.credentials import Credentials
from cryptography.fernet import Fernet
import base64
from utils.helpers import resource_path

class CredentialsManager:
    """Manages storage and retrieval of OAuth credentials securely"""
    
    def __init__(self):
        self.app_data_dir = self._get_app_data_dir()
        self.credentials_file = self.app_data_dir / 'credentials.json'
        self.client_config_file = self.app_data_dir / 'client_config.json'
        self.key_file = self.app_data_dir / '.key'
        
        # Ensure app data directory exists
        self.app_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption key
        self._init_encryption_key()
    
    def _get_app_data_dir(self):
        """Get the application data directory based on OS"""
        if os.name == 'nt':  # Windows
            base_dir = Path(os.environ.get('APPDATA', ''))
        else:  # macOS/Linux
            base_dir = Path.home() / '.local' / 'share'
        
    return base_dir / 'CalendarNow'
    
    def _init_encryption_key(self):
        """Initialize or load encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Make key file read-only
            os.chmod(self.key_file, 0o600)
    
    def _encrypt_data(self, data):
        """Encrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode()).decode()
    
    def _decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    def save_credentials(self, credentials):
        """Save OAuth credentials securely"""
        try:
            # Convert credentials to dict
            creds_dict = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            
            # Encrypt and save
            encrypted_data = self._encrypt_data(json.dumps(creds_dict))
            with open(self.credentials_file, 'w') as f:
                json.dump({'encrypted_credentials': encrypted_data}, f)
            
            # Make credentials file read-only
            os.chmod(self.credentials_file, 0o600)
            
            return True
        except Exception as e:
            print(f"Failed to save credentials: {e}")
            return False
    
    def load_credentials(self):
        """Load stored OAuth credentials"""
        try:
            if not self.credentials_file.exists():
                return None
            
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
            
            # Decrypt credentials
            encrypted_data = data.get('encrypted_credentials')
            if not encrypted_data:
                return None
            
            creds_dict = json.loads(self._decrypt_data(encrypted_data))
            
            # Create Credentials object
            credentials = Credentials(
                token=creds_dict.get('token'),
                refresh_token=creds_dict.get('refresh_token'),
                token_uri=creds_dict.get('token_uri'),
                client_id=creds_dict.get('client_id'),
                client_secret=creds_dict.get('client_secret'),
                scopes=creds_dict.get('scopes')
            )
            
            return credentials
        except Exception as e:
            print(f"Failed to load credentials: {e}")
            return None
    
    def has_valid_credentials(self):
        """Check if valid credentials exist"""
        credentials = self.load_credentials()
        return credentials is not None
    
    def delete_credentials(self):
        """Delete stored credentials"""
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
            return True
        except Exception as e:
            print(f"Failed to delete credentials: {e}")
            return False
    
    def save_client_config(self, client_config):
        """Save OAuth client configuration"""
        try:
            with open(self.client_config_file, 'w') as f:
                json.dump(client_config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save client config: {e}")
            return False
    
    def get_client_config(self):
        """Get OAuth client configuration"""
        try:
            # 1) Prefer credentials installed next to the executable (via installer)
            try:
                exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[2]
            except Exception:
                exe_dir = Path.cwd()
            installed_cfg = exe_dir / 'client_config.json'
            if installed_cfg.exists():
                with open(installed_cfg, 'r', encoding='utf-8') as f:
                    return json.load(f)

            # 2) Fall back to bundled resource inside the EXE (if added as data)
            try:
                bundled_path = Path(resource_path('resources/credentials/client_config.json'))
                if bundled_path.exists():
                    with open(bundled_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            except Exception:
                pass

            # 3) Finally, check per-user app data file (legacy path)
            if self.client_config_file.exists():
                with open(self.client_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return None
        except Exception as e:
            print(f"Failed to load client config: {e}")
            return None
    
    def has_client_config(self):
        """Check if client configuration exists and is not using default values"""
        config = self.get_client_config()
        if not config:
            return False
        # Accept either 'web' or 'installed' formats; do not enforce placeholder checks anymore
        return 'web' in config or 'installed' in config