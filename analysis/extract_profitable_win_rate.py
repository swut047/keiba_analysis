import pandas as pd


def extract_profitable_win_rate(target_file, course, min_race_count, max_tanshou_ave, max_fukushou_ave):
    df = pd.read_csv(target_file)

    for i, (tanshou, fukushou) in enumerate(zip(df['単勝回収率'], df['複勝回収率'])):
        results = []
        for i, (tanshou, fukushou) in enumerate(zip(df['単勝回収率'], df['複勝回収率'])):
            if not course or course not in df['コース'][i]:
                continue
            if tanshou >= 1 or fukushou >= 1:
                race_count = df['1着'][i] + df['2着'][i] + df['3着'][i] + df['4着以下'][i]
                tanshou_count = df['1着'][i]
                fukushou_count = df['1着'][i] + df['2着'][i] + df['3着'][i]

                ave_tanshou = tanshou * race_count / tanshou_count if tanshou_count > 0 else -1
                ave_fukushou = fukushou * race_count / fukushou_count if fukushou_count > 0 else -1

                result_found = False
                if tanshou >= 1:
                    if ave_tanshou < max_tanshou_ave and race_count >= min_race_count:
                        result_found = True
                if fukushou >= 1 and not result_found:
                    if ave_fukushou < max_fukushou_ave and race_count >= min_race_count:
                        result_found = True

                if result_found:
                    results.append({
                        '騎手名': df['騎手名'][i],
                        'コース': df['コース'][i],
                        '成績': f"{df['1着'][i]}-{df['2着'][i]}-{df['3着'][i]}-{df['4着以下'][i]}",
                        '単勝回収率': f"{tanshou:.2f}",
                        '複勝回収率': f"{fukushou:.2f}",
                        '単勝平均': f"{ave_tanshou:.2f}" if ave_tanshou > 0 else "N/A",
                        '複勝平均': f"{ave_fukushou:.2f}" if ave_fukushou > 0 else "N/A"
                    })

        return results


if __name__ == "__main__":
    target_file = 'win_rate_concat.csv'
    results = extract_profitable_win_rate(target_file, course='札幌', min_race_count=30, max_tanshou_ave=20, max_fukushou_ave=5.0)
    for res in results:
        print(res)
