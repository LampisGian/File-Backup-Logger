import threading
from pathlib import Path
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog
from backup_method import FolderBackupManager
from zip_manager import ZipBackupManager
from personal_setttings import ConfigManager

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

#This class is responsible for creating the custom notification windows with the appropriate colours and icons based on the type of notification 
# (success, error, info) and also is responsible for centering the notification window on the screen and handling the 
# user interactions with the notification such as closing it by clicking the close button or pressing the escape key or the enter key.
class CustomNotification(tk.Toplevel):
    def __init__(self, parent, title: str, message: str, notification_type: str = "info"):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.overrideredirect(True)

        bg_main = "#121212"
        card_bg = "#1c1c1e"
        text_main = "#f5f5f5"
        text_secondary = "#d1d5db"

        accent_map = {
            "success": ("#22c55e", "✅"),
            "error": ("#ef4444", "✖"),
            "info": ("#3b82f6", "ℹ️")
        }

        accent, icon = accent_map.get(notification_type, ("#3b82f6", "ℹ️"))

        self.configure(bg=bg_main)

        shadow = tk.Frame(self, bg="#0b0b0c")
        shadow.pack(padx=6, pady=6)

        card = tk.Frame(
            shadow,
            bg=card_bg,
            bd=0,
            highlightthickness=1,
            highlightbackground="#2f2f35"
        )
        card.pack()

        top_bar = tk.Frame(card, bg=accent, height=4)
        top_bar.pack(fill="x")

        header = tk.Frame(card, bg=card_bg)
        header.pack(fill="x", padx=18, pady=(14, 8))

        tk.Label(
            header,
            text=icon,
            font=("Helvetica", 16),
            bg=card_bg,
            fg=text_main
        ).pack(side="left")

        tk.Label(
            header,
            text=title,
            font=("Helvetica", 13, "bold"),
            bg=card_bg,
            fg=text_main
        ).pack(side="left", padx=(10, 0))

        close_label = tk.Label(
            header,
            text="✕",
            bg=card_bg,
            fg="#d4d4d8",
            font=("Helvetica", 11, "bold"),
            cursor="hand2",
            padx=8,
            pady=2
        )
        close_label.pack(side="right")
        close_label.bind("<Button-1>", lambda event: self.destroy())
        close_label.bind("<Enter>", lambda event: close_label.config(fg="white"))
        close_label.bind("<Leave>", lambda event: close_label.config(fg="#d4d4d8"))

        body = tk.Frame(card, bg=card_bg)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 14))

        tk.Label(
            body,
            text=message,
            justify="left",
            wraplength=440,
            font=("Helvetica", 10),
            bg=card_bg,
            fg=text_secondary
        ).pack(anchor="w")

        footer = tk.Frame(card, bg=card_bg)
        footer.pack(fill="x", padx=18, pady=(0, 16))

        ok_label = tk.Label(
            footer,
            text="OK",
            bg=accent,
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            padx=18,
            pady=8
        )
        ok_label.pack(anchor="e")

        ok_label.bind("<Button-1>", lambda event: self.destroy())
        ok_label.bind("<Enter>", lambda event: ok_label.config(bg=self._hover_color(accent)))
        ok_label.bind("<Leave>", lambda event: ok_label.config(bg=accent))

        self.bind("<Escape>", lambda event: self.destroy())
        self.bind("<Return>", lambda event: self.destroy())

        self.update_idletasks()
        self._center(parent)

    def _hover_color(self, color: str) -> str:
        hover_map = {
            "#22c55e": "#16a34a",
            "#ef4444": "#dc2626",
            "#3b82f6": "#2563eb"
        }
        return hover_map.get(color, color)

    def _center(self, parent):
        parent.update_idletasks()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        window_w = self.winfo_reqwidth()
        window_h = self.winfo_reqheight()

        x = parent_x + (parent_w // 2) - (window_w // 2)
        y = parent_y + (parent_h // 2) - (window_h // 2)

        self.geometry(f"{window_w}x{window_h}+{x}+{y}")

#This class is responsible for creating the settings window where the user can change the default destination folder, 
# the default backup type and the backup reminder interval and also is responsible for saving the settings in the config file 
# and updating the GUI with the new settings when the user saves them.
class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, config_manager: ConfigManager, on_save_callback):
        super().__init__(parent)
        self.title("Settings")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)
        self.configure(bg="#141414")

        self.config_manager = config_manager
        self.on_save_callback = on_save_callback

        preferences = self.config_manager.get_preferences()

        self.default_destination_var = tk.StringVar(
            value=preferences.get("default_destination_folder", "")
        )
        self.default_backup_type_var = tk.StringVar(
            value=preferences.get("default_backup_type", "folder")
        )
        self.backup_interval_var = tk.StringVar(
            value=preferences.get("backup_interval", "manual")
        )

        self._build_ui()
        self.update_idletasks()
        self._center(parent)

    def _build_ui(self):
        container = tk.Frame(self, bg="#141414", padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text="⚙️ Settings",
            bg="#141414",
            fg="#f5f5f5",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 16))

        tk.Label(
            container,
            text="Default destination folder",
            bg="#141414",
            fg="#d1d5db",
            font=("Helvetica", 10, "bold")
        ).grid(row=1, column=0, columnspan=3, sticky="w", pady=(0, 6))

        destination_entry = tk.Entry(
            container,
            textvariable=self.default_destination_var,
            bg="#f3f4f6",
            fg="#111111",
            relief="flat",
            font=("Helvetica", 10),
            width=42,
            insertbackground="#111111"
        )
        destination_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=(0, 10), pady=(0, 14))

        browse_button = tk.Label(
            container,
            text="📂 Browse",
            bg="#3a3a3a",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=8
        )
        browse_button.grid(row=2, column=2, sticky="ew", pady=(0, 14))
        browse_button.bind("<Button-1>", lambda event: self._browse_default_destination())
        browse_button.bind("<Enter>", lambda event: browse_button.config(bg="#525252"))
        browse_button.bind("<Leave>", lambda event: browse_button.config(bg="#3a3a3a"))

        tk.Label(
            container,
            text="Default backup type",
            bg="#141414",
            fg="#d1d5db",
            font=("Helvetica", 10, "bold")
        ).grid(row=3, column=0, columnspan=3, sticky="w", pady=(0, 6))

        backup_type_frame = tk.Frame(container, bg="#141414")
        backup_type_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=(0, 14))

        tk.Radiobutton(
            backup_type_frame,
            text="📁 Folder",
            variable=self.default_backup_type_var,
            value="folder",
            bg="#141414",
            fg="#e5e5e5",
            activebackground="#141414",
            activeforeground="#e5e5e5",
            selectcolor="#1f1f1f",
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Helvetica", 10),
            cursor="hand2"
        ).pack(side="left", padx=(0, 18))

        tk.Radiobutton(
            backup_type_frame,
            text="🗜️ ZIP",
            variable=self.default_backup_type_var,
            value="zip",
            bg="#141414",
            fg="#e5e5e5",
            activebackground="#141414",
            activeforeground="#e5e5e5",
            selectcolor="#1f1f1f",
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Helvetica", 10),
            cursor="hand2"
        ).pack(side="left")

        tk.Label(
            container,
            text="Backup reminder interval",
            bg="#141414",
            fg="#d1d5db",
            font=("Helvetica", 10, "bold")
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(0, 6))

        interval_frame = tk.Frame(container, bg="#141414")
        interval_frame.grid(row=6, column=0, columnspan=3, sticky="w", pady=(0, 16))

        for label, value in [
            ("Manual", "manual"),
            ("Daily", "daily"),
            ("Weekly", "weekly")
        ]:
            tk.Radiobutton(
                interval_frame,
                text=label,
                variable=self.backup_interval_var,
                value=value,
                bg="#141414",
                fg="#e5e5e5",
                activebackground="#141414",
                activeforeground="#e5e5e5",
                selectcolor="#1f1f1f",
                highlightthickness=0,
                bd=0,
                relief="flat",
                font=("Helvetica", 10),
                cursor="hand2"
            ).pack(side="left", padx=(0, 18))

        hint_label = tk.Label(
            container,
            text="Reminder only — it does not run automatic backups in the background.",
            bg="#141414",
            fg="#9ca3af",
            font=("Helvetica", 9)
        )
        hint_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(0, 16))

        button_frame = tk.Frame(container, bg="#141414")
        button_frame.grid(row=8, column=0, columnspan=3, sticky="e")

        reset_label = tk.Label(
            button_frame,
            text="Reset",
            bg="#3a3a3a",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            padx=16,
            pady=8
        )
        reset_label.pack(side="left", padx=(0, 10))
        reset_label.bind("<Button-1>", lambda event: self._reset_defaults())
        reset_label.bind("<Enter>", lambda event: reset_label.config(bg="#525252"))
        reset_label.bind("<Leave>", lambda event: reset_label.config(bg="#3a3a3a"))

        save_label = tk.Label(
            button_frame,
            text="Save",
            bg="#22c55e",
            fg="white",
            font=("Helvetica", 10, "bold"),
            cursor="hand2",
            padx=18,
            pady=8
        )
        save_label.pack(side="left")
        save_label.bind("<Button-1>", lambda event: self._save_settings())
        save_label.bind("<Enter>", lambda event: save_label.config(bg="#16a34a"))
        save_label.bind("<Leave>", lambda event: save_label.config(bg="#22c55e"))

    def _browse_default_destination(self):
        folder = filedialog.askdirectory(title="Select default destination folder")
        if folder:
            self.default_destination_var.set(folder)

    def _reset_defaults(self):
        self.default_destination_var.set("")
        self.default_backup_type_var.set("folder")
        self.backup_interval_var.set("manual")

    def _save_settings(self):
        self.config_manager.update_preferences(
            default_destination_folder=self.default_destination_var.get().strip(),
            default_backup_type=self.default_backup_type_var.get().strip(),
            backup_interval=self.backup_interval_var.get().strip()
        )
        self.on_save_callback()
        self.destroy()

    def _center(self, parent):
        parent.update_idletasks()

        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        window_w = self.winfo_reqwidth()
        window_h = self.winfo_reqheight()

        x = parent_x + (parent_w // 2) - (window_w // 2)
        y = parent_y + (parent_h // 2) - (window_h // 2)

        self.geometry(f"{window_w}x{window_h}+{x}+{y}")

#This class creates the main UI of the app with the appropriate buttons and spaces for choosing the source and destination folders and 
# the version of the backup and also is responsible for handling the user interactions with the UI such as clicking the buttons, 
# dragging and dropping folders and showing the notifications.
#Also this class is responsible for loading the settings of the user from the config file and setting the values as defaults 
#Also based on the interval it checks if the user needs a reminder to make a backup and shows the notification if needed and also is responsible for 
# refreshing the list of existing backups when the user changes the source or destination folders.
class BackupGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Backup Logger")
        self.root.geometry("980x700")
        self.root.minsize(860, 620)
        self.root.configure(bg="#141414")

        self.folder_backup_manager = FolderBackupManager()
        self.zip_backup_manager = ZipBackupManager()
        self.config_manager = ConfigManager()

        self.project_root = Path(__file__).resolve().parent.parent
        self.default_backups_path = self.project_root / "Backups"
        self.default_backups_path.mkdir(parents=True, exist_ok=True)

        self.source_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        self.version_var = tk.StringVar()
        self.backup_type_var = tk.StringVar(value="folder")
        self.status_var = tk.StringVar(value="Ready.")

        self._configure_styles()
        self._build_ui()
        self._load_config_into_gui()
        self._refresh_existing_backups()
        self.root.after(300, self._check_backup_reminder)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#141414")
        style.configure("Card.TFrame", background="#1f1f1f")

        style.configure(
            "Title.TLabel",
            background="#141414",
            foreground="#f5f5f5",
            font=("Helvetica", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#141414",
            foreground="#b0b0b0",
            font=("Helvetica", 10)
        )

        style.configure(
            "Section.TLabelframe",
            background="#1f1f1f",
            foreground="#f0f0f0",
            borderwidth=1
        )
        style.configure(
            "Section.TLabelframe.Label",
            background="#1f1f1f",
            foreground="#f8fafc",
            font=("Helvetica", 11, "bold")
        )

        style.configure(
            "Modern.TLabel",
            background="#1f1f1f",
            foreground="#e5e5e5",
            font=("Helvetica", 10)
        )

        style.configure(
            "Modern.TEntry",
            fieldbackground="#f3f4f6",
            foreground="#111111",
            padding=8
        )

        style.configure(
            "Accent.TButton",
            background="#22c55e",
            foreground="white",
            padding=(14, 10),
            font=("Helvetica", 10, "bold"),
            borderwidth=0
        )
        style.map("Accent.TButton", background=[("active", "#16a34a")])

        style.configure(
            "Secondary.TButton",
            background="#3a3a3a",
            foreground="white",
            padding=(12, 9),
            borderwidth=0
        )
        style.map("Secondary.TButton", background=[("active", "#525252")])

        style.configure(
            "Status.TLabel",
            background="#1f1f1f",
            foreground="#e5e5e5",
            font=("Helvetica", 10)
        )

    def _build_ui(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        outer.columnconfigure(0, weight=1)

        ttk.Label(
            outer,
            text="File Backup Logger",
            style="Title.TLabel"
        ).grid(row=0, column=0, sticky="w")

        ttk.Label(
            outer,
            text="Drag & drop, folder/ZIP backup, status tracking and clean backup history.",
            style="Subtitle.TLabel"
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

        content = ttk.Frame(outer, style="App.TFrame")
        content.grid(row=2, column=0, sticky="nsew")
        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(2, weight=1)

        source_frame = ttk.LabelFrame(
            content,
            text="Source Folder",
            style="Section.TLabelframe",
            padding=12
        )
        source_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        source_frame.columnconfigure(0, weight=1)

        ttk.Entry(
            source_frame,
            textvariable=self.source_var,
            style="Modern.TEntry"
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 8))

        ttk.Button(
            source_frame,
            text="📂 Browse",
            style="Secondary.TButton",
            command=self._browse_source_folder
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        self.drop_label = tk.Label(
            source_frame,
            text="📥 Drag & Drop source folder here",
            bg="#2a241f",
            fg="white",
            relief="ridge",
            bd=2,
            padx=12,
            pady=14,
            font=("Helvetica", 11, "bold")
        )
        self.drop_label.grid(row=1, column=0, columnspan=2, sticky="ew")

        if TkinterDnD is not None and DND_FILES is not None:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self._handle_drop)
        else:
            self.drop_label.configure(text="📥 Drag & Drop unavailable (install tkinterdnd2)")

        destination_frame = ttk.LabelFrame(
            content,
            text="Destination Folder",
            style="Section.TLabelframe",
            padding=12
        )
        destination_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        destination_frame.columnconfigure(0, weight=1)

        ttk.Entry(
            destination_frame,
            textvariable=self.destination_var,
            style="Modern.TEntry"
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8))

        ttk.Button(
            destination_frame,
            text="🗂️ Browse",
            style="Secondary.TButton",
            command=self._browse_destination_folder
        ).grid(row=0, column=1, sticky="ew")

        options_frame = ttk.LabelFrame(
            content,
            text="Backup Options",
            style="Section.TLabelframe",
            padding=12
        )
        options_frame.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        options_frame.columnconfigure(1, weight=1)

        ttk.Label(
            options_frame,
            text="Version",
            style="Modern.TLabel"
        ).grid(row=0, column=0, sticky="w", pady=(0, 8), padx=(0, 8))

        ttk.Entry(
            options_frame,
            textvariable=self.version_var,
            style="Modern.TEntry"
        ).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(
            options_frame,
            text="Leave empty for v1",
            style="Modern.TLabel"
        ).grid(row=1, column=1, sticky="w", pady=(0, 10))

        ttk.Label(
            options_frame,
            text="Backup Type",
            style="Modern.TLabel"
        ).grid(row=2, column=0, sticky="w", pady=(0, 6), padx=(0, 8))

        tk.Radiobutton(
            options_frame,
            text="📁 Folder backup",
            variable=self.backup_type_var,
            value="folder",
            bg="#1f1f1f",
            fg="#e5e5e5",
            activebackground="#1f1f1f",
            activeforeground="#e5e5e5",
            selectcolor="#141414",
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Helvetica", 10),
            anchor="w",
            cursor="hand2"
        ).grid(row=2, column=1, sticky="w", pady=(0, 6))

        tk.Radiobutton(
            options_frame,
            text="🗜️ ZIP backup",
            variable=self.backup_type_var,
            value="zip",
            bg="#1f1f1f",
            fg="#e5e5e5",
            activebackground="#1f1f1f",
            activeforeground="#e5e5e5",
            selectcolor="#141414",
            highlightthickness=0,
            bd=0,
            relief="flat",
            font=("Helvetica", 10),
            anchor="w",
            cursor="hand2"
        ).grid(row=3, column=1, sticky="w")

        existing_frame = ttk.LabelFrame(
            content,
            text="Existing Backups",
            style="Section.TLabelframe",
            padding=12
        )
        existing_frame.grid(row=2, column=1, sticky="nsew", padx=(8, 0))
        existing_frame.rowconfigure(0, weight=1)
        existing_frame.columnconfigure(0, weight=1)

        self.backups_listbox = tk.Listbox(
            existing_frame,
            bg="#181411",
            fg="#f3f4f6",
            selectbackground="#22c55e",
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3f3f46",
            font=("Helvetica", 10)
        )
        self.backups_listbox.grid(row=0, column=0, sticky="nsew")

        controls_frame = ttk.Frame(outer, style="App.TFrame")
        controls_frame.grid(row=3, column=0, sticky="ew", pady=(12, 8))

        self.start_button = ttk.Button(
            controls_frame,
            text="🚀 Start Backup",
            style="Accent.TButton",
            command=self._start_backup
        )
        self.start_button.grid(row=0, column=0, sticky="w")

        ttk.Button(
            controls_frame,
            text="🔄 Refresh",
            style="Secondary.TButton",
            command=self._refresh_existing_backups
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))

        ttk.Button(
            controls_frame,
            text="⚙️ Settings",
            style="Secondary.TButton",
            command=self._open_settings
        ).grid(row=0, column=2, sticky="w", padx=(10, 0))

        status_card = ttk.Frame(outer, style="Card.TFrame")
        status_card.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        status_card.columnconfigure(0, weight=1)

        ttk.Label(
            status_card,
            text="Status",
            style="Modern.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        self.status_label = ttk.Label(
            status_card,
            textvariable=self.status_var,
            style="Status.TLabel"
        )
        self.status_label.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        self.source_var.trace_add("write", lambda *args: self._refresh_existing_backups())

    def _load_config_into_gui(self):
        preferences = self.config_manager.get_preferences()
        last_used = self.config_manager.get_last_used()

        default_destination = preferences.get("default_destination_folder", "").strip()
        if default_destination:
            self.destination_var.set(default_destination)
        else:
            self.destination_var.set(str(self.default_backups_path))

        self.backup_type_var.set(
            preferences.get("default_backup_type", "folder")
        )

        last_source = last_used.get("last_source_folder", "").strip()
        if last_source:
            self.source_var.set(last_source)

        last_destination = last_used.get("last_destination_folder", "").strip()
        if last_destination:
            self.destination_var.set(last_destination)

        last_version = last_used.get("last_version", "").strip()
        if last_version:
            self.version_var.set(last_version)

    def _save_last_used_to_config(self):
        self.config_manager.update_last_used(
            last_source_folder=self.source_var.get().strip(),
            last_destination_folder=self.destination_var.get().strip(),
            last_version=self.version_var.get().strip()
        )

    def _save_successful_backup_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.config_manager.update_last_successful_backup_time(current_time)

    def _check_backup_reminder(self):
        preferences = self.config_manager.get_preferences()
        backup_state = self.config_manager.get_backup_state()

        interval = preferences.get("backup_interval", "manual").strip()
        last_backup_time = backup_state.get("last_successful_backup_time", "").strip()

        if interval == "manual":
            return

        if not last_backup_time:
            self._show_notification(
                "Backup Reminder",
                "No successful backup has been recorded yet. You may want to create one now.",
                "info"
            )
            return

        try:
            last_backup_datetime = datetime.strptime(last_backup_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return

        now = datetime.now()

        if interval == "daily":
            next_backup_due = last_backup_datetime + timedelta(days=1)
        elif interval == "weekly":
            next_backup_due = last_backup_datetime + timedelta(weeks=1)
        else:
            return

        if now >= next_backup_due:
            self._show_notification(
                "Backup Reminder",
                f"Your last successful backup was on {last_backup_time}.\nIt is time to create a new backup.",
                "info"
            )

    def _apply_settings_to_gui(self):
        preferences = self.config_manager.get_preferences()

        default_destination = preferences.get("default_destination_folder", "").strip()
        default_backup_type = preferences.get("default_backup_type", "folder").strip()

        if default_destination:
            self.destination_var.set(default_destination)
        else:
            self.destination_var.set(str(self.default_backups_path))

        self.backup_type_var.set(default_backup_type)
        self._refresh_existing_backups()
        self._show_notification(
            "Settings Saved",
            "Your settings were updated successfully.",
            "success"
        )

    def _open_settings(self):
        SettingsWindow(
            self.root,
            self.config_manager,
            self._apply_settings_to_gui
        )

    def _show_notification(self, title: str, message: str, notification_type: str):
        CustomNotification(self.root, title, message, notification_type)

    def _browse_source_folder(self):
        folder = filedialog.askdirectory(title="Select source folder")
        if folder:
            self.source_var.set(folder)
            self._save_last_used_to_config()

    def _browse_destination_folder(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:
            self.destination_var.set(folder)
            self._save_last_used_to_config()
            self._refresh_existing_backups()

    def _handle_drop(self, event):
        raw_data = event.data.strip()
        dropped_path = raw_data

        if dropped_path.startswith("{") and dropped_path.endswith("}"):
            dropped_path = dropped_path[1:-1]

        dropped_path = dropped_path.strip()
        path_obj = Path(dropped_path)

        if path_obj.exists() and path_obj.is_dir():
            self.source_var.set(str(path_obj.resolve()))
            self._save_last_used_to_config()
            self._set_status(f"Source folder set: {path_obj.name}", "info")
        else:
            self._show_notification("Invalid Drop", "Please drop a valid folder.", "error")

    def _refresh_existing_backups(self):
        self.backups_listbox.delete(0, tk.END)

        source_path = self.source_var.get().strip()
        destination_path = self.destination_var.get().strip()

        if not source_path:
            self.backups_listbox.insert(tk.END, "No source folder selected.")
            return

        try:
            existing_backups = self.folder_backup_manager.get_existing_backups(
                source_path,
                destination_path
            )

            if existing_backups:
                for entry in existing_backups:
                    self.backups_listbox.insert(tk.END, entry)
            else:
                self.backups_listbox.insert(tk.END, "No previous backups found.")

        except Exception:
            self.backups_listbox.insert(tk.END, "Backups list unavailable until valid paths are set.")

    def _set_status(self, message: str, status_type: str = "info"):
        self.status_var.set(message)

        color_map = {
            "info": "#e5e5e5",
            "success": "#86efac",
            "error": "#fca5a5",
            "running": "#fcd34d"
        }

        self.status_label.configure(foreground=color_map.get(status_type, "#e5e5e5"))

    def _set_running_state(self, is_running: bool):
        if is_running:
            self.start_button.config(state="disabled")
        else:
            self.start_button.config(state="normal")

    def _start_backup(self):
        source_path = self.source_var.get().strip()
        destination_path = self.destination_var.get().strip()
        version = self.version_var.get().strip()

        if not source_path:
            self._show_notification(
                "Missing Source",
                "Please select or drop a source folder.",
                "error"
            )
            return

        self._save_last_used_to_config()
        self._set_running_state(True)
        self._set_status("Backup in progress...", "running")

        worker = threading.Thread(
            target=self._run_backup_worker,
            args=(source_path, destination_path, version),
            daemon=True
        )
        worker.start()

    def _run_backup_worker(self, source_path: str, destination_path: str, version: str):
        try:
            if self.backup_type_var.get() == "folder":
                backup_path = self.folder_backup_manager.create_backup(
                    source_path,
                    destination_path,
                    version
                )
            else:
                backup_path = self.zip_backup_manager.create_zip_backup(
                    source_path,
                    destination_path,
                    version
                )

            self.root.after(0, self._on_backup_success, backup_path)

        except Exception as error:
            self.root.after(0, self._on_backup_error, error)

    def _on_backup_success(self, backup_path):
        self._set_running_state(False)
        self._save_last_used_to_config()
        self._save_successful_backup_time()
        self._set_status(f"Backup completed successfully: {backup_path}", "success")
        self._refresh_existing_backups()
        self._show_notification(
            "Backup Completed",
            f"Backup created successfully:\n{backup_path}",
            "success"
        )

    def _on_backup_error(self, error):
        self._set_running_state(False)
        self._set_status(f"Backup failed: {error}", "error")
        self._show_notification("Backup Failed", str(error), "error")


def create_root():
    if TkinterDnD is not None:
        return TkinterDnD.Tk()
    return tk.Tk()


def launch_gui():
    root = create_root()
    BackupGUI(root)
    root.mainloop()