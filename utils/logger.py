# utils/logger.py
import logging
import os
import sys
from utils.privacy import sanitize

# Setup paths
if hasattr(sys, 'frozen'):
    # In frozen EXE, we want the log next to the executable, NOT in the temp folder
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_FILE = os.path.join(BASE_DIR, "h4_omni_debug.log")

class PrivacyFormatter(logging.Formatter):
    """
    Custom Formatter that runs the sanitizer on every log record.
    """
    def format(self, record):
        # Sanitize the message itself
        record.msg = sanitize(record.msg)
        # Sanitize arguments if they exist
        if record.args:
            record.args = tuple(sanitize(arg) if isinstance(arg, str) else arg for arg in record.args)
        return super().format(record)

def get_logger(debug_mode=False):
    """
    Returns the logger instance.
    debug_mode arg is accepted for compatibility but ignored (logger always debugs to file).
    """
    logger = logging.getLogger("h4_omni")
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # 1. File Handler (ONLY IN DEBUG MODE)
        if debug_mode:
            try:
                fh = logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8')
                fh.setLevel(logging.DEBUG)
                # Use our Privacy Formatter
                fmt = PrivacyFormatter('%(asctime)s | %(levelname)s | %(module)s | %(message)s')
                fh.setFormatter(fmt)
                logger.addHandler(fh)
            except Exception as e:
                # LOUD FAILURE: If we can't write, tell the user (only if frozen)
                if hasattr(sys, 'frozen'):
                    import ctypes
                    try:
                        ctypes.windll.user32.MessageBoxW(0, f"Critical Logging Error:\nCould not create log file at:\n{LOG_FILE}\n\nError: {e}", "Log Error", 0x10)
                    except: pass

        # 2. Console Handler
        # ONLY add if sys.stdout is valid (prevent noconsole crash)
        if sys.stdout is not None:
            try:
                ch = logging.StreamHandler(sys.stdout)
                ch.setLevel(logging.DEBUG)
                ch.setFormatter(fmt)
                logger.addHandler(ch)
            except: pass

    return logger

# --- COMPATIBILITY ALIAS ---
# This fixes the "ImportError: cannot import name 'setup_logger'"
setup_logger = get_logger