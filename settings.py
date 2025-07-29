import json

# Function to load current settings out of json
def load_settings(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'camera_source': 'droidcam'}

# Function to save changes to the settings to json
def save_settings(file, settings):
    with open(file, 'w') as f:
        json.dump(settings, f, indent=2)