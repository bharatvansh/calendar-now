; Inno Setup script for Calendar Now
[Setup]
AppName=Calendar Now
AppVerName=Calendar Now
DefaultDirName={pf}\Calendar Now
DefaultGroupName=Calendar Now
OutputBaseFilename=CalendarNow-Setup

[Files]
Source: "..\build\main\CalendarNow.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Calendar Now"; Filename: "{app}\CalendarNow.exe"
Name: "{commondesktop}\Calendar Now"; Filename: "{app}\CalendarNow.exe"

[Run]
Filename: "{app}\CalendarNow.exe"; Description: "Launch Calendar Now"; Flags: nowait postinstall
