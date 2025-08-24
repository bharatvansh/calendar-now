# Building Calendar Now for Windows

## 1) Generate icons (once or after edits)

```powershell
# From repo root
python .\convert_icon.py
```

This creates PNG and ICO files in `resources\icons`.

## 2) Build the Windows EXE with PyInstaller

```powershell
pyinstaller .\main.spec
```

Output will appear in `dist\CalendarNow\CalendarNow.exe`.

Why you should not share only that EXE: this is a "one-dir" build and requires the sibling `_internal` folder. If you copy just the EXE out of its folder, it will fail with an error like "Failed to load Python DLL ... _internal\python313.dll". Use the installer below, or build a portable one-file EXE.

## 2b) Build a portable single-file EXE (optional)

If you want a standalone EXE that users can run from anywhere (no `_internal` folder), build the one-file variant:

```powershell
pyinstaller --onefile --name CalendarNow --icon resources/icons/app_icon.ico --noconsole `
	--add-data "resources/icons/*.png;resources/icons" `
	--add-data "resources/icons/*.ico;resources/icons" `
	--add-data "resources/icons/*.svg;resources/icons" `
	src/main.py
```

Output: `dist\CalendarNow.exe` (single file). This is safe to share or move by itself.

## 3) Build the Windows installer (Inno Setup)

Install Inno Setup 6+ and add its `ISCC.exe` to PATH.

```powershell
# Compile the installer script
ISCC .\installer\calendar-now.iss
```

The installer `CalendarNow-Setup.exe` will be written to the repo root by default.

## Installation behavior
- Adds program files into `C:\Program Files\Calendar Now` (default)
- Creates Start Menu shortcut
- Optional desktop shortcut
- Optional auto-start via Registry `Run` key for current user

## Notes
- The app runs as a GUI process (no console) and shows a system tray icon.
- First run triggers the setup wizard for Google authentication.
- Resources are bundled; icon paths resolved via `utils.helpers.resource_path`.

## Which file to distribute?
- Recommended: `installer\Output\CalendarNow-Setup.exe` (standard installer). This ensures all files are installed together and shortcuts are created.
- Portable alternative: `dist\CalendarNow.exe` (one-file build). Users can run it from any folder without installing.
- Do NOT distribute or move `dist\CalendarNow\CalendarNow.exe` by itself. That EXE depends on the adjacent `_internal` folder and will fail with a "Failed to load Python DLL" error if separated.
