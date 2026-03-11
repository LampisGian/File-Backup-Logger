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
            "info": ("#3b82f6", "ℹ")
        }

        accent, icon = accent_map.get(notification_type, ("#3b82f6", "ℹ"))

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
            wraplength=420,
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

class BackupGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("File Backup Logger")
        self.root.geometry("980x700")
        self.root.minsize(860, 620)
        self.root.configure(bg="#141414")

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

        folder_radio = tk.Radiobutton(
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
        )
        folder_radio.grid(row=2, column=1, sticky="w", pady=(0, 6))

        zip_radio = tk.Radiobutton(
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
        )
        zip_radio.grid(row=3, column=1, sticky="w")

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