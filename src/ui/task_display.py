"""
Task Display Window - Shows current and next events in a sleek always-on-top window
Based on the original now_task_display.py but integrated with Calendar Now
"""

import tkinter as tk
from tkinter import ttk
import math
from datetime import datetime, timedelta
import queue
from dateutil import parser, tz
from PyQt5 import QtCore


class TaskDisplayWindow:
    """Main task display window showing current and next events"""
    
    def __init__(self, calendar_client, settings_manager):
        self.calendar_client = calendar_client
        self.settings_manager = settings_manager
        self.command_queue = queue.Queue()

        self.load_settings()

        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        # Start command polling on Tk thread
        self.root.after(100, self.poll_commands)

        # Variables for dragging
        self.start_x = 0
        self.start_y = 0

        # Auto-refresh timer
        self.refresh_seconds = 30
        
    def load_settings(self):
        """Load appearance settings"""
        # Background color (global)
        self.bg_color = self.settings_manager.get_setting('bg_color', '#000000')

        # Per-section styles (with safe fallbacks)
        default_time = {
            'font_family': 'Segoe UI',
            'font_size': 14,
            'bold': False,
            'color': '#FFFFFF',
        }
        default_task = {
            'font_family': 'Segoe UI',
            'font_size': 14,
            'bold': True,
            'color': '#FFFFFF',
        }
        default_ending = {
            'font_family': 'Segoe UI',
            'font_size': 11,
            'bold': False,
            'color': '#FFFFFF',
        }

        time_style = self.settings_manager.get_setting('overlay_time', default_time) or default_time
        task_style = self.settings_manager.get_setting('overlay_task', default_task) or default_task
        ending_style = self.settings_manager.get_setting('overlay_ending', default_ending) or default_ending

        # Shallow-merge with defaults to ensure all keys exist
        self.time_style = {**default_time, **(time_style or {})}
        self.task_style = {**default_task, **(task_style or {})}
        self.ending_style = {**default_ending, **(ending_style or {})}
        # Optional debug logging
        try:
            if self.settings_manager.get_setting('debug_mode', False):
                print("[Overlay Styles] time=", self.time_style, "task=", self.task_style, "ending=", self.ending_style)
        except Exception:
            pass
        
    def setup_window(self):
        """Setup the main window properties"""
        self.root.title("Current Task")
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-topmost', True)
        self.root.resizable(True, True)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Initial size
        self.root.geometry("450x80")
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (450 // 2)
        y = 50  # Position near top of screen
        self.root.geometry(f"450x80+{x}+{y}")
        
        # Bind mouse events for dragging
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)
        
    def start_move(self, event):
        """Start window drag operation"""
        self.start_x = event.x
        self.start_y = event.y
        
    def on_move(self, event):
        """Handle window drag movement"""
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f"+{x}+{y}")
        
    def create_widgets(self):
        """Create all UI widgets"""
        # Main container with padding
        self.main_frame = tk.Frame(self.root, bg=self.bg_color)
        self.main_frame.pack(fill='both', expand=True, padx=25, pady=15)
        
        # Content container with grid layout
        self.content_frame = tk.Frame(self.main_frame, bg=self.bg_color)
        self.content_frame.pack(fill='both', expand=True)
        
        # Configure grid weights
        self.content_frame.grid_columnconfigure(0, weight=0)  # Time column - fixed width
        self.content_frame.grid_columnconfigure(1, weight=0)  # Separator - fixed width
        self.content_frame.grid_columnconfigure(2, weight=1)  # Task column - expandable
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Left side - Time (fixed width)
        self.time_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.time_frame.grid(row=0, column=0, sticky='nsw', padx=(0, 10))
        
        self.time_label = tk.Label(
            self.time_frame,
            text="12:34\nPM",
            bg=self.bg_color,
            fg=self.time_style['color'],
            font=(
                self.time_style['font_family'],
                self.time_style['font_size'],
                'bold' if self.time_style.get('bold') else 'normal'
            ),
            justify='center',
            anchor='center'
        )
        self.time_label.pack(expand=True, fill='both')
        
        # Separator line (fixed width)
        self.separator = tk.Frame(self.content_frame, bg=self.task_style['color'], width=2)
        self.separator.grid(row=0, column=1, sticky='ns', padx=(0, 10))
        self.separator.grid_propagate(False)
        
        # Right side - Task info (expandable)
        self.task_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        self.task_frame.grid(row=0, column=2, sticky='nsew')
        
        # Configure task frame grid
        self.task_frame.grid_rowconfigure(0, weight=1)
        self.task_frame.grid_rowconfigure(1, weight=1)
        self.task_frame.grid_columnconfigure(0, weight=1)
        
        self.task_label = tk.Label(
            self.task_frame,
            text="Loading Task",
            bg=self.bg_color,
            fg=self.task_style['color'],
            font=(
                self.task_style['font_family'],
                self.task_style['font_size'],
                'bold' if self.task_style.get('bold') else 'normal'
            ),
            anchor='w',
            justify='left'
        )
        self.task_label.grid(row=0, column=0, sticky='ew', pady=(0, 2))
        
        self.ending_label = tk.Label(
            self.task_frame,
            text="Loading time",
            bg=self.bg_color,
            fg=self.ending_style['color'],
            font=(
                self.ending_style['font_family'],
                self.ending_style['font_size'],
                'bold' if self.ending_style.get('bold') else 'normal'
            ),
            anchor='w',
            justify='left'
        )
        self.ending_label.grid(row=1, column=0, sticky='ew')
        
        # Bind dragging to all widgets
        for widget in [self.main_frame, self.content_frame, self.time_frame, self.task_frame,
                      self.time_label, self.task_label, self.ending_label, self.separator]:
            widget.bind('<Button-1>', self.start_move)
            widget.bind('<B1-Motion>', self.on_move)
            widget.bind('<Button-3>', self.show_context_menu)
            
        # Bind dragging to the root window as well
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)
            
        # Create context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Refresh", command=self.update_display)
        self.context_menu.add_command(label="Reload Styles", command=self._reload_styles)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Settings", command=self.show_settings)
        self.context_menu.add_command(label="Hide", command=self.hide_window)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Close", command=self.close_window)

    def _reload_styles(self):
        try:
            self.load_settings()
            self.apply_styles()
        except Exception as ex:
            print("Error reloading styles:", ex)

    def apply_styles(self):
        """Apply current styles to widgets (runs on Tk thread)"""
        # Backgrounds
        self.root.configure(bg=self.bg_color)
        for w in [self.main_frame, self.content_frame, self.time_frame, self.task_frame]:
            w.configure(bg=self.bg_color)
        for lbl in [self.time_label, self.task_label, self.ending_label]:
            lbl.configure(bg=self.bg_color)
        # Time
        self.time_label.configure(
            fg=self.time_style['color'],
            font=(self.time_style['font_family'], self.time_style['font_size'], 'bold' if self.time_style.get('bold') else 'normal')
        )
        # Task
        self.task_label.configure(
            fg=self.task_style['color'],
            font=(self.task_style['font_family'], self.task_style['font_size'], 'bold' if self.task_style.get('bold') else 'normal')
        )
        # Ending
        self.ending_label.configure(
            fg=self.ending_style['color'],
            font=(self.ending_style['font_family'], self.ending_style['font_size'], 'bold' if self.ending_style.get('bold') else 'normal')
        )
        # Separator reflects task color
        self.separator.configure(bg=self.task_style['color'])
        self.auto_resize()
        
    def show_context_menu(self, event):
        """Show right-click context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def show_settings(self):
        """Show settings dialog (placeholder)"""
        # Since this window is Tk-based and settings dialog is PyQt-based,
        # we can't open it directly here. Instead, toggle a flag so the tray
        # can reopen the overlay with updated settings. Users can access
        # settings from the tray menu. For convenience, we show a minimal
        # info message.
        try:
            import tkinter.messagebox as mb
            mb.showinfo("Settings", "Open the tray icon menu > Settings > General to customize overlay fonts and colors.")
        except Exception:
            pass

    # ------------- Thread-safe command processing -------------
    def enqueue_command(self, name, payload=None):
        try:
            self.command_queue.put((name, payload), block=False)
        except Exception:
            pass

    def request_settings_reload(self):
        self.enqueue_command('reload', None)

    def request_hide(self):
        self.enqueue_command('hide', None)

    def request_show(self):
        self.enqueue_command('show', None)

    def request_close(self):
        self.enqueue_command('close', None)

    def poll_commands(self):
        try:
            while True:
                name, payload = self.command_queue.get_nowait()
                if name == 'reload':
                    self.load_settings()
                    self.apply_styles()
                elif name == 'hide':
                    self._hide_window()
                elif name == 'show':
                    self._show_window()
                elif name == 'close':
                    self._close()
        except queue.Empty:
            pass
        finally:
            # keep polling
            self.root.after(100, self.poll_commands)
        
    def _hide_window(self):
        """Hide the task display window"""
        self.root.withdraw()
        
    def _show_window(self):
        """Show the task display window"""
        self.root.deiconify()
        self.root.lift()
        
    def hide_window(self):
        """Thread-safe hide from any thread"""
        self.request_hide()

    def show_window(self):
        """Thread-safe show from any thread"""
        self.request_show()

    def close_window(self):
        """Thread-safe close from any thread"""
        self.request_close()

    def _close(self):
        """Helper to close the window from the tkinter thread"""
        try:
            self.root.quit()
            self.root.destroy()
        except tk.TclError:
            # Window might already be destroyed
            pass
        
    def parse_event_time(self, ev_time):
        """Parse event time from Google Calendar API response"""
        if "dateTime" in ev_time:
            dt = parser.isoparse(ev_time["dateTime"])
            return dt
        elif "date" in ev_time:
            # All-day event
            return parser.isoparse(ev_time["date"]).replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
        else:
            return None
            
    def find_now_and_next(self, events):
        """Find current and next events from event list"""
        local_now = datetime.now(tz.tzlocal())
        current = None
        nxt = None
        
        # Parse events
        parsed = []
        for ev in events:
            start = ev.get("start", {})
            end = ev.get("end", {})
            try:
                start_dt = self.parse_event_time(start)
                end_dt = self.parse_event_time(end)
                parsed.append((start_dt, end_dt, ev.get("summary", "(no title)")))
            except Exception:
                continue
                
        # Find current event
        for s, e, summary in parsed:
            if s and e and s <= local_now < e:
                current = (s, e, summary)
                break
                
        # Find next event
        future = sorted([p for p in parsed if p[0] and p[0] > local_now], key=lambda x: x[0])
        if future:
            nxt = future[0]
            
        return current, nxt
        
    def pretty_time(self, dt):
        """Format datetime to pretty string"""
        if not dt:
            return ""
        return dt.astimezone(tz.tzlocal()).strftime("%I:%M %p").lstrip("0")
        
    def calculate_time_remaining(self, end_time):
        """Calculate time remaining until end_time"""
        if not end_time:
            return "Unknown time"
            
        local_now = datetime.now(tz.tzlocal())
        remaining = end_time - local_now
        
        if remaining.total_seconds() <= 0:
            return "Ended"
            
        total_minutes = math.ceil(remaining.total_seconds() / 60)
        
        if total_minutes < 60:
            return f"Ending in {total_minutes} mins"
        else:
            hours = total_minutes // 60
            minutes = total_minutes % 60
            if minutes == 0:
                return f"Ending in {hours} hrs"
            else:
                return f"Ending in {hours}h {minutes}m"
                
    def update_display(self):
        """Update the task display with current calendar events"""
        def _update_ui():
            try:
                # Update current time
                current_time = datetime.now()
                time_str = current_time.strftime("%I:%M\n%p").lstrip("0")
                self.time_label.config(text=time_str)
                
                # Get today's events
                if self.calendar_client:
                    events = self.calendar_client.get_today_events()
                    current, nxt = self.find_now_and_next(events)
                    
                    if current:
                        s, e, title = current
                        clean_title = title.strip()
                        self.task_label.config(text=clean_title)
                        time_remaining = self.calculate_time_remaining(e)
                        self.ending_label.config(text=time_remaining)
                    else:
                        self.task_label.config(text="Free Time")
                        if nxt:
                            s2, e2, t2 = nxt
                            self.ending_label.config(text=f"Next: {t2} at {self.pretty_time(s2)}")
                        else:
                            self.ending_label.config(text="No more events today")
                else:
                    self.task_label.config(text="Calendar Unavailable")
                    self.ending_label.config(text="Check authentication")
                    
                # Auto-resize window
                self.auto_resize()
                
            except Exception as ex:
                print(f"Error updating display: {ex}")
                self.task_label.config(text="Error")
                self.ending_label.config(text="Check connection")
                self.auto_resize()
        
        # Schedule UI update in the main thread
        self.root.after(0, _update_ui)
            
    def auto_resize(self):
        """Automatically resize window to fit content"""
        self.root.update_idletasks()
        
        # Get required size
        main_frame = list(self.root.children.values())[0]
        main_frame.update_idletasks()
        
        req_width = main_frame.winfo_reqwidth() + 50  # Increased padding
        req_height = main_frame.winfo_reqheight() + 30 # Increased padding
        
        # Apply constraints
        min_width, min_height = 250, 80
        max_width = 800
        
        final_width = max(min_width, min(max_width, req_width))
        final_height = max(min_height, req_height)
        
        # Get current position
        current_geo = self.root.geometry()
        if '+' in current_geo:
            pos_part = '+' + current_geo.split('+', 1)[1]
        else:
            pos_part = ""
            
        self.root.geometry(f"{final_width}x{final_height}{pos_part}")
        
    def auto_refresh(self):
        """Auto-refresh the display periodically"""
        self.update_display()
        # Schedule next refresh in the main thread
        self.root.after(self.refresh_seconds * 1000, self.auto_refresh)
        
    def start(self):
        """Start the task display window"""
        self.update_display()
        self.auto_refresh()
        
    def run(self):
        """Run the task display window (blocking)"""
        self.start()
        self.root.mainloop()
        
    def run_in_thread(self):
        """Run the task display window in a separate thread"""
        import threading
        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
