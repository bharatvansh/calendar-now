# Privacy Policy

Effective date: 2025-08-19

This Privacy Policy explains how Calendar Now (the “App”) handles your information.

Calendar Now is a desktop application that integrates with your Google Calendar and runs from your system tray. We designed it to process data locally on your device and to minimize data collection.

## Summary

- We do not operate a backend server; your calendar data stays on your device.
- OAuth tokens are stored locally and encrypted.
- We request only the scopes needed for calendar features.
- You control your data and can revoke access at any time.

## What data we access

If you connect a Google account, the App may access data from Google Calendar via Google’s APIs:

- Calendar events (titles, times, descriptions, locations, attendees)
- Calendar metadata (calendar list, primary calendar info)

The App uses the following OAuth scopes (minimum required):

- `https://www.googleapis.com/auth/calendar.readonly` — read events
- `https://www.googleapis.com/auth/calendar.events` — create/update/delete events (only when you use those features)

The App does not collect analytics, usage metrics, or personal data outside of your Google Calendar content required to provide features.

## How data is stored

- OAuth credentials (access/refresh tokens and client settings) are stored locally on your device in your user profile directory:
  - Windows: `%APPDATA%\\CalendarNow`  
  - macOS/Linux: `~/.local/share/CalendarNow`
- Tokens are encrypted at rest using a symmetric key (Fernet). The encryption key is generated locally and stored alongside credentials with restricted file permissions.
- Event data is kept in memory only as needed to display your calendar and notifications.

## How data is used

- To display your events, notify you about upcoming events, and provide optional features like quick add or event edits.
- No data is transmitted to us; all API calls are between your device and Google’s servers.

## Data sharing

- We do not sell, rent, or otherwise share your data with third parties.
- Google may process your data according to its own terms when you use the Google APIs.

## Your choices and controls

- You can disconnect your Google account at any time in Settings → Account, which revokes and deletes local credentials.
- You can delete the App’s local data by removing the files in the App’s data directory (see paths above).
- You can adjust notification and synchronization settings in Settings.

## Security

- Tokens are encrypted at rest.
- Writes are performed atomically to reduce the risk of corruption.
- The App requests minimal scopes to function.

## Children’s privacy

- The App is not directed to children under 13, and we do not knowingly collect personal information from children.

## Changes to this policy

We may update this Privacy Policy from time to time. Material changes will be reflected by updating the “Effective date” above. Continued use of the App after changes indicates acceptance of the updated policy.

## Contact

If you have questions about this policy or the App’s privacy practices, contact: contact@calendarnow.com
