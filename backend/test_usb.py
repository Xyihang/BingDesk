import asyncio
import sys

async def test_usb():
    ps_script = (
        "$usbDisks = Get-Disk | Where-Object { $_.BusType -eq 'USB' } | Select-Object -ExpandProperty Number; "
        "foreach ($diskNum in $usbDisks) { "
        "  Get-Partition -DiskNumber $diskNum -ErrorAction SilentlyContinue | "
        "  Where-Object { $_.DriveLetter } | Select-Object -ExpandProperty DriveLetter "
        "}"
    )
    print(f"PowerShell script: {ps_script}")
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")

    try:
        proc = await asyncio.create_subprocess_exec(
            "powershell", "-NoProfile", "-Command", ps_script,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15.0)
        print(f"Return code: {proc.returncode}")
        print(f"STDOUT: [{stdout.decode().strip()}]")
        print(f"STDERR: [{stderr.decode().strip()}]")
    except asyncio.TimeoutError:
        print("TIMEOUT after 15 seconds")
    except Exception as e:
        print(f"EXCEPTION: {type(e).__name__}: {e}")

asyncio.run(test_usb())
