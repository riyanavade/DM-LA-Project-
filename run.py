import asyncio
import sys
from streamlit.web import cli

# Hard monkeypatch for Python 3.14 changes to get_event_loop
_original_get_event_loop = asyncio.get_event_loop

def patched_get_event_loop():
    try:
        return _original_get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop

asyncio.get_event_loop = patched_get_event_loop

if __name__ == "__main__":
    # Run streamlit
    sys.argv = ["streamlit", "run", "app.py"]
    sys.exit(cli.main())
