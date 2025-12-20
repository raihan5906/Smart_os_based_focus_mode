import tkinter as tk

APP_NAME = "Smart OS-Based Focus Manager"


def safe_destroy(win):
    try:
        win.destroy()
    except Exception:
        pass


def show_info_popup(root, title, message, x=None, y=None,
                    width=420, height=100, timeout_ms=2500):
    """
    Simple white info popup (auto closes)
    """
    top = tk.Toplevel(root)
    top.title(title)
    top.resizable(False, False)
    top.attributes("-topmost", True)

    frame = tk.Frame(top, bg="white", padx=16, pady=12)
    frame.pack(fill="both", expand=True)

    label = tk.Label(
        frame,
        text=message,
        bg="white",
        fg="black",
        font=("Segoe UI", 10),
        wraplength=width - 40,
        justify="left"
    )
    label.pack(anchor="w")

    top.protocol("WM_DELETE_WINDOW", lambda: None)

    _position_window(top, x, y, width, height)

    if timeout_ms:
        root.after(timeout_ms, lambda: safe_destroy(top))

    return top


def show_warning_countdown(root, app_or_site_name, seconds,
                           x=None, y=None, width=460, height=120):
    """
    White countdown popup (single popup, updates text every second)
    """
    top = tk.Toplevel(root)
    top.title("Warning")
    top.resizable(False, False)
    top.attributes("-topmost", True)

    frame = tk.Frame(top, bg="white", padx=16, pady=12)
    frame.pack(fill="both", expand=True)

    main_label = tk.Label(
        frame,
        text=f"{app_or_site_name}",
        bg="white",
        fg="black",
        font=("Segoe UI", 10, "bold"),
        wraplength=width - 40,
        justify="left"
    )
    main_label.pack(anchor="w")

    countdown_var = tk.StringVar()
    countdown_label = tk.Label(
        frame,
        textvariable=countdown_var,
        bg="white",
        fg="black",
        font=("Segoe UI", 10)
    )
    countdown_label.pack(anchor="w", pady=(8, 0))

    top.protocol("WM_DELETE_WINDOW", lambda: None)

    _position_window(top, x, y, width, height)

    cancelled = {"flag": False}

    def update(sec):
        if cancelled["flag"]:
            return

        if sec <= 0:
            safe_destroy(top)
            return

        countdown_var.set(
            f"being closed by {APP_NAME} in {sec} seconds"
        )
        top.after(1000, lambda: update(sec - 1))

    update(seconds)

    def cancel():
        cancelled["flag"] = True
        safe_destroy(top)

    return cancel


def _position_window(win, x, y, width, height):
    try:
        screen_w = win.winfo_screenwidth()
        screen_h = win.winfo_screenheight()

        if x is not None and y is not None:
            left = max(0, min(screen_w - width, int(x - width // 2)))
            topy = max(0, min(screen_h - height, int(y - height // 2)))
            win.geometry(f"{width}x{height}+{left}+{topy}")
        else:
            win.geometry(f"{width}x{height}")
    except Exception:
        pass
