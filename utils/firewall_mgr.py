
import subprocess
import ctypes
import sys
from utils.logger import get_logger

log = get_logger()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_rule_exists(port):
    """Checks if a firewall rule exists for the port (Loose matching)."""
    # Netsh is tricky to query by port directly without complex parsing.
    # We will check if ANY rule contains our standard naming convention or the port number.
    # This is a 'best effort' check for the UI diagnostic.
    try:
        # Check matching our naming convention first (Most reliable for our tool)
        rule_name = f"(TCP {port})"
        check_cmd = f'netsh advfirewall firewall show rule name=all | findstr "{rule_name}"'
        if subprocess.call(check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            return True
            
        return False
    except:
        return False

def open_port(port, name="Mantella Omni-Tool"):
    """Opens a TCP port in Windows Firewall using netsh."""
    rule_name = f"{name} (TCP {port})"
    try:
        # Check if rule exists (simple check)
        check_cmd = f'netsh advfirewall firewall show rule name="{rule_name}"'
        if subprocess.call(check_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
            log.info(f"[FIREWALL] Rule '{rule_name}' already exists.")
            return True

        # Add Rule
        params = f'advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port}'
        
        if not is_admin():
            log.warning(f"[FIREWALL] Requesting Admin Elevation to open Port {port}...")
            # Use ShellExecuteW to trigger UAC prompt for netsh
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", "netsh", params, None, 1)
            if ret > 32:
                log.info(f"[FIREWALL] Elevation request sent for Port {port}.")
                return True # We assume success if UAC is accepted, though we can't verify immediately
            else:
                log.error(f"[FIREWALL] Elevation failed/denied for Port {port}. Error code: {ret}")
                return False
        
        # If already admin, run directly
        cmd = f'netsh {params}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log.info(f"[FIREWALL] Successfully opened Port {port} ({name}).")
            return True
        else:
            log.error(f"[FIREWALL] Failed to open Port {port}: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        log.error(f"[FIREWALL] Error executing netsh: {e}")
        return False

def enforce_omni_ports():
    """Opens 4999, 5000, 5001, 11434."""
    open_port(4999, "Mantella Server (Default)")
    open_port(5000, "Mantella Server (Alt)")
    open_port(5001, "Omni-Tool Proxy")
    open_port(11434, "Ollama Service")
