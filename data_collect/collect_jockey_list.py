import glob
import os
import re
from copy import deepcopy

import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm


# 文字化け判定関数
def is_garbled(text):
    # 日本語文字（ひらがな・カタカナ・漢字）の割合を調べる
    jp_chars = re.findall(r"[ぁ-んァ-ン一-龥]", text)
    ratio = len(jp_chars) / (len(text) + 1e-5)
    # 文字化け文字（�や?）の割合を調べる
    garbled_chars = re.findall(r"[�?]", text)
    garbled_ratio = len(garbled_chars) / (len(text) + 1e-5)
    # 日本語が少なく、文字化け文字が多い場合はTrue
    return ratio < 0.05 or garbled_ratio > 0.05


def get_race_data():
    # htmlファイルの取得
    target_dir = "race_results/"
    html_files = glob.glob(target_dir + "**/*.html", recursive=True)
    print(len(html_files), "files found.")

    # 保存するデータのフォーマット定義
    jockey_name_list = []

    for i, html_file in enumerate(tqdm(html_files, desc="Processing race results")):
        with open(html_file, encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")

            # 文字化けチェック
            body_text = soup.get_text()
            if is_garbled(body_text):
                print(f"Skipping garbled file: {html_file}")
                continue  # 文字化けしている場合はスキップ
            # すべての着順の行を取得
            rows = soup.select("table#All_Result_Table tbody tr.HorseList")

            for j, row in enumerate(rows):
                # 騎手
                jockey = row.select_one("td.Jockey a").text.strip()
                # 騎手名のみ（漢字ひらがなカタカナアルファベットとカンマ）を抽出
                jockey = "".join(
                    re.findall(
                        r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ffA-Za-zＡ-Ｚａ-ｚ.,．]+",
                        jockey,  # 全角ピリオドを追加
                    )
                )
                if jockey not in jockey_name_list:
                    jockey_name_list.append(jockey)
                    # 騎手名がカタカナの場合は出力する
                    if re.match(r"^[\u30a0-\u30ff]+$", jockey):
                        """print(jockey)
                        print(html_file)"""

    # ファイルに出力
    with open("jockey_list.txt", "w", encoding="utf-8") as file:
        for jockey in jockey_name_list:
            file.write(jockey + "\n")


if __name__ == "__main__":
    get_race_data()
