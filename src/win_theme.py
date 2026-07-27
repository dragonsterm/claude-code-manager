"""Windows-only chrome tweaks via ctypes. Every call degrades silently."""
import ctypes

DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY = 19  # pre-20H1


def enable_dpi_awareness():
    """Must run before tk.Tk() or text stays blurry on scaled displays."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


def _toplevel_hwnd(tk_window) -> int:
    """Tk's winfo_id() is a child window; the frame belongs to its parent."""
    hwnd = tk_window.winfo_id()
    try:
        parent = ctypes.windll.user32.GetParent(hwnd)
        return parent or hwnd
    except Exception:
        return hwnd


def apply_dark_titlebar(tk_window) -> bool:
    try:
        hwnd = _toplevel_hwnd(tk_window)
        value = ctypes.c_int(1)
        for attr in (DWMWA_USE_IMMERSIVE_DARK_MODE,
                     DWMWA_USE_IMMERSIVE_DARK_MODE_LEGACY):
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attr, ctypes.byref(value), ctypes.sizeof(value)
            ) == 0:
                return True
    except Exception:
        pass
    return False
