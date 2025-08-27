import os
import time as t

import requests
from bs4 import BeautifulSoup


def extract_race_result(file_path):
    # HTMLファイルを読み込む
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")
    # レース結果のテーブルを取得
    result_table = soup.find("table", class_="RaceTable01")

    if not result_table:
        print("レース結果のテーブルが見つかりませんでした。")
        return

    # テーブルの行を取得
    rows = result_table.find_all("tr")[1:]  # ヘッダー行をスキップ

    return rows


def extract_horse_names(rows):
    # 着順と馬名を抽出
    for row in rows:
        columns = row.find_all("td")
        if len(columns) >= 4:  # 必要なカラム数を確認
            rank = columns[0].text.strip()  # 着順
            horse_name = columns[3].text.strip()  # 馬名
            print(f"着順: {rank}, 馬名: {horse_name}")


def get_race_result(base_url, target_year, place, time, day, race):
    place_dict = {
        "01": "sapporo",
        "02": "hakodate",
        "03": "fukushima",
        "04": "niigata",
        "05": "tokyo",
        "06": "nakayama",
        "07": "chukyo",
        "08": "kyoto",
        "09": "hanshin",
        "10": "kokura",
    }
    url = f"{base_url}{target_year}{place}{time}{day}{race}"
    print(f"URL: {url}")
    # User-Agentを指定
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:136.0) Gecko/20100101 Firefox/136.0"
    }

    # target_race_nameのディレクトリが存在しない場合作成
    target_dir = f"race_results{os.sep}{target_year}{os.sep}{place_dict[place]}{os.sep}{time}{os.sep}{day}"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    file_name = f"{target_dir}{os.sep}{race}.html"

    # ファイルがすでに存在している場合はスキップ
    if os.path.exists(file_name):
        print(f"{file_name} はすでに存在します。スキップします。")
        return True

    # HTTP GETリクエストを送信し、HTMLを取得
    response = requests.get(url, headers=headers)

    # ステータスコードが200（成功）でない場合はエラーを表示
    if response.status_code != 200:
        print("ページの取得に失敗しました。")
        print(f"ステータスコード: {response.status_code}")
    else:
        # レスポンス内容を.htmlファイルとして保存
        # レスポンスのエンコーディングを明示的に設定
        response.encoding = (
            response.apparent_encoding
        )  # サーバーが指定するエンコーディングを推測

        # HTMLをBeautiful Soupでパース（エンコーディングを指定）
        soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

        # レース結果のテーブルを取得
        result_table = soup.find("table", class_="RaceTable01")

        # レース結果のテーブルが存在する場合のみレスポンスの内容をファイルに書き込む
        if result_table:
            with open(file_name, "w", encoding="utf-8") as file:
                file.write(response.text)
            print(f"{file_name} に保存しました。")
            t.sleep(3)  # 3秒待機
            return True
        else:
            print(f"{file_name}にはレース結果のテーブルが見つかりませんでした。")
            t.sleep(3)  # 3秒待機
            return False


# 年単位ですべてのレース結果を取得する場合
def get_race_results_per_year(target_year):
    base_url = "https://race.netkeiba.com/race/result.html?race_id="

    # 最初の2桁は開催場所
    # （01：札幌、02：函館、03：福島、04：新潟、05:東京、06：中山、07：中京、08：京都、09：阪神、10：小倉）
    # 次の2桁は開催数
    # 次の2桁は開催日
    # 最後の2桁はレース番号
    # 例：06010111←中山開催1回目1日目11レース

    places = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
    times = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10"]
    days = ["01", "02", "03", "04", "05", "06", "07", "08"]
    races = [
        "01",
        "02",
        "03",
        "04",
        "05",
        "06",
        "07",
        "08",
        "09",
        "10",
        "11",
        "12",
    ]

    # すべての組み合わせを取得
    get_result = True
    get_result_tmp = True

    for place in places[:]:
        if not get_result:
            get_result = True
        for time in times:
            # 同一開催場所で連続で開催回の結果が取得できない場合はスキップ
            if get_result == False and get_result_tmp == False:
                break
            get_result_tmp = get_result
            if not get_result:
                get_result = True
            for day in days:
                if not get_result:
                    break
                for race in races:
                    get_result = get_race_result(
                        base_url, target_year, place, time, day, race
                    )
                    if not get_result:
                        break


def main():
    start_year = 2020
    end_year = 2025

    for year in range(start_year, end_year + 1):
        get_race_results_per_year(year)


if __name__ == "__main__":
    main()
