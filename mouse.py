import ctypes
import win32file
import ctypes.wintypes as wintypes
from ctypes import windll

def clamp_char(value: int) -> int:
    return max(-128, min(127, value))

def _DeviceIoControl(devhandle, ioctl, inbuf, inbufsiz, outbuf, outbufsiz):
    DeviceIoControl_Fn = windll.kernel32.DeviceIoControl
    DeviceIoControl_Fn.argtypes = [
        wintypes.HANDLE,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.DWORD),
        wintypes.LPVOID
    ]
    DeviceIoControl_Fn.restype = wintypes.BOOL
    
    dwBytesReturned = wintypes.DWORD(0)
    lpBytesReturned = ctypes.byref(dwBytesReturned)
    status = DeviceIoControl_Fn(
        int(devhandle),
        ioctl,
        inbuf,
        inbufsiz,
        outbuf,
        outbufsiz,
        lpBytesReturned,
        None
    )
    return status, dwBytesReturned


class MOUSE_IO(ctypes.Structure):
    _fields_ = [
        ("button", ctypes.c_char),
        ("x", ctypes.c_char),
        ("y", ctypes.c_char),
        ("wheel", ctypes.c_char),
        ("unk1", ctypes.c_char)
    ]


handle = 0
found = False

def device_initialize(device_name: str) -> bool:
    global handle
    try:
        handle = win32file.CreateFileW(
            device_name,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_ALWAYS,
            win32file.FILE_ATTRIBUTE_NORMAL,
            0
        )
    except Exception as e:
        #print("Error initializing device:", e)
        return False
    return bool(handle)

def mouse_open() -> bool:
    global found
    global handle

    if found and handle:
        return True

    for i in range(1, 10):
        devpath = f'\\??\\ROOT#SYSTEM#000{i}#' + '{1abc05c0-c378-41b9-9cef-df1aba82b015}'
        if device_initialize(devpath):
            found = True
            return True
        if i == 10:
            print('Failed to initialize device.')

    return False

def call_mouse(buffer: MOUSE_IO) -> bool:
    global handle
    status, _ = _DeviceIoControl(
        handle, 
        0x2a2010,
        ctypes.c_void_p(ctypes.addressof(buffer)),
        ctypes.sizeof(buffer),
        None,
        0, 
    )
    if not status:
        print("DeviceIoControl failed to send mouse input.")
    return status


def mouse_close() -> None:
    global handle
    if handle:
        win32file.CloseHandle(int(handle))
        handle = 0

def mouse_move(button: int, x: int, y: int, wheel: int) -> None:
    """
    Sends a single relative mouse input to the GHUB device.
    """
    global handle

    x_clamped = clamp_char(x)
    y_clamped = clamp_char(y)
    btn_byte   = clamp_char(button)
    wheel_byte = clamp_char(wheel)

    io = MOUSE_IO()
    # c_char expects a bytes object of length 1 or an int in the range -128..127:
    io.button = ctypes.c_char(btn_byte.to_bytes(1, 'little', signed=True))
    io.x      = ctypes.c_char(x_clamped.to_bytes(1, 'little', signed=True))
    io.y      = ctypes.c_char(y_clamped.to_bytes(1, 'little', signed=True))
    io.wheel  = ctypes.c_char(wheel_byte.to_bytes(1, 'little', signed=True))
    io.unk1   = ctypes.c_char(b'\x00')

    if not call_mouse(io):
        mouse_close()
        if not mouse_open():
            print("Failed to reinitialize device after error.")


if not mouse_open():
    print("Ghub is not open or something else is wrong")
