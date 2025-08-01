from lib.utils import get_settings, get_std_dir
from lib.crop_page import crop_and_binarize

if __name__ == "__main__":
    target_std_str, _, _  = get_settings()
    if target_std_str:
        base_dir = get_std_dir(target_std_str)
        crop_and_binarize(base_dir)
