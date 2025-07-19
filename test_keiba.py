import os

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_race_result(
    base_url, target_race, target_race_name, start_year, stop_year=2024
):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }
    for year in range(start_year, stop_year):
        print(f"year : {year}")

        url = base_url + str(year) + target_race

        # HTTP GETリクエストを送信し、HTMLを取得
        response = requests.get(url, headers=headers)
        # ステータスコードを確認

        # ステータスコードが200（成功）でない場合はエラーを表示
        if response.status_code != 200:
            print("ページの取得に失敗しました。")
            print(f"URL: {url}")
        else:
            # レスポンス内容を.htmlファイルとして保存
            # レスポンスのエンコーディングを明示的に設定
            response.encoding = (
                response.apparent_encoding
            )  # サーバーが指定するエンコーディングを推測
            # target_race_nameのディレクトリが存在しない場合作成
            if not os.path.exists(f"race_results{os.sep}{target_race_name}"):
                os.makedirs(f"race_results{os.sep}{target_race_name}")

            file_name = (
                f"race_results{os.sep}{target_race_name}{os.sep}race_result_{year}.html"
            )

            # ファイルがすでに存在している場合はスキップ
            if os.path.exists(file_name):
                print(f"{file_name} はすでに存在します。スキップします。")
                continue

            # レスポンスの内容をファイルに書き込む
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"{file_name} に保存しました。")

            # HTMLをBeautiful Soupでパース（エンコーディングを指定）
            soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

            result_table = soup.find("table", class_="RaceTable01")
            if result_table:
                # レース結果の表をループしてデータを出力
                # 最初の行はヘッダーなのでスキップ
                for i, row in enumerate(result_table.find_all("tr")[1:]):
                    if i >= 5:
                        break
                    columns = row.find_all("td")
                    if len(columns) >= 10:  # レース結果のカラム数を確認
                        position = columns[0].text.strip()  # 着順
                        horse_name = columns[3].text.strip()  # 馬名
                        jockey = columns[6].text.strip()  # 騎手
                        time = columns[7].text.strip()  # タイム
                        popular = columns[9].text.strip()
                        odds = columns[10].text.strip()
                        print(
                            f"{position}: {horse_name} ({jockey}) {popular}人気\
                              {odds}倍 - タイム: {time}"
                        )
            result_harontime = soup.find(
                "table", class_="RaceCommon_Table Race_HaronTime"
            )
            if result_harontime:
                for row in result_harontime.find_all("tr")[2:]:
                    columns = row.find_all("td")
                    for column in columns:
                        print(column.text)


def main():
    # ベースURLとレースIDテンプレートを設定
    base_url = "https://race.netkeiba.com/race/result.html?race_id="
    race_id_template = "05010111"  # 天皇賞・春のレースIDテンプレート（例）
    target_race_name = "test"  # 保存先のディレクトリ名

    # 過去10年分のデータを取得
    start_year = 2025
    stop_year = 2026
    get_race_result(base_url, race_id_template, target_race_name, start_year, stop_year)


if __name__ == "__main__":
    main()
