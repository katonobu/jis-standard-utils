import os
import cv2
import glob
import numpy as np
from lib.utils import get_latest_dir

# 日本語ファイル名対応の読み込み
def load_image_unicode(path):
    with open(path, 'rb') as f:
        img_array = np.asarray(bytearray(f.read()), dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
def save_image_unicode(path, image):
    ext = os.path.splitext(path)[1]  # 拡張子（例: .png）
    success, encoded_image = cv2.imencode(ext, image)
    if success:
        with open(path, 'wb') as f:
            f.write(encoded_image.tobytes())
        return True
    else:
        return False    

def gamma_correction(image, gamma=0.5):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)


def detect_cropped_rect(file):    # 画像読み込み
    image = load_image_unicode(file)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # ガンマ補正でコントラスト強調
    corrected = gamma_correction(gray, gamma=0.5)

    # ノイズ除去（ぼかし）
    blurred = cv2.GaussianBlur(corrected, (5, 5), 0)

    # Cannyエッジ検出（しきい値は調整可能）
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # 輪郭抽出
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 最大の矩形領域を選定
    max_area = 0
    best_rect = None
    height, width = gray.shape
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h

        # サイズフィルタ：画像全体の80%以上は除外
        if area < width * height * 0.8 and area > 10000:
            if area > max_area:
                max_area = area
                best_rect = (x, y, w, h)

    return best_rect

def crop(org_file_path_name, rect, output_file_path_name):
    # 画像読み込み
    image = load_image_unicode(org_file_path_name)
    x, y, w, h = rect
    roi = image[y:y+h, x:x+w]
    save_image_unicode(output_file_path_name, roi)

def gamma_correction(image, gamma=0.5):
    inv_gamma = 1.0 / gamma
    table = np.array([(i / 255.0) ** inv_gamma * 255 for i in range(256)]).astype("uint8")
    return cv2.LUT(image, table)

def binarize(cropped_file_path_name, output_file_path_name, gamma=1.5):
    # 画像読み込み
    image = load_image_unicode(cropped_file_path_name)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    corrected = gamma_correction(gray, gamma)

    # 二値化
    th, binary = cv2.threshold(corrected, 128, 255, cv2.THRESH_OTSU)
    
    # 保存
    save_image_unicode(output_file_path_name, binary)

def crop_and_binarize(base_dir):
    import json
    rects = []
    latest_dir = get_latest_dir(base_dir, 'capture_*', key_func=lambda x: int(x.split('_')[-1], 10))
    if latest_dir:
        png_files = glob.glob(os.path.join(latest_dir, '*.png'))
        for file in png_files:
            print(f'Processing {file}')
            rect = detect_cropped_rect(file)
            if rect:
                rects.append(rect)
            else:
                print('No suitable rectangle found.')

        # 平均矩形を算出
        if rects:
            avg_x = int(np.mean([r[0] for r in rects]))
            avg_y = int(np.mean([r[1] for r in rects]))
            avg_w = int(np.mean([r[2] for r in rects]))
            avg_h = int(np.mean([r[3] for r in rects]))
            print(f'平均矩形: x={avg_x}, y={avg_y}, w={avg_w}, h={avg_h}')

            # 平均矩形で各画像を切り出し/透かし除去
            for file in png_files:
                filename = os.path.basename(file)

                # 切り出す
                cropped_folder_path = os.path.join(os.path.dirname(file), "..", file.split(os.path.sep)[-2].replace('capture_', 'cropped_'))
                os.makedirs(cropped_folder_path, exist_ok=True)
                cropped_path_file_name = os.path.join(cropped_folder_path, filename)
                crop(file, (avg_x, avg_y, avg_w, avg_h), cropped_path_file_name)

                # 透かしを除去
                binaried_folder_path = os.path.join(os.path.dirname(file), "..", file.split(os.path.sep)[-2].replace('capture_', 'binarized_'))
                os.makedirs(binaried_folder_path, exist_ok=True)
                binarized_path_file_name = os.path.join(binaried_folder_path, filename)
                binarize(cropped_path_file_name, binarized_path_file_name)


if __name__ == "__main__":
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'Q9000')
    crop_and_binarize(base_dir)
