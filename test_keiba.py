import os

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_race_result(base_url, target_race, start_year, stop_year=2024):
    for year in range(start_year, stop_year):
        print(f'year : {year}')

        url = base_url + str(year) + target_race

        # HTTP GETリクエストを送信し、HTMLを取得
        response = requests.get(url)

        # ステータスコードが200（成功）でない場合はエラーを表示
        if response.status_code != 200:
            print("ページの取得に失敗しました。")
        else:
            # HTMLをBeautiful Soupでパース（エンコーディングを指定）
            soup = BeautifulSoup(
                response.content, 'html.parser', from_encoding='utf-8'
            )

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
    # target address
    base_url = 'https://race.netkeiba.com/race/result.html?race_id='
    # base_url = 'https://race.netkeiba.com/race/result.html?race_id=\
    #             202306010111'

    target_race = '06010111'

    get_race_result(base_url, target_race, 2013, 2024)


if __name__ == '__main__':
    main()
