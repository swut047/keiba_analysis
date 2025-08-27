import re
from bs4 import BeautifulSoup


def get_race_info(soup):
    # レースデータを含む要素を見つける
    race_data01 = soup.find('div', class_='RaceData01')
    race_data02 = soup.find('div', class_='RaceData02')

    # レース種類（障害3000m）を抽出
    race_type_text = race_data01.text.strip()

    # テキストから必要な部分を抽出（芝ダート障害）
    race_type_match = re.search(r'[障ダ芝]\s*(\d+)m', race_type_text)
    race_type = race_type_match.group(0) if race_type_match else "不明"

    # 開催場所を抽出
    venue_spans = race_data02.find_all('span')
    venue = venue_spans[1].text.strip() if len(venue_spans) > 1 else "不明"

    print(f"開催場所: {venue}")
    print(f"レース種類: {race_type}")

    return venue, race_type


def get_horse_info(soup):
    # 出馬表のテーブルを取得
    table = soup.find('table', class_='Shutuba_Table')

    # 馬のリストを取得
    horse_rows = table.find_all('tr', class_='HorseList')

    umaban_list, horse_name_list, jockey_list = [], [], []

    print("| 馬番 | 馬名 | 騎手 | オッズ |")
    print("|------+------+------+-------|")

    # 各馬の情報を抽出
    for row in horse_rows:
        # 馬番を取得
        umaban_td = row.find('td', class_=lambda x: x and x.startswith('Umaban'))
        umaban = umaban_td.text.strip() if umaban_td else ""

        # 馬名を取得
        horse_info = row.find('td', class_='HorseInfo')
        horse_name = horse_info.find('span', class_='HorseName').find('a').text.strip() if horse_info else ""

        # 騎手を取得
        jockey_td = row.find('td', class_='Jockey')
        jockey = jockey_td.text.strip() if jockey_td else ""

        # オッズを取得
        odds_td = row.find('td', class_='Txt_R Popular')
        odds_span = odds_td.find('span') if odds_td else None
        odds = odds_span.text.strip() if odds_span else ""

        print(f"| {umaban} | {horse_name} | {jockey} | {odds} |")

        umaban_list.append(umaban)
        horse_name_list.append(horse_name)
        jockey_list.append(jockey)

    return umaban_list, horse_name_list, jockey_list

# HTMLファイルを読み込む
with open('../data_collect/next_week_sample.html', 'r', encoding='euc-jp') as file:
    html_content = file.read()

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(html_content, 'html.parser')

# レース情報を取得
venue, race_type = get_race_info(soup)

# 馬情報を取得
umaban_list, horse_name_list, jockey_list = get_horse_info(soup)
