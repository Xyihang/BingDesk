import ctypes
from ctypes import wintypes

# Windows API constants
DRIVE_REMOVABLE = 2

# Load kernel32
create_file = ctypes.windll.kernel32.CreateFileW
get_drive_type = ctypes.windll.kernel32.GetDriveTypeW

# Test each drive letter
for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
    drive_path = f"{letter}:\\"
    drive_type = get_drive_type(drive_path)
    if drive_type == DRIVE_REMOVABLE:
        print(f"Removable drive found: {letter}:")
    elif drive_type != 0:  # 0 = DRIVE_UNKNOWN
        print(f"Drive {letter}: type={drive_type}")
