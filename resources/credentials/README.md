This folder stores local Google OAuth credential files for development and the app's runtime.

Important:
- Never commit your real `client_config.json` or `credentials.json` to a public repository.
- The repository's `.gitignore` already excludes these files.

How to add your real credentials locally:
1) Create OAuth credentials in the Google Cloud Console (Application type: Desktop). Add `http://localhost:8080/callback` as a redirect URI.
2) Download the JSON and save it as `client_config.json` in this folder (`resources/credentials/client_config.json`).
3) Run the app and complete the OAuth flow. The tokens will be saved to `credentials.json` in the app data directory or project root (depending on run mode).

If you want to keep an example credential in the repo for documentation, use `client_config.example.json` and replace the placeholders with your values locally (do not commit the real file).