# Calendar Now
 
[![Build Windows EXE and Installer](https://github.com/bharatvansh/calendar-now/actions/workflows/windows-build.yml/badge.svg)](https://github.com/bharatvansh/calendar-now/actions/workflows/windows-build.yml)
Manage your Google Calendar from the system tray with a lightweight, polished desktop app built with PyQt5. It shows upcoming events, notifies you at the right time, and includes a minimal always-on-top overlay for your current task.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Highlights

- System tray app for Windows, macOS, and Linux
- First-time setup wizard with secure Google OAuth 2.0
- Event notifications (default: at event start; configurable 0–60 minutes)
- Modern “Calendar View” window with upcoming events
- Always-on-top “Task Display” overlay (shows current/next event, time remaining)
- Auto-sync in the background (default every 1 minute)
- Encrypted credential storage (Fernet)

## Requirements

- Python `3.7+`
- A Google account with Calendar enabled
- A Google Cloud project with the Google Calendar API enabled

## Install

Recommended for Windows PowerShell:

```powershell
# 1) Clone
git clone https://github.com/your-username/calendar-now.git
cd calendar-now

# 2) Create & activate a virtual environment
py -3 -m venv .venv
. .\.venv\Scripts\Activate.ps1

# 3) Install dependencies
python -m pip install -r requirements.txt

# 4) Install the app (editable/development mode)
python -m pip install -e .
```

After installation you can start the app with:

```powershell
calendar-now
# or (GUI entry point)
calendar-now-gui
```

Tip: When developing or using advanced flags, run the module directly:

```powershell
python .\src\main.py --help
```

## First-time Setup (Google OAuth)

1) Open the app: run `calendar-now`. The Setup Wizard appears automatically on first run.

2) Create OAuth 2.0 credentials in Google Cloud Console:
- Visit https://console.cloud.google.com/
- Create/select a project
- Enable “Google Calendar API” (APIs & Services → Library)
- Create Credentials → OAuth client ID → Application type: Desktop
- Add redirect URI: `http://localhost:8080/callback`
- Download the credentials JSON

3) Provide credentials to the wizard:
- Option A: Click “Browse” and select your credentials JSON
- Option B: Paste Client ID and Client Secret manually

4) Click “Authenticate with Google” to sign in and grant access. A local callback server on port 8080 completes the flow.

5) Done. The tray icon appears; right‑click it for options.

Note: If you place a file named `credentials.json` in the project root, the wizard will auto-detect it and prefill your client details.

## Usage

- Left‑click tray icon: Open the Calendar View window
- Right‑click tray icon: Open menu with actions

Tray menu:
- Show Task Display: Shows the always-on-top overlay with current/next event
- Open Calendar: Opens the Calendar View window
- Sync Now: Immediately refresh events and notifications
- Settings → Account: Connect/reconnect or disconnect your Google account
- Settings → Notifications: Enable/disable and set minutes before start
- Settings → General: Sync interval, overlay fonts/colors, background color
- About: App information
- Exit: Quit the app

Calendar View window:
- Shows upcoming events with readable date/time
- “Refresh Events” button fetches latest data

Task Display overlay:
- Always on top; draggable
- Left shows current local time; right shows current task and “Ending in …” or next event
- Right‑click for a small context menu (Refresh, Reload Styles, Settings hint, Hide, Close)

## Configuration

Settings are saved per user.

- Windows: `%APPDATA%\CalendarNow\settings.json`
- macOS/Linux: `~/.local/share/CalendarNow/settings.json`

Common settings and defaults (subset):

- `notifications_enabled`: `true`
- `notification_minutes`: `0` (At start; set `1-60` for heads‑up minutes)
- `sync_interval`: `60000` (milliseconds; 1 minute)
- `minimize_to_tray`: `true`
- `bg_color`: `"#000000"` (overlay background)
- Overlay styles (fonts/colors), each a dict:
   - `overlay_time`: `{ font_family, font_size, bold, color }`
   - `overlay_task`: `{ font_family, font_size, bold, color }`
   - `overlay_ending`: `{ font_family, font_size, bold, color }`

Credential storage (per user):

- Windows: `%APPDATA%\CalendarNow\`
- macOS/Linux: `~/.local/share/CalendarNow/`

Files created by the app:

- `client_config.json`: your OAuth client details
- `credentials.json`: your tokens (encrypted)
- `.key`: the encryption key for credentials (Fernet)

## Command‑line flags (source run)

Flags are handled when you run the app via `python src/main.py`:

```powershell
python .\src\main.py --help            # Show help
python .\src\main.py --version         # Show version
python .\src\main.py --debug           # Enable debug logs for this run
python .\src\main.py --reset-settings  # Reset settings to defaults
python .\src\main.py --reset-auth      # Revoke & remove stored credentials
python .\src\main.py --create-shortcut # Create a Desktop shortcut (Windows)
```

Note: The packaged entry points `calendar-now` / `calendar-now-gui` do not process these flags. For flags, run `src/main.py` directly.

To enable debug logs with the packaged command, set an environment variable for the session:

```powershell
$env:DEBUG_MODE = "1"
calendar-now
```

## Troubleshooting

System tray not available
- Some desktop environments disable or lack a system tray. Enable it or try a different DE.

OAuth callback times out or fails
- Ensure redirect URI exactly matches `http://localhost:8080/callback`
- Make sure port 8080 is not blocked or in use
- Confirm Google Calendar API is enabled in your project
- Re-run the wizard: Settings → Account → Connect/Reconnect Account

No notifications
- Check Settings → Notifications → “Enable notifications”
- Remember: all-day events are skipped for pop-up notifications
- If `notification_minutes` is `0`, notifications fire “at start” (with a 1‑minute tolerance)

Start with Windows
- Toggle in Settings → General. If it doesn’t take effect, you can add the app to Startup Apps (Windows Settings) or place a shortcut in `shell:startup`.

Resetting
- From source: run with `--reset-auth` and/or `--reset-settings`
- Manual: close the app and delete the files under your app data folder listed above

## Development

Run locally (from the repo):

```powershell
. .\.venv\Scripts\Activate.ps1
python .\src\main.py --debug
```

Run tests:

```powershell
python -m unittest -v
```

Notes:
- Some legacy tests are skipped on purpose; the overlay settings tests run.
- The project uses a `src/` layout; packaging is defined in `setup.py`.

## License

MIT. See repository for details.

## Legal

- Privacy Policy: see `PRIVACY.md`
- Terms of Use: see `TERMS.md`

Tip for Google OAuth verification: Host these pages at stable HTTPS URLs on a verified domain and add that domain under “Authorized domains” in the Google Cloud Console OAuth consent screen.