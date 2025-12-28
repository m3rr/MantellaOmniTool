# utils/dll_inspector.py
import ctypes
from ctypes import wintypes
import os

def get_file_version(filepath):
    """
    Interrogates the Windows PE Header to extract the FileVersion string.
    Returns a tuple (1, 2, 3, 4) or None if failed.
    """
    if not os.path.exists(filepath):
        return None

    try:
        # 1. Get size of version info
        size = ctypes.windll.version.GetFileVersionInfoSizeW(filepath, None)
        if not size:
            return None

        # 2. Create buffer and retrieve info
        res = ctypes.create_string_buffer(size)
        ctypes.windll.version.GetFileVersionInfoW(filepath, None, size, res)

        # 3. Query the value
        r = ctypes.c_void_p()
        l = ctypes.c_uint()
        
        # Look for the root block (FixedFileInfo)
        if not ctypes.windll.version.VerQueryValueW(res, "\\", ctypes.byref(r), ctypes.byref(l)):
            return None

        # 4. Parse the VS_FIXEDFILEINFO struct
        class VS_FIXEDFILEINFO(ctypes.Structure):
            _fields_ = [
                ("dwSignature", wintypes.DWORD),
                ("dwStrucVersion", wintypes.DWORD),
                ("dwFileVersionMS", wintypes.DWORD),
                ("dwFileVersionLS", wintypes.DWORD),
                ("dwProductVersionMS", wintypes.DWORD),
                ("dwProductVersionLS", wintypes.DWORD),
                ("dwFileFlagsMask", wintypes.DWORD),
                ("dwFileFlags", wintypes.DWORD),
                ("dwFileOS", wintypes.DWORD),
                ("dwFileType", wintypes.DWORD),
                ("dwFileSubtype", wintypes.DWORD),
                ("dwFileDateMS", wintypes.DWORD),
                ("dwFileDateLS", wintypes.DWORD),
            ]

        # Cast the pointer to our struct
        ffi = ctypes.cast(r, ctypes.POINTER(VS_FIXEDFILEINFO)).contents
        
        # Extract version parts
        major = ffi.dwFileVersionMS >> 16
        minor = ffi.dwFileVersionMS & 0xFFFF
        build = ffi.dwFileVersionLS >> 16
        revision = ffi.dwFileVersionLS & 0xFFFF
        
        return (major, minor, build, revision)

    except Exception as e:
        print(f"[DLL Inspector] Error: {e}")
        return None