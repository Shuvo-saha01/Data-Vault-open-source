import threading
import time
import subprocess
import sys


def _clear_clipboard():
    """Clears the clipboard based on OS."""
    if sys.platform == "win32":
        subprocess.run(['powershell', '-command', 'Set-Clipboard -Value ""'], 
                      capture_output=True)
    elif sys.platform == "darwin":
        subprocess.run(['pbcopy'], input=b'', capture_output=True)
    else:
        subprocess.run(['xclip', '-selection', 'clipboard'], 
                      input=b'', capture_output=True)


def copy_to_clipboard(text: str, clear_after: int = 30):
    """
    Copies text to clipboard and auto-clears after specified seconds.
    
    Args:
        text: The text to copy
        clear_after: Seconds before clipboard is cleared (default 30)
    """
    # Copy to clipboard
    if sys.platform == "win32":
        subprocess.run(['powershell', '-command', 
                       f'Set-Clipboard -Value "{text}"'], 
                      capture_output=True)
    elif sys.platform == "darwin":
        subprocess.run(['pbcopy'], input=text.encode(), capture_output=True)
    else:
        subprocess.run(['xclip', '-selection', 'clipboard'], 
                      input=text.encode(), capture_output=True)

    print(f"✓ Copied to clipboard! Auto-clearing in {clear_after} seconds...")

    # Start background thread to clear clipboard
    def delayed_clear():
        time.sleep(clear_after)
        _clear_clipboard()
        print("✓ Clipboard cleared!")

    thread = threading.Thread(target=delayed_clear, daemon=True)
    thread.start()
    