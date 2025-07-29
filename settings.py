import json

def load_settings(file):
    """
    Load settings from a JSON file.

    Args:
        file (str): Path to the JSON settings file.

    Returns:
        dict: Loaded settings as a dictionary.
              If the file does not exist, returns default settings.
    """
    try:
        # Open the file in read mode and parse JSON contents
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # If the file is not found, return default settings dictionary
        return {
            'background_capture_interval': '60',
            'camera_source': 'droidcam',
            'droidcam_ip': '0.0.0.0',
            'droidcam_port': '0000',
            'picam_awb_mode': 1
        }


def save_settings(file, settings):
    """
    Save settings dictionary to a JSON file.

    Args:
        file (str): Path to the JSON settings file.
        settings (dict): Settings dictionary to save.

    Returns:
        None
    """
    # Open the file in write mode and write the JSON with indentation for readability
    with open(file, 'w') as f:
        json.dump(settings, f, indent=2)
