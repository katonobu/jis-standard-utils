import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_element(driver, xpath, retry_count = 10, retry_interval = 1):
    """指定されたXPathの要素を取得する。見つからない場合はNoneを返す。"""
    for count in range(retry_count):
        try:
            element = driver.find_element("xpath", xpath)
            if element:
                if 0 < count:
                    print("O")
                return element
        except Exception as e:
            print(f"Error finding elements with xpath '{xpath}': {e}")
        time.sleep(retry_interval)
        print('.', end="", flush=True)

def capture_pages(driver, url, target_std_str, output_dir, user, pw):
    driver.get(url)

    # 検索ページで検索対象を入力
    input_field_ele = get_element(driver, '//*[@id="label-f01"]')
    input_field_ele.send_keys(target_std_str)

    list_input_ele = get_element(driver, '//*[@id="main"]/form[1]/div/div/input')
    list_input_ele.click()

    time.sleep(3)

    # 一覧表示で出てきたJISリストの規格番号のリンククリック
    link_ele = get_element(driver, '//*[@id="form"]/table/tbody/tr/td[1]/a')
    driver.execute_script("arguments[0].click();", link_ele)

    time.sleep(3)

    # 規格詳細画面のPDFファイルのリンクをクリック
    link_ele = get_element(driver, '//*[@id="form"]/table[2]/tbody/tr/td[2]/a')
    driver.execute_script("arguments[0].click();", link_ele)

    time.sleep(3)

    # ログインページでログイン
    user_id_ele = get_element(driver, '//*[@id="userId"]')
    user_id_ele.send_keys(user)
    time.sleep(1)
    pw_ele = get_element(driver, '//*[@id="form"]/center/table/tbody/tr[2]/td/input')
    pw_ele.send_keys(pw)
    time.sleep(1)
    login_ele = get_element(driver, '//*[@id="form"]/center/table/tbody/tr[3]/td/input[1]')
    driver.execute_script("arguments[0].click();", login_ele)
    
    time.sleep(3)

    # 現在のWindowハンドルの一覧を取得
    wh_before = driver.window_handles


    # 規格詳細画面に戻るのでのPDFファイルのリンクをクリック
    link_ele = get_element(driver, '//*[@id="form"]/table[2]/tbody/tr/td[2]/a')
    driver.execute_script("arguments[0].click();", link_ele)

    while True:
        # 新規Windowを開いたあとのWindowハンドル一覧を取得
        wh_after = driver.window_handles
        if set(wh_after) and set(wh_after).difference(set(wh_before)):
            # Windowハンドル一覧の比較を行い、新規で開いたWindowのハンドルを取得
            new_window = set(wh_after).difference(set(wh_before)).pop()
            if new_window:
                # 新規Windowに切り替え
                driver.switch_to.window(new_window)
                break
        time.sleep(3)

    idx = 1
    now_str = time.strftime("%Y%m%d%H%M%S", time.localtime())
    output_dir = os.path.join(output_dir, f'capture_{now_str}')
    os.makedirs(output_dir)
    val = input(f'Page {idx} Enter [n] to quie: ')
    while not val.startswith('n'):
        file_name = os.path.join(output_dir, f'{idx:03d}_{now_str}.png')
        driver.save_screenshot(file_name)
        print(f'Save to {file_name}')
        idx += 1
        val = input(f'Page {idx} Enter [n] to quie: ')
    return

def capture_standard(target_std_str, output_dir, user, pw):
    try:
        # Chromeのオプション設定
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1280,1000")  # 幅1280px, 高さ1000px

        # ChromeDriverのセットアップ
        driver = webdriver.Chrome(options=chrome_options)
        url = 'https://www.jisc.go.jp/app/jis/general/GnrJISSearch.html'

        capture_pages(driver, url, target_std_str, output_dir, user, pw)

        # Close Web Browser
        driver.quit()
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    target_std_str = 'Q9000'
    user = 'user_name'
    pw = 'password'

    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', target_std_str)
    capture_standard(target_std_str, output_dir, user, pw)