import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

from src.app_state import AppState
from src.launcher import launch_claude
from src.win_theme import apply_dark_titlebar

COLOR_BG = "#1E1E1E"
COLOR_PANEL = "#252526"
COLOR_PANEL_HOVER = "#2D2D30"
COLOR_BORDER = "#3C3C3C"
COLOR_TEXT = "#CCCCCC"
COLOR_TEXT_DIM = "#858585"
COLOR_TEXT_BRIGHT = "#FFFFFF"
COLOR_ORANGE = "#D97757"
COLOR_ORANGE_HOVER = "#E08868"
COLOR_DISABLED = "#3C3C3C"
COLOR_DISABLED_TEXT = "#888888"
COLOR_PS_BLUE = "#0078D4"
COLOR_PS_BLUE_HOVER = "#1A88E0"
COLOR_CMD_GREY = "#4E4E4E"
COLOR_CMD_GREY_HOVER = "#5E5E5E"

WIN_W, WIN_H = 560, 330

# Windows rejects these as filenames regardless of extension.
RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"}
RESERVED_NAMES |= {f"COM{i}" for i in range(1, 10)}
RESERVED_NAMES |= {f"LPT{i}" for i in range(1, 10)}
INVALID_CHARS = '\\/:*?"<>|'


def validate_folder_name(name: str):
    """Return None if usable as a single folder name, else an error string."""
    if not name or not name.strip():
        return "Folder name cannot be empty."
    if name != name.strip():
        return "Folder name cannot start or end with spaces."
    if name in (".", ".."):
        return "Folder name cannot be '.' or '..'."
    if any(c in name for c in INVALID_CHARS):
        return "Folder name contains invalid characters: \\ / : * ? \" < > |"
    if any(ord(c) < 32 for c in name):
        return "Folder name contains control characters."
    if name.endswith("."):
        return "Folder name cannot end with a period."
    if name.split(".")[0].upper() in RESERVED_NAMES:
        return f"'{name}' is a reserved Windows device name."
    return None


def _hover(widget, normal, hovered):
    """Background swap on mouse over. Disabled widgets keep their colour."""
    def enter(_event):
        if str(widget.cget("state")) != "disabled":
            widget.config(bg=hovered)

    def leave(_event):
        if str(widget.cget("state")) != "disabled":
            widget.config(bg=normal)

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


class ClaudeCodeManagerUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Claude Code Manager")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        self.root.minsize(WIN_W, WIN_H)
        self._center()
        self._set_icon()

        self.state = AppState()
        self._build_ui()
        self.update_ui_state()

        self.root.update_idletasks()
        apply_dark_titlebar(self.root)

        self.root.bind("<Control-t>", lambda _e: self.toggle_terminal())
        self.root.bind("<Return>", lambda _e: self.on_launch())
        self.root.bind("<Escape>", lambda _e: self.root.destroy())

    def _center(self):
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - WIN_W) // 2)
        y = max(0, (sh - WIN_H) // 3)
        self.root.geometry(f"{WIN_W}x{WIN_H}+{x}+{y}")

    def _set_icon(self):
        icon = Path(__file__).resolve().parent.parent / "assets" / "icon.ico"
        if icon.exists():
            try:
                self.root.iconbitmap(str(icon))
            except tk.TclError:
                pass

    def _build_ui(self):
        # --- header card: eyebrow + path -------------------------------
        card = tk.Frame(self.root, bg=COLOR_PANEL, padx=18, pady=16,
                        highlightbackground=COLOR_BORDER, highlightthickness=1)
        card.pack(fill="x", padx=20, pady=(22, 16))

        tk.Label(card, text="A C T I V E   P R O J E C T", bg=COLOR_PANEL,
                 fg=COLOR_TEXT_DIM, font=("Segoe UI", 8, "bold")).pack(anchor="w")

        self.lbl_dir = tk.Label(card, text="No project selected", bg=COLOR_PANEL,
                                fg=COLOR_ORANGE, font=("Consolas", 10),
                                wraplength=470, justify="left")
        self.lbl_dir.pack(anchor="w", pady=(8, 0))

        # --- action row ------------------------------------------------
        row = tk.Frame(self.root, bg=COLOR_BG)
        row.pack(fill="x", padx=20)

        self.btn_new = tk.Button(
            row, text="+   New Project", bg=COLOR_PANEL, fg=COLOR_TEXT_BRIGHT,
            activebackground=COLOR_ORANGE, activeforeground=COLOR_TEXT_BRIGHT,
            relief="flat", bd=0, padx=15, pady=9, font=("Segoe UI", 9, "bold"),
            cursor="hand2", command=self.on_new_project,
        )
        self.btn_new.pack(side="left", expand=True, fill="x", padx=(0, 6))
        _hover(self.btn_new, COLOR_PANEL, COLOR_PANEL_HOVER)

        self.btn_change = tk.Button(
            row, text="\U0001F4C1   Change Directory", bg=COLOR_PANEL,
            fg=COLOR_TEXT_BRIGHT, activebackground=COLOR_ORANGE,
            activeforeground=COLOR_TEXT_BRIGHT, relief="flat", bd=0, padx=15, pady=9,
            font=("Segoe UI", 9, "bold"), cursor="hand2", command=self.on_change_dir,
        )
        self.btn_change.pack(side="left", expand=True, fill="x", padx=(6, 0))
        _hover(self.btn_change, COLOR_PANEL, COLOR_PANEL_HOVER)

        # --- divider ---------------------------------------------------
        self.divider = tk.Frame(self.root, bg=COLOR_BORDER, height=1)
        self.divider.pack(fill="x", padx=20, pady=20)

        # --- launch row ------------------------------------------------
        launch_row = tk.Frame(self.root, bg=COLOR_BG)
        launch_row.pack(fill="x", padx=20)

        self.btn_launch = tk.Button(
            launch_row, text="Launch Claude Code", bg=COLOR_DISABLED,
            fg=COLOR_DISABLED_TEXT, state="disabled", relief="flat", bd=0, pady=13,
            activebackground=COLOR_ORANGE_HOVER, activeforeground=COLOR_TEXT_BRIGHT,
            font=("Segoe UI", 10, "bold"), command=self.on_launch,
        )
        self.btn_launch.pack(side="left", expand=True, fill="x", padx=(0, 10))
        _hover(self.btn_launch, COLOR_ORANGE, COLOR_ORANGE_HOVER)

        self.btn_switch = tk.Button(
            launch_row, text="PS", bg=COLOR_PS_BLUE, fg=COLOR_TEXT_BRIGHT,
            relief="flat", bd=0, width=6, pady=11, font=("Segoe UI", 9, "bold"),
            activeforeground=COLOR_TEXT_BRIGHT, cursor="hand2",
            command=self.toggle_terminal,
        )
        self.btn_switch.pack(side="right")

        tk.Label(self.root, text="Ctrl+T  switch shell     Enter  launch",
                 bg=COLOR_BG, fg=COLOR_TEXT_DIM,
                 font=("Segoe UI", 8)).pack(anchor="e", padx=20, pady=(14, 0))

    def toggle_terminal(self):
        self.state.set_terminal("cmd" if self.state.terminal == "powershell" else "powershell")
        self.update_ui_state()

    def _browse_start_dir(self) -> str:
        """Current project if it still exists, else the user's home folder."""
        cur = self.state.current_dir
        if cur and Path(cur).is_dir():
            return cur
        return str(Path.home())

    def on_change_dir(self):
        chosen = filedialog.askdirectory(title="Select Project Directory",
                                         initialdir=self._browse_start_dir())
        if chosen:
            self.state.set_directory(chosen)
            self.update_ui_state()

    def on_new_project(self):
        parent_dir = filedialog.askdirectory(title="Select Parent Location for New Project",
                                             initialdir=self._browse_start_dir())
        if not parent_dir:
            return
        raw = simpledialog.askstring("New Project", "Enter project folder name:")
        if raw is None:
            return
        error = validate_folder_name(raw)
        if error:
            messagebox.showerror("Invalid Name", error)
            return
        new_path = Path(parent_dir) / raw
        try:
            new_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            messagebox.showerror("Create Failed", str(exc))
            return
        self.state.set_directory(str(new_path))
        self.update_ui_state()

    def on_launch(self):
        if not self.state.is_launch_ready():
            return
        try:
            launch_claude(self.state.terminal, self.state.current_dir)
        except OSError as exc:
            messagebox.showerror("Launch Failed", str(exc))

    def update_ui_state(self):
        if self.state.current_dir:
            self.lbl_dir.config(text=self.state.current_dir, fg=COLOR_TEXT_BRIGHT)
        else:
            self.lbl_dir.config(text="No project selected", fg=COLOR_ORANGE)

        if self.state.terminal == "powershell":
            self.btn_switch.config(text="PS", bg=COLOR_PS_BLUE,
                                   activebackground=COLOR_PS_BLUE_HOVER)
            _hover(self.btn_switch, COLOR_PS_BLUE, COLOR_PS_BLUE_HOVER)
            launch_text = "⚡  Launch Claude Code (with PowerShell)"
        else:
            self.btn_switch.config(text="CMD", bg=COLOR_CMD_GREY,
                                   activebackground=COLOR_CMD_GREY_HOVER)
            _hover(self.btn_switch, COLOR_CMD_GREY, COLOR_CMD_GREY_HOVER)
            launch_text = "⚡  Launch Claude Code (with CMD)"

        if self.state.is_launch_ready():
            self.btn_launch.config(state="normal", bg=COLOR_ORANGE,
                                   fg=COLOR_TEXT_BRIGHT, text=launch_text,
                                   cursor="hand2")
        else:
            self.btn_launch.config(state="disabled", bg=COLOR_DISABLED,
                                   fg=COLOR_DISABLED_TEXT, text=launch_text,
                                   cursor="arrow")
