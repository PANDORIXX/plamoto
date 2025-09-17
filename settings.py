import json

# -------------------------------
# Helpers
# -------------------------------
def load_settings(file):
    """Load settings from a JSON file."""
    try:
        # Open the file in read mode and parse JSON contents
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file is not found, return default settings dictionary
        return {
            'background_capture_interval': '60',
            'camera_source': 'picam',
            'droidcam_ip': '0.0.0.0',
            'droidcam_port': '0000',
            'picam_awb_mode': 1
        }

def save_settings(file, settings):
    """Save settings dictionary to a JSON file."""
    # Open the file in write mode and write the JSON with indentation for readability
    with open(file, 'w') as f:
        json.dump(settings, f, indent=2)

def get_interval_minutes_from_settings(settings: dict) -> int:
    """Parse interval minutes from settings; fallback to 60 if missing/invalid."""
    val = settings.get('background_capture_interval', 60)
    try:
        return max(1, int(val))
    except (ValueError, TypeError):
        return 60
    
def parse_form_settings(form_data: dict, current_settings: dict) -> dict:
    """Parse and validate form data, return a clean settings dict."""
    def parse_int(val, default):
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    return {
        'background_capture_interval': max(1, parse_int(form_data.get('background_capture_interval'), current_settings.get('background_capture_interval', 60))),
        'camera_source': form_data.get('camera_source', current_settings.get('camera_source', 'picam')),
        'droidcam_ip': form_data.get('droidcam_ip', current_settings.get('droidcam_ip', '')),
        'droidcam_port': parse_int(form_data.get('droidcam_port'), current_settings.get('droidcam_port', 4747)),
        'picam_awb_mode': parse_int(form_data.get('picam_awb_mode'), current_settings.get('picam_awb_mode', 0))
    }