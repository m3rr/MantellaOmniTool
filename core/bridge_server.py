# core/bridge_server.py
import http.server
import socketserver
import threading
import json
import requests
import sys
from core import PROXY_PORT, OLLAMA_PORT
from utils.logger import get_logger

log = get_logger()
log_callback = None

def set_log_callback(func):
    global log_callback
    log_callback = func

def _log(msg):
    log.info(msg)
    if log_callback:
        log_callback(f"[PROXY] {msg}")

class OllamaProxyHandler(http.server.BaseHTTPRequestHandler):
    """
    Acts as an Ollama MITM Proxy.
    Receives Ollama-format JSON from Mantella.exe (Port 5001).
    Forwards to Real Ollama (Port 11434).
    Intercepts prompts for 'Genesis' injection.
    """
    
    def log_message(self, format, *args):
        return # Silence default logs

    def do_POST(self):
        # 1. Handle Routes (Support both generate and chat)
        # 1. Handle Routes (Support both generate and chat)
        accepted_routes = ["/api/generate", "/api/chat", "/v1/chat/completions", "/chat/completions"]
        
        # Simple suffix check or exact match
        is_valid = any(self.path.endswith(route) for route in accepted_routes)
        
        if not is_valid:
            self.send_error(404, f"Endpoint not found (Ollama Proxy): {self.path}")
            return

        try:
            # 2. Read Payload
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            _log(f"Intercepted Request ({content_length} bytes)")
            
            try:
                data = json.loads(post_data)
                # STREAMING IS BACK ON (Pass-Through approach)
                # data["stream"] = False 
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
                return

            # 3. INTERCEPTION LOGIC
            # 3. INTERCEPTION LOGIC
            # Inspect prompt/system prompt here
            prompt = data.get("prompt", "")
            if not prompt and "messages" in data:
                 # Chat format: OpenAI/Ollama-Compat
                 msgs = data.get("messages", [])
                 for m in reversed(msgs):
                     if m.get("role") == "user":
                         prompt = m.get("content", "")
                         break
            
            lower_prompt = prompt.lower()
            
            # DEBUG: Log the detected prompt to ensure we aren't blind
            _log(f"[PUPPETEER] Analyzing Request. Prompt snippet: '{lower_prompt[:50]}...'")
            
            user_intent_keywords = ["inventory", "trade", "buy", "sell", "wares", "goods", "shop", "purchase"]
            has_user_intent = any(k in lower_prompt for k in user_intent_keywords)
            
            if has_user_intent:
                _log("[PUPPETEER] Intent Detected: TRADE/INVENTORY. Arming injectors.")
            else:
                 # WARNING: Broadening trigger window. If AI says "My inventory", we should probably trust it even if user didn't ask explicitly.
                 # But for now, let's just Log failure.
                 _log(f"[PUPPETEER] No Intent Detected. Keywords checked against: {lower_prompt}")

            _log(f"Processing Prompt: {prompt[:50]}...")
            
            # FUTURE: Inject Memories here
            # data["system"] = "You are Genesis..."
            
            # 4. INJECT SYSTEM INSTRUCTION (Puppeteer V4: Subliminal Messaging)
            # Instead of fighting the stream, we tell the AI what to do.
            system_instruction = (
                "\n[SYSTEM]: IF the user wants to trade, buy, sell, or browse goods, "
                "you MUST include the tag '[inventory]' in your response."
                "\nRULES:"
                "\n1. Output the tag EXACTLY as: [inventory]"
                "\n2. NO spaces: [inventory] is CORRECT."
                "\n3. lowercase: [inventory] is CORRECT."
                "\n4. Place it on a new line."
            )

            if "messages" in data:
                # OpenAI Format: Append to system message or insert new one
                messages = data["messages"]
                found_system = False
                for msg in messages:
                    if msg.get("role") == "system":
                        msg["content"] += system_instruction
                        found_system = True
                        break
                if not found_system:
                    messages.insert(0, {"role": "system", "content": system_instruction})
                _log("[PUPPETEER] Injected System Instruction (OpenAI Mode).")

            elif "prompt" in data:
                # Ollama Format: Prepend to prompt
                data["prompt"] = system_instruction + "\n\n" + data["prompt"]
                if "system" in data:
                    data["system"] += system_instruction
                _log("[PUPPETEER] Injected System Instruction (Ollama Mode).")

            # 5. Forward to Real Ollama
            target_path = self.path
            if "chat/completions" in self.path:
                 target_path = "/v1/chat/completions"
            
            target_url = f"http://localhost:{OLLAMA_PORT}{target_path}"
            
            # PUPPETEER V5: HYBRID APPROACH (System Instruction + Stream Injection Fallback)
            # We use System Prompt to guide the AI, AND we sniff the stream to catch failures.
            
            resp = requests.post(target_url, json=data, stream=True)
            
            self.send_response(resp.status_code)
            for k, v in resp.headers.items():
                if k.lower() not in ['content-encoding', 'transfer-encoding', 'content-length']:
                     self.send_header(k, v)
            
            self.send_header('Transfer-Encoding', 'chunked')
            self.end_headers()
            
            buffer_text = ""
            injection_done = False
            triggers = [
                 # Strong Action Triggers
                 "take a look", "look around", "what i have", "my wares", "for sale", 
                 "interested in", "got these", "browse", "show you", "check my", 
                 " brought out", "bring them out", "sell you",
                 # Phrasal Triggers
                 "my inventory", "your inventory", "the inventory", "access inventory", "open inventory",
                 "at your disposal", "in stock", "have available"
            ]

            try:
                for chunk in resp.iter_content(chunk_size=1024):
                    if chunk:
                        # 1. Forward Original Chunk
                        self.wfile.write(f"{len(chunk):X}\r\n".encode('utf-8'))
                        self.wfile.write(chunk)
                        self.wfile.write(b"\r\n")
                        
                        # 2. Analyze Chunk
                        # We just accumulate text to double-check if AI already sent the tag
                        try:
                            chunk_str = chunk.decode('utf-8', errors='ignore')
                            norm_chunk = chunk_str.lower().replace('\n', ' ').replace('\r', '')
                            buffer_text += norm_chunk
                            if len(buffer_text) > 4096: buffer_text = buffer_text[-4096:]
                        except: pass

                # 3. END OF STREAM INJECTION (The "P.S." Strategy)
                # We inject the tag ONLY here, at the very end, to ensure it's not buried.
                
                # Check triggers one last time or use initial intent
                should_inject = False
                if any(t in buffer_text for t in triggers) or has_user_intent:
                    should_inject = True
                
                # Check if AI already did it (unlikely given your logs, but safe to check)
                if "[inventory]" in buffer_text.replace(" ", ""):
                    should_inject = False
                    injection_done = True 

                if should_inject:
                    _log(f"[PUPPETEER] Intent confirmed! Force Injecting Double Tap.")
                    
                    # INJECTION PAYLOAD
                    # We inject "[inventory] [Inventory]" to hit both potential keys.
                    tags = "\n\n[inventory] [Inventory]\n\n"
                    
                    injection_payload = ""
                    if '"choices":' in buffer_text: # OpenAI
                        injection_json = json.dumps({"choices": [{"delta": {"content": tags}}]})
                        injection_payload = f"data: {injection_json}\n\n"
                    else: # Ollama
                        injection_json = json.dumps({"response": tags, "done": False})
                        injection_payload = f"data: {injection_json}\n\n"
                    
                    inj_bytes = injection_payload.encode('utf-8')
                    self.wfile.write(f"{len(inj_bytes):X}\r\n".encode('utf-8'))
                    self.wfile.write(inj_bytes)
                    self.wfile.write(b"\r\n")
                    injection_done = True 
                    
                    # --- OMNI-TOOL MECHANICAL BYPASS ---
                    # The user has installed the "Resurrected Patch" which listens for this file.
                    # We write the signal directly to the game folder (via current working dir or relative).
                    # We assume the tool is running near the game, or write to known paths.
                    # Since PapyrusUtil "MiscUtil.ReadFromFile" reads from the Data folder usually...
                    # We will write to BOTH local and a best-guess Data path if possible.
                    # But actually, PapyrusUtil defaults to: Base Skyrim Directory (where SkyrimSE.exe is).
                    
                    try:
                        # 1. Write to local (if tool is in Skyrim root)
                        with open("_mantella_omni_action.txt", "w") as f:
                            f.write("inventory")
                        _log("[PUPPETEER] Wrote mechanical signal: _mantella_omni_action.txt")
                        
                        # 2. Try to write to the mapped Skyrim Directory from config
                        # We need to find the game path. It's tricky from inside the handler.
                        # But we can try the "d:\Games\..." or "C:\Games\..." common paths if we knew them.
                        # For now, we rely on the tool being run correctly or the file being in the root.
                    except Exception as e:
                        _log(f"[PUPPETEER] Failed to write mechanical signal: {e}")

                self.wfile.write(b"0\r\n\r\n")
                _log("Proxy: Response Complete.")
            except Exception as e:
                _log(f"Proxy Error: {e}")

        except Exception as e:
            _log(f"Proxy Error: {e}")
            # self.send_error(500, f"Internal Error: {e}") # Can't send if headers sent

class MantellaServer(socketserver.TCPServer):
    allow_reuse_address = True

def start_bridge_thread(port=None):
    """Starts the Ollama Proxy on specified Port (default 5001)."""
    target_port = int(port) if port else int(PROXY_PORT)
    try:
        server = MantellaServer(("localhost", target_port), OllamaProxyHandler)
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        _log(f"Ollama MITM Proxy Online on Port {target_port}")
        return server
    except OSError as e:
        if "Address already in use" in str(e):
             _log(f"CRITICAL: Port {PROXY_PORT} locked.")
        else:
             _log(f"Start Error: {e}")
        return None
    except Exception as e:
        _log(f"Unexpected Error: {e}")
        return None