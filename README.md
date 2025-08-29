# keiba_analysis
tools for analyzing keiba made with python

## 使い方

### データ収集

- レース結果をnetkeibaから収集（例：2020~2025までのレース結果を取得）
```python data_collect/get_race_results.py --start_year 2020 --end_year 2025```
- レース結果から騎手一覧を取得
``` python3 data_collect/collect_jockey_list.py```

### 分析

- 各騎手の勝率をコース別に算出
``` python3 analysis/jockey_win_rate.py```
- 回収率が1を超える騎手とコースの組み合わせを抽出
``` python3 analysis/extract_profitable_win_rate.py```

### GUI

- GUIで分析を行う
  - コース名やその他条件を指定するとそれらに合致する条件下で回収率が1を超える騎手を表示
``` python3 gui/gui_test.py```
