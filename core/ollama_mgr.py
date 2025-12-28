# core/ollama_mgr.py
import requests
import json
import os
import subprocess
import time
from utils.logger import get_logger
from core import TARGETS

log = get_logger()

class OllamaManager:
    BASE_URL = "http://localhost:11434"
    _process = None

    @staticmethod
    def ensure_running():
        """Checks if reachable. If not, attempts to LAUNCH it."""
        
        # 1. First Check (Fast)
        for attempt in range(1, 3):
            try:
                if requests.get(OllamaManager.BASE_URL, timeout=1).status_code == 200: return True
            except: time.sleep(0.5)
            
        # 2. Attempt Auto-Launch
        log.warning("[OLLAMA] Service offline. Attempting auto-launch...")
        ollama_exe = TARGETS.get("Ollama", {}).get("found")
        
        # Fallback to defaults if scanner missed it
        if not ollama_exe:
             defaults = [
                 os.path.join(os.environ["LOCALAPPDATA"], "Programs", "Ollama", "ollama.exe"),
                 r"C:\Ollama\ollama.exe"
             ]
             for d in defaults:
                 if os.path.exists(d): ollama_exe = d; break

        # FIX: Expand Environment Variables (e.g. %UserProfile%)
        if ollama_exe:
            ollama_exe = os.path.expandvars(ollama_exe)

        if ollama_exe and os.path.exists(ollama_exe):
            try:
                # Launch in background, hidden
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                # FIX: Store the process handle so we can kill it later
                OllamaManager._process = subprocess.Popen([ollama_exe, "serve"], startupinfo=startupinfo)
                
                log.info(f"[OLLAMA] Launch command sent to {ollama_exe} (PID: {OllamaManager._process.pid})")
                
                # 3. Wait for Boot (up to 8 seconds)
                for _ in range(8):
                    time.sleep(1)
                    try:
                        if requests.get(OllamaManager.BASE_URL, timeout=1).status_code == 200: 
                            log.info("[OLLAMA] Service is now ONLINE.")
                            return True
                    except: pass
            except Exception as e:
                log.error(f"[OLLAMA] Launch failed: {e}")
        
        return False

    @staticmethod
    def shutdown():
        """
        Force kills the managed Ollama process if it exists.
        """
        if OllamaManager._process:
            try:
                log.info(f"[OLLAMA] Terminating child process (PID: {OllamaManager._process.pid})...")
                OllamaManager._process.terminate()
                OllamaManager._process = None
            except Exception as e:
                log.warning(f"[OLLAMA] Termination failed: {e}")

    @staticmethod
    def scan_local_manifests():
        """
        Queries the Ollama API for installed models.
        Returns a list of model names (e.g. ['llama3:latest', 'dolphin-mistral:7b']).
        """
        try:
            url = f"{OllamaManager.BASE_URL}/api/tags"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                # Extract 'name' from the models list
                return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            log.warning(f"Ollama API Scan failed: {e}")
        
        return []

    @staticmethod
    def pull_model(model_name, progress_callback=None):
        """
        Pulls a model from the library.
        progress_callback(status, percent)
        """
        url = f"{OllamaManager.BASE_URL}/api/pull"
        payload = {"name": model_name, "stream": True}
        
        try:
            with requests.post(url, json=payload, stream=True) as resp:
                if resp.status_code != 200:
                    log.error(f"Pull Failed: {resp.text}")
                    return False
                
                for line in resp.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            status = data.get("status", "working")
                            
                            # Calculate Percentage
                            total = data.get("total", 0)
                            completed = data.get("completed", 0)
                            pct = 0
                            if total > 0:
                                pct = int((completed / total) * 100)
                            
                            if progress_callback:
                                progress_callback(status, pct)
                                
                            if status == "success":
                                return True
                        except: pass
            return True
        except Exception as e:
            log.error(f"Pull Exception: {e}")
            return False

    @staticmethod
    def quick_generate(prompt, model_name="dolphin-llama3:8b"):
        """
        Synchronous generation for the Bridge.
        Returns the text response or None on failure.
        """
        url = f"{OllamaManager.BASE_URL}/api/generate"
        
        # Fail fast if no prompt
        if not prompt: return None

        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_ctx": 4096 # Default context window
            }
        }
        
        try:
            log.info(f"Sending to Brain [{model_name}]: {prompt[:30]}...")
            resp = requests.post(url, json=payload, timeout=45)
            
            if resp.status_code == 200:
                data = resp.json()
                result = data.get("response", "").strip()
                log.info(f"Brain Replied: {result[:30]}...")
                return result
            else:
                log.error(f"Ollama Error {resp.status_code}: {resp.text}")
                return f"Error: I am unable to think clearly. (Status {resp.status_code})"
                
        except Exception as e:
            log.error(f"Ollama Connection Failed: {e}")
            return "Error: My connection to the neural network is severed."