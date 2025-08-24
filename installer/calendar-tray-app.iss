; Inno Setup Script for Calendar Tray App
; Requires Inno Setup 6.x (https://jrsoftware.org/isinfo.php)

#define MyAppName "Calendar Now"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Calendar Now Team"
#define MyAppURL "https://github.com/your-username/calendar-now"
#define MyAppExeName "CalendarNow.exe"

[Setup]
AppId={{8E2B6A28-6E3A-4C7A-9B2C-5E7E0B97F2A0}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableStartupPrompt=yes
DisableDirPage=no
DisableProgramGroupPage=no
LicenseFile=..\TERMS.md
InfoBeforeFile=..\PRIVACY.md
OutputBaseFilename=CalendarNow-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64
SetupIconFile=..\resources\icons\app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked
Name: "autoStart"; Description: "Start {#MyAppName} when Windows starts"; GroupDescription: "Startup:"; Flags: unchecked

[Files]
; Package the portable one-file EXE so users can run it standalone
Source: "..\dist\CalendarNow.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion
; Include OAuth client config next to the EXE (you must place the file before compiling)
Source: "..\resources\credentials\client_config.json"; DestDir: "{app}"; Flags: ignoreversion; Check: FileExists('..\resources\credentials\client_config.json')

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Registry]
; Auto-start at login (current user) if selected
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "CalendarNow"; ValueData: """{app}\{#MyAppExeName}"""; Tasks: autoStart
