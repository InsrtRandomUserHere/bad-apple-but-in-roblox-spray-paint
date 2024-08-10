import ctypes
from ctypes.wintypes import DWORD, WORD
from math import floor

emptyLong = ctypes.c_ulong()


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", DWORD),
                ("dwFlags", DWORD),
                ("time", DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class KeybdInput(ctypes.Structure):
    _fields_ = [("wVk", WORD),
                ("wScan", WORD),
                ("dwFlags", DWORD),
                ("time", DWORD),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", DWORD),
                ("wParamL", WORD),
                ("wParamH", WORD)]


class InputList(ctypes.Union):
    _fields_ = [
        ("mi", MouseInput),
        ("ki", KeybdInput),
        ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("inputList", InputList)]


MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000


def move(x, y, relative=False):  # MOVE MOUSE TO (X, Y)
    mouseFlag = MOUSEEVENTF_MOVE

    if not relative:
        mouseFlag |= MOUSEEVENTF_ABSOLUTE
        x = floor(x / 1920 * 65535)  # ASSUMING COORDINATES ARE BASED ON 1920 x 1080 RESOLUTION
        y = floor(y / 1080 * 65535)

    inputList = InputList()
    inputList.mi = MouseInput(x, y, 0, mouseFlag, 0, ctypes.pointer(emptyLong))

    windowsInput = Input(emptyLong, inputList)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(windowsInput), ctypes.sizeof(windowsInput))
