import subprocess
import threading
import time
import re
import shutil
from logging import setup_logger

# -------------------------------
# Logging setup
# -------------------------------
logger = setup_logger(__name__)

# -------------------------------
# Cloudflare setup
# -------------------------------
def start_cloudflare_quick_tunnel(max_wait_sec=15):
    """
    Start a Cloudflare Quick Tunnel in a daemon thread.
    Logs the public URL if successful, otherwise logs an error and raises RuntimeError.
    """

    # Check if cloudflared is installed
    if not shutil.which("cloudflared"):
        logger.error("cloudflared is not installed. Please install it first.")
        raise RuntimeError("cloudflared is not installed. Please install it first.")

    tunnel_info = {"url": None, "error": None}

    def run_tunnel():
        try:
            process = subprocess.Popen(
                ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                line = line.strip()
                # Extract trycloudflare.com URL
                match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
                if match:
                    tunnel_info["url"] = match.group(0)
                    break

            if not tunnel_info["url"]:
                # Read stderr as fallback for errors
                tunnel_info["error"] = process.stderr.read().strip()

            # Keep process running in background
            process.wait()
        except Exception as e:
            tunnel_info["error"] = str(e)

    # Run in daemon thread
    thread = threading.Thread(target=run_tunnel, daemon=True)
    thread.start()

    # Wait a short time for URL to appear
    start_time = time.time()
    while time.time() - start_time < max_wait_sec:
        if tunnel_info["url"]:
            logger.info(f"Your app is publicly reachable at: {tunnel_info['url']}")
            return tunnel_info["url"]
        if tunnel_info["error"]:
            logger.error(f"Cloudflare Tunnel failed: {tunnel_info['error']}")
            raise RuntimeError(f"Cloudflare Tunnel failed: {tunnel_info['error']}")
        time.sleep(0.2)

    # Timeout
    logger.error("Cloudflare Tunnel did not start in time or no URL was returned.")
    raise RuntimeError("Cloudflare Tunnel did not start in time or no URL was returned.")