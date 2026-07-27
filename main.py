import tkinter as tk

from src.ui import ClaudeCodeManagerUI
from src.win_theme import enable_dpi_awareness


def main():
    enable_dpi_awareness()  # must precede Tk() or text renders blurry when scaled
    root = tk.Tk()
    ClaudeCodeManagerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
