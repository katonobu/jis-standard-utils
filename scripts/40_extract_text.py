import os
import glob
import subprocess
from lib.utils import get_settings, get_std_dir, get_latest_dir

if __name__ == "__main__":
    target_std_str, _, _  = get_settings()
    if target_std_str:
        base_dir = get_std_dir(target_std_str)
        if base_dir:
            src_dir = get_latest_dir(base_dir, 'binarized_*', key_func=lambda x: int(x.split('_')[-1], 10))
            if src_dir:
                dst_dir = os.path.join(base_dir, os.path.basename(src_dir).replace('binarized_', 'ocred_'))
                os.makedirs(dst_dir, exist_ok=True)
                for src_file in glob.glob(os.path.join(src_dir, '*.png')):
                    tmp_file_name = f'{os.path.basename(src_dir)}_{os.path.basename(src_file).replace(".png", "")}_p1.json'
                    tmp_file = os.path.join(dst_dir, tmp_file_name)
                    dst_file = os.path.join(dst_dir, f'{os.path.basename(src_file).replace(".png", "")}.json')
                    if os.path.isfile(dst_file):
                        print(f'Skipping {dst_file} as it already exists.')
                        continue
                    else:
                        if not os.path.isfile(tmp_file):
                            print(f'Extracting text from {os.path.basename(src_file)}')
                            cmds = [
                                "yomitoku",
                                src_file,
                                "-f", "json",
                                "-o", dst_dir,
                            ]
                            procObj = subprocess.run(cmds, stdout=subprocess.PIPE)
                            outputStr = procObj.stdout.decode('utf-8')
                            print(outputStr)
                            if procObj.returncode != 0:
                                print(f'Error extracting text from {os.path.basename(src_file)}: {os.path.basename(outputStr)}')
                                break
                        else:
                            print(f'Using existing temporary file: {os.path.basename(tmp_file)}')
                        os.rename(tmp_file, dst_file)
