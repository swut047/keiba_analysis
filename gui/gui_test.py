import pandas as pd
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty
from kivy.graphics import Color, Rectangle
import japanize_kivy

import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Python のモジュール検索パスに追加
sys.path.insert(0, project_root)

from analysis.extract_profitable_win_rate import extract_profitable_win_rate


class BackgroundLabel(Label):
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(BackgroundLabel, self).__init__(**kwargs)
        self.bind(size=self.update_bg, pos=self.update_bg)
        # 幅が変更されたときにテキストサイズを更新
        self.bind(width=lambda instance, width: setattr(instance, 'text_size', (width, None)))

    def update_bg(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.background_color)
            Rectangle(pos=self.pos, size=self.size)


class ProfitableWinRateApp(App):
    result_text = StringProperty('')

    def build(self):
        # メインレイアウト
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # 入力エリア
        input_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
        self.file_input = TextInput(text='data_collect/win_rate_concat.csv', multiline=False)
        input_layout.add_widget(Label(text='CSVファイル名:'))
        input_layout.add_widget(self.file_input)

        # フィルタリングセクション
        filter_layout = GridLayout(cols=2, size_hint=(1, 0.2))

        self.course_filter = TextInput(text='札幌', multiline=False)
        filter_layout.add_widget(Label(text='コース名に含む文字:'))
        filter_layout.add_widget(self.course_filter)

        self.min_race_count = TextInput(text='30', multiline=False)
        filter_layout.add_widget(Label(text='最小レース数:'))
        filter_layout.add_widget(self.min_race_count)

        self.max_tanshou_ave = TextInput(text='20', multiline=False)
        filter_layout.add_widget(Label(text='単勝平均上限:'))
        filter_layout.add_widget(self.max_tanshou_ave)

        self.max_fukushou_ave = TextInput(text='5.0', multiline=False)
        filter_layout.add_widget(Label(text='複勝平均上限:'))
        filter_layout.add_widget(self.max_fukushou_ave)

        # 実行ボタン
        analyze_button = Button(text='分析実行', size_hint=(1, 0.05))
        analyze_button.bind(on_press=self.analyze_data)

        # カラム幅の定義
        self.col_widths = [0.15, 0.2, 0.25, 0.1, 0.1, 0.1, 0.1]  # 合計が1になるようにする

        # 共通のグリッドパラメータ
        grid_spacing = 2
        grid_padding = [2, 2]  # 左右、上下のパディング

        # テーブルヘッダー用のコンテナ（BoxLayout）
        header_container = BoxLayout(orientation='vertical', size_hint=(1, 0.08))

        # テーブルヘッダー
        self.header_grid = GridLayout(
            cols=7,
            spacing=grid_spacing,
            padding=grid_padding,
            size_hint=(1, 1)  # コンテナ内で全体を占める
        )

        headers = ['騎手名', 'コース', '1着-2着-3着-4着以下', '単勝回収率', '複勝回収率', '単勝平均', '複勝平均']

        for header, width in zip(headers, self.col_widths):
            header_label = BackgroundLabel(
                text=header,
                bold=True,
                halign='center',
                valign='middle',
                size_hint_x=width,
                height=30,
                background_color=[0.7, 0.7, 0.7, 1],
                color=[0, 0, 0, 1]
            )
            self.header_grid.add_widget(header_label)

        header_container.add_widget(self.header_grid)


        # 結果表示エリア - スクロール可能なグリッドレイアウト
        scroll_view = ScrollView(size_hint=(1, 0.52))
        # 結果表示用グリッド - ヘッダーと同じパラメータを使用
        self.results_grid = GridLayout(
            cols=7,
            spacing=grid_spacing,
            padding=grid_padding,
            size_hint_y=None
        )

        # グリッドの高さを内容に合わせて調整
        self.results_grid.bind(minimum_height=self.results_grid.setter('height'))

        scroll_view.add_widget(self.results_grid)

        # レイアウトに追加
        main_layout.add_widget(input_layout)
        main_layout.add_widget(filter_layout)
        main_layout.add_widget(analyze_button)
        main_layout.add_widget(header_container)  # BoxLayoutコンテナを追加
        main_layout.add_widget(scroll_view)

        return main_layout

    def create_cell_label(self, text, align='center', row_color=[1, 1, 1, 1]):
        """表のセルとなるラベルを作成"""
        label = BackgroundLabel(
            text=str(text),
            size_hint_y=None,
            height=30,
            halign=align,
            valign='middle',
            text_size=(0, 30),  # 高さのみ指定（幅は自動調整）
            background_color=row_color,
            color=[0, 0, 0, 1]  # テキスト色を黒に設定
        )
        # テキストサイズを設定 - 幅をセルの幅に合わせる
        label.text_size = (label.width, None)
        # サイズが変わったときにテキストサイズを更新
        label.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))

        return label

    def analyze_data(self, instance):
        try:
            # 既存の結果をクリア
            self.results_grid.clear_widgets()

            # 入力値の取得
            win_rate_file = self.file_input.text
            course_filter = self.course_filter.text
            min_race_count = int(self.min_race_count.text)
            max_tanshou_ave = float(self.max_tanshou_ave.text)
            max_fukushou_ave = float(self.max_fukushou_ave.text)

            # データ分析
            results = extract_profitable_win_rate(win_rate_file, course_filter, min_race_count, max_tanshou_ave, max_fukushou_ave)

            # 結果を表形式で表示
            for row_index, result in enumerate(results):
                # 交互に行の色を変える
                row_color = [0.95, 0.95, 0.95, 1] if row_index % 2 == 0 else [1, 1, 1, 1]

                # 各列のデータとその配置
                columns = [
                    (result['騎手名'], 'center'),
                    (result['コース'], 'center'),
                    (result['成績'], 'center'),
                    (result['単勝回収率'], 'center'),
                    (result['複勝回収率'], 'center'),
                    (result['単勝平均'], 'center'),
                    (result['複勝平均'], 'center')
                ]

                # セルを追加
                for (text, align), width in zip(columns, self.col_widths):
                    label = self.create_cell_label(text, align, row_color)
                    label.size_hint_x = width
                    self.results_grid.add_widget(label)

            if not results:
                # 結果がない場合のメッセージ
                empty_label = self.create_cell_label('条件に一致する結果はありませんでした', 'center')
                empty_label.size_hint_x = 1
                self.results_grid.add_widget(empty_label)

        except Exception as e:
            # エラーメッセージ表示
            self.results_grid.clear_widgets()
            error_label = self.create_cell_label(f'エラーが発生しました: {str(e)}', 'center')
            error_label.size_hint_x = 1
            self.results_grid.add_widget(error_label)

if __name__ == '__main__':
    Window.size = (1000, 700)  # ウィンドウサイズを設定
    ProfitableWinRateApp().run()
