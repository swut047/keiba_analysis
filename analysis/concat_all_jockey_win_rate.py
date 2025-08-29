import os
import pandas as pd
import glob
from pathlib import Path

def find_and_merge_csv(directory_path, output_file):
    """
    指定されたディレクトリ内のCSVファイルを再帰的に探索し、
    すべてのCSVファイルを結合して1つのファイルとして出力する

    Args:
        directory_path: CSVファイルを探索するディレクトリパス
        output_file: 出力ファイルのパス

    Returns:
        bool: 処理が成功したかどうか
    """
    # 1. 再帰的にCSVファイルを探索
    csv_files = glob.glob(os.path.join(directory_path, '**', '*.csv'), recursive=True)

    if not csv_files:
        print(f"No CSV files found in {directory_path}")
        return False

    print(f"Found {len(csv_files)} CSV files.")

    # 2. ファイルを読み込む
    dataframes = []
    for file in csv_files:
        try:
            df = pd.read_csv(file)
            # 騎手名の列を追加
            path_obj = Path(file)
            parent_dir = path_obj.parent.name
            # 一番左の列に騎手名を追加
            df.insert(0, '騎手名', [parent_dir] * len(df))
            dataframes.append(df)
            print(f"Read {file} successfully.")
        except Exception as e:
            print(f"Error reading {file}: {e}")

    if not dataframes:
        print("No data to merge.")
        return False


    # 3. 全てのデータフレームを結合
    merged_df = pd.concat(dataframes, ignore_index=True)

    # 4. 結合したデータを出力
    merged_df.to_csv(os.path.join(output_file), index=False)
    print(f"Merged data saved to {output_file}")

    return True

# 使用例
if __name__ == "__main__":
    # 探索するディレクトリのパス
    directory_path = "analysis/win_rate_results"
    # 出力ファイルのパス
    output_file = "analysis/win_rate_concat.csv"

    find_and_merge_csv(directory_path, output_file)
