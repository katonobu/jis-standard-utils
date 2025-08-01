import os
import json
import glob

def get_settings():
    setting_json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
    if os.path.exists(setting_json_path):
        with open(setting_json_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        target_std_str = settings.get('target_std_str', 'Q9000')
        user = settings.get('user', 'invalid_use_name')
        pw = settings.get('pw', 'invalid_password')
        return target_std_str, user, pw
    else:
        print(f'Settings file not found: {setting_json_path}')
        print('Please create a settings.json file with the required parameters.')
        print('Example file exists at settings_sample.json')
        print('Exiting...')
        return None, None, None


def get_std_dir(target_std_str):
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', target_std_str)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def get_latest_dir(base_dir, glob_str, key_func=lambda x:int(x.split('_')[-1], 10)):
    sorted_dirs = sorted(
        [d for d in glob.glob(os.path.join(base_dir, glob_str)) if os.path.isdir(d)],
        key=key_func,
        reverse=True
    )
    if 0 < len(sorted_dirs):
        return sorted_dirs[0]
    else:
        print(f'No directories found matching {glob_str} in {base_dir}')
        return None

