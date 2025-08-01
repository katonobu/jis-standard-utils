import os
import re
import json
import glob
from lib.utils import get_settings, get_std_dir, get_latest_dir

def extrat_page(json_file_path):
    head_offset_str = {
        "0_142":"",
        "142_170":"  ",
        "170_180":"    ",
        "180_210":"      ",
        "210_240":"        ",
        "240_250":"          ",
        "250_400":"            ",
    }

    contents = []
    if os.path.isfile(json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
        # 矩形y軸でソートして処理する
        for p in sorted(obj["paragraphs"], key=lambda x: x['box'][1]):
            x = p['box'][0]
            for key in head_offset_str:
                splitted = key.split('_')
                if int(splitted[0], 10) <= x < int(splitted[1], 10):
                    contents.append(head_offset_str[key] + p['contents'])
                    break
    return contents

def extract_section(page_objs):
    titles = []

    exp_section = None
    to_be_skipped = True

    # 各ページを舐めながら、必要な行だけ行単位のリストに追加
    all_lines = []
    for page in page_objs[1:]:
        if 1 < len(page) and re.match(r'^\d+$', page[0]) and re.match(r'^.*\d+ : \d+.+$', page[1]):
            to_be_appended_lines = page[2:]
        else:
            to_be_appended_lines = page
        if to_be_skipped:
            if 0 < len(to_be_appended_lines):
                for line in to_be_appended_lines:
                    if line.strip() == "0 序文":
                        exp_section = 0
                        init_section_title = line.strip()
                        to_be_skipped = False
                        break
                    elif line.strip() == "序文":
                        exp_section = 1
                        init_section_title = line.strip()
                        to_be_skipped = False
                        break
                    else:
                        titles.append(line.strip())

        if not to_be_skipped:
            all_lines += to_be_appended_lines

    sections = []
    section_obj = {
        "section_title":init_section_title
    }
    subsection_obj = None
    lines = []
    empty_section = ""
    for line in all_lines:
        stripped = line.strip()
        if stripped == "序文" or stripped in titles:
            continue
        elif re.match(r'^\d+ \.*$', stripped) and int(stripped.split(" ")[0], 10) == exp_section:
            exp_section += 1
            if 0 < len(lines):
                if subsection_obj is None and section_obj is not None:
                    section_obj["sentences"] = lines
                    lines = []
                    sections.append(section_obj)
                    section_obj = {
                        "section_title": stripped,
                    }
                elif subsection_obj is not None and section_obj is not None:
                    subsection_obj["sentences"] = lines
                    lines = []
                    if "subsections" not in section_obj:
                        section_obj["subsections"] = []
                    section_obj["subsections"].append(subsection_obj)
                    subsection_obj = None
                    sections.append(section_obj)
                    section_obj = {
                        "section_title": stripped,
                    }
        elif re.match(r'^\d+\.\d+ .*$', stripped):
            print(stripped)
            if subsection_obj is not None:
                subsection_obj["sentences"] = lines
                lines = []
                if "subsections" not in section_obj:
                    section_obj["subsections"] = []
                section_obj["subsections"].append(subsection_obj)
            subsection_obj = {
                "subsection_title": stripped,
            }
        elif re.match(r'^\d+\.\d+$', stripped):
            empty_section = stripped
        elif 0 < len(empty_section):
            empty_section = ""
            if subsection_obj is not None:
                subsection_obj["sentences"] = lines
                lines = []
                if "subsections" not in section_obj:
                    section_obj["subsections"] = []
                section_obj["subsections"].append(subsection_obj)
            subsection_title = f'{empty_section} {stripped.split("(")[0]}'
            print(subsection_title)
            subsection_obj = {
                "subsection_title": subsection_title,
                "subsection_subtitle":f'({"(".join(stripped.split("(")[1:])}'
            }
        else:
            lines.append(line)
    if subsection_obj is None:
        subsection_obj["sentences"] = lines
        if "subsections" not in section_obj:
            section_obj["subsections"] = []
        section_obj["subsections"].append(subsection_obj)
    else:
        section_obj["sentences"] = lines
    sections.append(section_obj)
    return {
        "titles": titles,
        "sections": sections,
    }

if __name__ == "__main__":
    target_std_str, _, _  = get_settings()
    if target_std_str:
        base_dir = get_std_dir(target_std_str)
        if base_dir:
            src_dir = get_latest_dir(base_dir, 'ocred_*', key_func=lambda x: int(x.split('_')[-1], 10))
            pages = []
            for src_file in glob.glob(os.path.join(src_dir, '*.json')):
                print(f'Processing {os.path.basename(src_file)}')
                pages.append(extrat_page(src_file))
            with open(os.path.join(base_dir, "pages.json"), 'w', encoding='utf-8') as f:
                json.dump(pages, f, ensure_ascii=False, indent=2)
            analysed_obj = extract_section(pages)
            with open(os.path.join(base_dir, "analysed.json"), 'w', encoding='utf-8') as f:
                json.dump(analysed_obj, f, ensure_ascii=False, indent=2)