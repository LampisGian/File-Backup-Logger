import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog

from backup_method import FolderBackupManager
from zip_manager import ZipBackupManager

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


class CustomNotification(tk.Toplevel):
    def __init__(self, parent, title: str, message: str, notification_type: str = "info"):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        bg_color = "#1f2937"
        border_color = "#10b981" if notification_type == "success" else "#ef4444" if notification_type == "error" else "#3b82f6"
        icon = "✅" if notification_type == "success" else "❌" if notification_type == "error" else "ℹ️"

        self.configure(bg=bg_color)

        container = tk.Frame(
            self,
            bg=bg_color,
            highlightbackground=border_color,
            highlightthickness=2
        )
        container.pack(fill="both", expand=True, padx=10, pady=10)

        header = tk.Frame(container, bg=bg_color)
        header.pack(fill="x", padx=14, pady=(14, 8))

        tk.Label(
            header,
            text=f"{icon} {title}",
            font=("Helvetica", 14, "bold"),
            bg=bg_color,
            fg="white"
        ).pack(anchor="w")

        tk.Label(
            container,
            text=message,
            justify="left",
            wraplength=420,
            font=("Helvetica", 11),
            bg=bg_color,
            fg="#e5e7eb"
        ).pack(anchor="w", padx=14, pady=(0, 14))

        button_frame = tk.Frame(container, bg=bg_color)
        button_frame.pack(fill="x", padx=14, pady=(0, 14))

        tk.Button(
            button_frame,
            text="OK",
            command=self.destroy,
            bg=border_color,
            fg="white",
            activebackground=border_color,
            activeforeground="white",
            relief="flat",
            padx=18,
            pady=6,
            cursor="hand2"
        ).pack(anchor="e")

        self.update_idletasks()
        self._center(parent)

    def _center(self, parent):
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        window_w = self.winfo_reqwidth()
        window_h = self.winfo_reqheight()

        x = parent_x + (parent_w // 2) - (window_w // 2)
        y = parent_y + (parent_h // 2) - (window_h // 2)

        self.geometry(f"+{x}+{y}")


class BackupGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Backup Logger")
        self.root.geometry("980x700")
        self.root.minsize(860, 620)
        self.root.configure(bg="#0f172a")

        self.folder_backup_manager = FolderBackupManager()
        self.zip_backup_manager = ZipBackupManager()

        self.project_root = Path(__file__).resolve().parent.parent
        self.default_backups_path = self.project_root / "Backups"
        self.default_backups_path.mkdir(parents=True, exist_ok=True)

        self.source_var = tk.StringVar()
        self.destination_var = tk.StringVar(value=str(self.default_backups_path))
        self.version_var = tk.StringVar()
        self.backup_type_var = tk.StringVar(value="folder")
        self.status_var = tk.StringVar(value="Ready.")

        self._configure_styles()
        self._build_ui()
        self._refresh_existing_backups()

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#0f172a")
        style.configure("Card.TFrame", background="#111827")

        style.configure(
            "Title.TLabel",
            background="#0f172a",
            foreground="white",
            font=("Helvetica", 22, "bold")
        )

        style.configure(
            "Subtitle.TLabel",
            background="#0f172a",
            foreground="#94a3b8",
            font=("Helvetica", 10)
        )

        style.configure(
            "Section.TLabelframe",
            background="#111827",
            foreground="#e5e7eb",
            borderwidth=1
        )
        style.configure(
            "Section.TLabelframe.Label",
            background="#111827",
            foreground="#f8fafc",
            font=("Helvetica", 11, "bold")
        )

        style.configure(
            "Modern.TLabel",
            background="#111827",
            foreground="#e5e7eb",
            font=("Helvetica", 10)
        )

        style.configure(
            "Modern.TEntry",
            fieldbackground="#f8fafc",
            foreground="#111827",
            padding=8
        )

        style.configure(
            "Accent.TButton",
            background="#2563eb",
            foreground="white",
            padding=(14, 10),
            font=("Helvetica", 10, "bold"),
            borderwidth=0
        )
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])

        style.configure(
            "Secondary.TButton",
            background="#374151",
            foreground="white",
            padding=(12, 9),
            borderwidth=0
        )
        style.map("Secondary.TButton", background=[("active", "#4b5563")])

        style.configure(
            "TRadiobutton",
            background="#111827",
            foreground="#e5e7eb",
            font=("Helvetica", 10)
        )

        style.configure(
            "Status.TLabel",
            background="#111827",
            foreground="#e5e7eb",
            font=("Helvetica", 10)
        )

    def _build_ui(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=16)
        outer.pack(fill="both", expand=True)

        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

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

        # Source
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
            bg="#1e293b",
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

        # Destination
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

        # Options
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

        ttk.Radiobutton(
            options_frame,
            text="📁 Folder backup",
            variable=self.backup_type_var,
            value="folder"
        ).grid(row=2, column=1, sticky="w", pady=(0, 6))

        ttk.Radiobutton(
            options_frame,
            text="🗜️ ZIP backup",
            variable=self.backup_type_var,
            value="zip"
        ).grid(row=3, column=1, sticky="w")

        # Existing backups
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
            bg="#0b1220",
            fg="#e5e7eb",
            selectbackground="#2563eb",
            selectforeground="white",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#334155",
            font=("Helvetica", 10)
        )
        self.backups_listbox.grid(row=0, column=0, sticky="nsew")

        # Controls
        controls_frame = ttk.Frame(outer, style="App.TFrame")
        controls_frame.grid(row=3, column=0, sticky="ew", pady=(12, 8))
        controls_frame.columnconfigure(2, weight=1)

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

        self.progress = ttk.Progressbar(
            controls_frame,
            mode="indeterminate",
            length=250
        )
        self.progress.grid(row=0, column=3, sticky="e")

        # Status
        status_card = ttk.Frame(outer, style="Card.TFrame")
        status_card.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        status_card.columnconfigure(0, weight=1)

        ttk.Label(
            status_card,
            text="Status",
            style="Modern.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        ttk.Label(
            status_card,
            textvariable=self.status_var,
            style="Status.TLabel"
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

        self.source_var.trace_add("write", lambda *args: self._refresh_existing_backups())

    def _show_notification(self, title: str, message: str, notification_type: str):
        CustomNotification(self.root, title, message, notification_type)

    def _browse_source_folder(self):
        folder = filedialog.askdirectory(title="Select source folder")
        if folder:
            self.source_var.set(folder)

    def _browse_destination_folder(self):
        folder = filedialog.askdirectory(title="Select destination folder")
        if folder:
            self.destination_var.set(folder)
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
            self.status_var.set(f"Source folder set: {path_obj.name}")
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

    def _set_running_state(self, is_running: bool):
        if is_running:
            self.start_button.config(state="disabled")
            self.progress.start(10)
        else:
            self.start_button.config(state="normal")
            self.progress.stop()

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

        self._set_running_state(True)
        self.status_var.set("Backup in progress...")

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
        self.status_var.set(f"Backup completed successfully: {backup_path}")
        self._refresh_existing_backups()
        self._show_notification(
            "Backup Completed",
            f"Backup created successfully:\n{backup_path}",
            "success"
        )

    def _on_backup_error(self, error):
        self._set_running_state(False)
        self.status_var.set(f"Backup failed: {error}")
        self._show_notification("Backup Failed", str(error), "error")


def create_root():
    if TkinterDnD is not None:
        return TkinterDnD.Tk()
    return tk.Tk()


def launch_gui():
    root = create_root()
    BackupGUI(root)
    root.mainloop()