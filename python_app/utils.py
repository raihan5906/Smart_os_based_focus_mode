import ctypes
import psutil
import win32gui
import win32process
from datetime import datetime

# ================= IDLE TIME =================
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

def get_idle_seconds():
    li = LASTINPUTINFO()
    li.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(li)) == 0:
        return 0
    millis = ctypes.windll.kernel32.GetTickCount() - li.dwTime
    return millis / 1000.0

# ================= ACTIVE WINDOW =================
def get_active_window_info():
    try:
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return None

        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        try:
            proc = psutil.Process(pid)
            name = proc.name().lower()
        except Exception:
            name = ""

        title = win32gui.GetWindowText(hwnd)

        return {
            "hwnd": hwnd,
            "pid": pid,
            "name": name,
            "title": title
        }
    except Exception:
        return None

# ================= WINDOW RECT =================
def get_window_rect(hwnd):
    try:
        return win32gui.GetWindowRect(hwnd)
    except Exception:
        return None

# ================= PROCESS CONTROL =================
def terminate_process(pid):
    try:
        p = psutil.Process(pid)
        p.terminate()
        return True
    except Exception:
        return False

def set_high_priority(pid):
    try:
        psutil.Process(pid).nice(psutil.HIGH_PRIORITY_CLASS)
        return True
    except Exception:
        return False

def set_low_priority(pid):
    try:
        psutil.Process(pid).nice(psutil.IDLE_PRIORITY_CLASS)
        return True
    except Exception:
        return False

# ================= TIME CHECK =================
def is_within_time(start_str, end_str):
    """
    Returns True if current time is within start_str and end_str (HH:MM).
    Supports overnight ranges.
    """
    try:
        if not start_str or not end_str:
            return False

        now = datetime.now().time()
        start = datetime.strptime(start_str, "%H:%M").time()
        end = datetime.strptime(end_str, "%H:%M").time()

        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end
    except Exception:
        return False
