import os
import json
from lib.crop_page import crop_and_binarize

if __name__ == "__main__":
    setting_json_path = os.path.join(os.path.dirname(__file__), '..', 'settings.json')
    if os.path.exists(setting_json_path):
        with open(setting_json_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        target_std_str = settings.get('target_std_str', 'Q9000')
        user = settings.get('user', 'invalid_use_name')
        pw = settings.get('pw', 'invalid_password')

        base_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs', target_std_str)
        crop_and_binarize(base_dir)
    else:
        print(f'Settings file not found: {setting_json_path}')
        print('Please create a settings.json file with the required parameters.')
        print('Example file exists at settings_sample.json')
        print('Exiting...')
