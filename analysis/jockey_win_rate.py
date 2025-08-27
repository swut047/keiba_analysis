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


# htmlファイルの取得
target_dir = "race_results/"
html_files = glob.glob(target_dir + "**/*.html", recursive=True)
print(len(html_files), "files found.")

# レース開催地一覧
place_list = [
    "札幌",
    "函館",
    "福島",
    "新潟",
    "東京",
    "中山",
    "中京",
    "京都",
    "阪神",
    "小倉",
]

# 保存するデータのフォーマット定義
target_race_results = {"1着": 0, "2着": 0, "3着": 0, "4着以下": 0}
target_return_rate = {"単勝回収率": 0.0, "複勝回収率": 0.0}
target_jockey_name = []
target_jockey_foreign, target_jockey_foreign_dict = [], {}
target_results_dict = {}

# 対象となる騎手をテキストから読み込む
filepath = "jockey_list.txt"
with open(filepath, "r", encoding="utf-8") as file:
    target_jockey_name = file.read().splitlines()

# 表記ゆれの外人への対応
filepath = "jockey_corresponding.txt"
with open(filepath, "r", encoding="utf-8") as file:
    target_jockey_foreign = file.read().splitlines()
    for line in target_jockey_foreign:
        if line.strip():
            # 騎手名と対応する表記を分割
            parts = line.split(" ")
            if len(parts) == 2:
                target_jockey_foreign_dict[parts[0]] = parts[1]


for jockey in target_jockey_name:
    target_results_dict[jockey] = {}

for i, html_file in enumerate(tqdm(html_files, desc="Processing race results")):
    """if i > 1000:
    break"""

    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # 文字化けチェック
    body_text = soup.get_text()
    if is_garbled(body_text):
        print(f"Skipping garbled file: {html_file}")
        continue  # 文字化けしている場合はスキップ

    race_data = soup.find("div", class_="RaceData01")

    if not race_data:
        continue  # レース情報がない場合はスキップ

    # レース情報の取得(馬場、距離、開催地)
    text = race_data.get_text()
    if "芝" in text:
        course_type = "芝"
    elif "ダ" in text:
        course_type = "ダート"
    else:
        course_type = "障害"

    distance_match = re.search(r"([芝ダ障])(\d+)m", text)
    if distance_match:
        distance = int(distance_match.group(2))

    # 開催場所はタイトルや見出しから抽出
    title = soup.title.string if soup.title else ""
    place_match = re.search(r"\d{4}年\d+月\d+日\s*([^\d]+)\d+R", title)
    place = place_match.group(1).strip() if place_match else None

    race_info = place + course_type + str(distance) + "m"  # 例：東京芝1600m

    # 複勝の払戻テーブル行を取得
    fukusho_row = soup.select_one("tr.Fukusho")
    # 払戻金
    payouts = [
        x.strip("</br></br>").replace("円", "")
        for x in fukusho_row.select_one("td.Payout span")
        .decode_contents()
        .split("<br>")
    ]
    payouts = [pay.replace(",", "") for pay in payouts]

    # すべての着順の行を取得
    rows = soup.select("table#All_Result_Table tbody tr.HorseList")

    # 着順を含む要素を抽出
    ranks = soup.select("td.Result_Num div.Rank")
    # 着順をリストに格納
    rankings = [rank.text.strip() for rank in ranks if rank.text.strip()]

    # 単勝の払い戻し金額を含む要素を抽出
    tansho_payout_element = soup.select_one("tr.Tansho td.Payout span")

    # 金額を取得
    if tansho_payout_element:
        try:
            tansho_payout = [
                float(tansho_payout_element.text.strip("円").replace(",", "")) / 100
            ]
        except ValueError:  # 1着が同着の場合
            # print(f"Invalid payout format in {html_file}")
            tansho_payout = [
                float(payout.replace(",", "")) / 100
                for payout in tansho_payout_element.text.split("円")[:2]
            ]

    for j, row in enumerate(rows):
        # 馬名
        horse_name = row.select_one("span.Horse_Name a").text.strip()
        # 騎手
        jockey = row.select_one("td.Jockey a").text.strip()
        # 騎手名のみ（漢字ひらがなカタカナアルファベット）を抽出
        jockey = "".join(
            re.findall(
                r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ffA-Za-zＡ-Ｚａ-ｚ.,．]+",
                jockey,  # 全角ピリオドを追加
            )
        )

        if jockey in target_jockey_name:
            # 表記ゆれの騎手への対応
            if jockey in target_jockey_foreign_dict.keys():
                jockey = target_jockey_foreign_dict[jockey]

            # レース情報がまだ登録されていない場合は初期化
            if race_info not in target_results_dict[jockey].keys():
                target_results_dict[jockey][race_info] = {}
                target_results_dict[jockey][race_info]["race_results"] = deepcopy(
                    target_race_results
                )
                target_results_dict[jockey][race_info]["return_rate"] = deepcopy(
                    target_return_rate
                )

            # 1着の場合
            if rankings[j] == "1":
                if '中村' in jockey:
                    print(f"Processing {jockey} in file: {html_file} {race_info}")
                target_results_dict[jockey][race_info]["race_results"]["1着"] += 1
                target_results_dict[jockey][race_info]["return_rate"][
                    "単勝回収率"
                ] += tansho_payout[j]
                target_results_dict[jockey][race_info]["return_rate"]["複勝回収率"] += (
                    float(payouts[0]) / 100
                )
            # 2着の場合
            if rankings[j] == "2":
                target_results_dict[jockey][race_info]["race_results"]["2着"] += 1
                target_results_dict[jockey][race_info]["return_rate"]["複勝回収率"] += (
                    float(payouts[1]) / 100
                )
            # 3着の場合
            if rankings[j] == "3":
                if len(payouts) < 3:
                    # 7頭以下のレースでは2着までしか複勝がない場合がある
                    target_results_dict[jockey][race_info]["race_results"][
                        "4着以下"
                    ] += 1
                else:
                    target_results_dict[jockey][race_info]["race_results"]["3着"] += 1
                    target_results_dict[jockey][race_info]["return_rate"][
                        "複勝回収率"
                    ] += (float(payouts[2]) / 100)
            # 4着以下の場合
            else:
                target_results_dict[jockey][race_info]["race_results"]["4着以下"] += 1


# 単勝/複勝回収率の計算
for jockey in target_results_dict.keys():
    for key in target_results_dict[jockey].keys():
        target_race_results_tmp = deepcopy(
            target_results_dict[jockey][key]["race_results"]
        )
        target_return_rate_tmp = deepcopy(
            target_results_dict[jockey][key]["return_rate"]
        )

        race_count = sum(
            [target_race_results_tmp[key] for key in target_race_results_tmp.keys()]
        )
        if race_count == 0:
            print(f"Skipping jockey: {jockey} {key}")
            print("skip")
            continue
        target_return_rate_tmp["単勝回収率"] = round(
            target_return_rate_tmp["単勝回収率"] / race_count, 2
        )
        target_return_rate_tmp["複勝回収率"] = round(
            target_return_rate_tmp["複勝回収率"] / race_count, 2
        )

        target_results_dict[jockey][key]["race_results"] = target_race_results_tmp
        target_results_dict[jockey][key]["return_rate"] = target_return_rate_tmp

# 結果の出力
for jockey in target_results_dict.keys():
    flat_data = []
    for course, info in target_results_dict[jockey].items():
        row = {"コース": course}
        row.update(info["race_results"])
        row.update(info["return_rate"])
        flat_data.append(row)

    if len(flat_data) == 0:
        print(f"Processing jockey: {jockey}")
        continue

    df = pd.DataFrame(flat_data)

    # 集計結果を保存
    save_dir = f"win_rate_results/{jockey}/"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    df = df.sort_values("コース")
    df.to_csv(os.path.join(save_dir, "output.csv"), index=False)
