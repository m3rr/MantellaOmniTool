# utils/privacy.py
import os
import re
import getpass

# Detect the current user's name
CURRENT_USER = getpass.getuser()

# We also want to catch "C:\Users\Name" specifically just in case
USER_PROFILE = os.path.expanduser("~")

def sanitize(text):
    """
    The 'Men in Black' Flashy Thing.
    Replaces the system username with %USER% in any string.
    Case-insensitive to catch 'Admin', 'admin', 'ADMIN'.
    """
    if not isinstance(text, str):
        return text
        
    # 1. Sanitize the full user profile path first (More specific)
    # Replaces "C:\Users\DarkKinkLord" with "%UserProfile%"
    if USER_PROFILE in text:
        text = text.replace(USER_PROFILE, "%UserProfile%")
        
    # 2. Sanitize just the username (Less specific)
    # Replaces "DarkKinkLord" with "%USER%"
    if CURRENT_USER:
        pattern = re.compile(re.escape(CURRENT_USER), re.IGNORECASE)
        text = pattern.sub("%USER%", text)
        
    return text