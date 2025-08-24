import os
import json
import webbrowser
import threading
import time
import requests
from urllib.parse import parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from .credentials import CredentialsManager

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback"""
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        try:
            # Parse URL and get authorization code
            parsed_url = urlparse(self.path)
            params = parse_qs(parsed_url.query)
            
            if 'code' in params:
                # Store the authorization code in server instance
                self.server.auth_code = params['code'][0]
                print(f"OAuth callback received code: {params['code'][0][:10]}...")  # Debug
                
                # Send success response
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html>
                        <body>
                            <h2>Authentication Successful!</h2>
                            <p>You can close this window and return to the application.</p>
                            <script>window.close();</script>
                        </body>
                    </html>
                ''')
            elif 'error' in params:
                error = params['error'][0]
                print(f"OAuth callback error: {error}")  # Debug
                
                # Send error response
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f'''
                    <html>
                        <body>
                            <h2>Authentication Failed</h2>
                            <p>Error: {error}</p>
                            <p>You can close this window and try again.</p>
                        </body>
                    </html>
                '''.encode())
            else:
                print("OAuth callback: No code or error parameter found")  # Debug
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                    <html>
                        <body>
                            <h2>Invalid Request</h2>
                            <p>No authorization code received.</p>
                        </body>
                    </html>
                ''')
                
        except Exception as e:
            print(f"OAuth callback handler error: {e}")  # Debug
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h2>Server Error</h2></body></html>')
    
    def log_message(self, format, *args):
        """Suppress default HTTP server logging"""
        pass

class OAuthHandler:
    """Handle OAuth 2.0 authentication flow for Google Calendar API"""
    
    def __init__(self, credentials_manager):
        self.credentials_manager = credentials_manager
        self.scopes = [
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        self.redirect_uri = 'http://localhost:8080/callback'
        
    def is_first_run(self):
        """Check if this is the first time the app is being run"""
        return not self.credentials_manager.has_valid_credentials()
    
    def get_credentials(self):
        """Get stored credentials or None if not available"""
        return self.credentials_manager.load_credentials()
    
    def perform_authentication(self):
        """Perform OAuth authentication flow"""
        try:
            # Load client configuration
            client_config = self.credentials_manager.get_client_config()
            if not client_config:
                raise Exception("Client configuration not found. Please set up OAuth credentials.")
            
            print("Starting OAuth flow...")  # Debug
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            # Try to start local server with better error handling
            server_port = 8080
            max_retries = 5
            server = None
            
            for attempt in range(max_retries):
                try:
                    print(f"Attempting to start server on port {server_port} (attempt {attempt + 1})")
                    server = HTTPServer(('localhost', server_port), OAuthCallbackHandler)
                    server.auth_code = None
                    break
                except OSError as e:
                    if attempt == max_retries - 1:
                        raise Exception(f"Failed to start OAuth callback server after {max_retries} attempts: {e}")
                    print(f"Port {server_port} busy, waiting 2 seconds before retry...")
                    time.sleep(2)
            
            if server is None:
                raise Exception("Failed to create OAuth callback server")
            
            print(f"OAuth server started successfully on port {server_port}")
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            # Generate authorization URL and open in browser
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f"Opening browser with URL: {auth_url}")  # Debug
            webbrowser.open(auth_url)
            
            # Wait for callback
            timeout = 120  # 2 minutes timeout
            start_time = time.time()
            
            print("Waiting for authentication callback...")  # Debug
            while server.auth_code is None and (time.time() - start_time) < timeout:
                time.sleep(0.5)
            
            try:
                server.shutdown()
            except:
                pass  # Ignore shutdown errors
            
            if server.auth_code is None:
                raise Exception("Authentication timeout or user cancelled")
            
            print(f"Received auth code: {server.auth_code[:10]}...")  # Debug (partial)
            
            # Exchange authorization code for tokens
            print(f"Exchanging authorization code for tokens...")  # Debug
            
            # Create a more flexible flow that can handle scope variations
            flow_flexible = Flow.from_client_config(
                client_config,
                scopes=None,  # Don't enforce specific scopes
                redirect_uri=self.redirect_uri
            )
            
            try:
                # Try to fetch token with the flexible flow
                flow_flexible.fetch_token(code=server.auth_code)
                credentials = flow_flexible.credentials
                print("Token exchange successful with flexible flow")
                
            except Exception as token_error:
                print(f"Flexible flow also failed: {token_error}")
                
                # Last resort: manual token exchange
                client_info = client_config.get('web') or client_config.get('installed', {})
                
                token_data = {
                    'client_id': client_info['client_id'],
                    'client_secret': client_info['client_secret'],
                    'code': server.auth_code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': self.redirect_uri,
                }
                
                print("Attempting manual token exchange...")
                response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
                token_response = response.json()
                
                print(f"Manual token response: {token_response}")  # Debug
                
                if response.status_code != 200 or 'access_token' not in token_response:
                    raise Exception(f"Manual token exchange failed: {token_response}")
                
                # Create credentials manually
                credentials = Credentials(
                    token=token_response['access_token'],
                    refresh_token=token_response.get('refresh_token'),
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=client_info['client_id'],
                    client_secret=client_info['client_secret'],
                    scopes=token_response.get('scope', ' '.join(self.scopes)).split()
                )
                print("Manual token exchange successful")
            
            print("Credentials obtained, saving...")  # Debug
            
            # Save credentials
            success = self.credentials_manager.save_credentials(credentials)
            if not success:
                raise Exception("Failed to save credentials")
            
            print("Authentication completed successfully!")  # Debug
            return True
            
        except Exception as e:
            print(f"Authentication failed: {e}")
            return False
    
    def refresh_credentials(self):
        """Refresh expired credentials"""
        try:
            credentials = self.credentials_manager.load_credentials()
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                self.credentials_manager.save_credentials(credentials)
                return True
            return False
        except Exception as e:
            print(f"Failed to refresh credentials: {e}")
            return False
    
    def revoke_credentials(self):
        """Revoke and delete stored credentials"""
        try:
            credentials = self.credentials_manager.load_credentials()
            if credentials:
                # Revoke the credentials
                import requests
                requests.post('https://oauth2.googleapis.com/revoke',
                            params={'token': credentials.token},
                            headers={'content-type': 'application/x-www-form-urlencoded'})
            
            # Delete stored credentials
            self.credentials_manager.delete_credentials()
            return True
        except Exception as e:
            print(f"Failed to revoke credentials: {e}")
            return False