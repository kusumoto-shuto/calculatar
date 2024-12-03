import flet as ft
import requests
import datetime

# 気象庁のAPIのエンドポイント
AREA_CODE_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

# 地域リストの取得
def get_area_list():
    try:
        response = requests.get(AREA_CODE_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

# 天気予報の取得
def get_weather_forecast(area_code):
    try:
        url = FORECAST_URL.format(area_code)
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.vertical_alignment = ft.MainAxisAlignment.START
    
    # 地域リストを取得
    area_list = get_area_list()
    if not area_list:
        return
    
    # 地域一覧オプションを作成
    area_options = [
        ft.dropdown.Option(str(code), info["name"])
        for code, info in area_list.get("offices", {}).items()
    ]

    # ドロップダウンリスト
    area_dropdown = ft.Dropdown(
        options=area_options, 
        label="地域を選択",
        on_change=lambda e: on_area_change(e.control.value)
    )

    # 天気表示エリア
    weather_text = ft.Text("", size=14, width=400)

    # 天気情報を取得してUIに表示する関数
    def display_weather(area_code):
        weather_data = get_weather_forecast(area_code)
        if weather_data and len(weather_data) > 0:
            try:
                # 最初の timeSeries は天気と風の情報を持つ
                weather_info = weather_data[0]["timeSeries"][0]["areas"][0]
                # 時系列2に温度データが含まれている場合
                temp_info_section = [ts for ts in weather_data[0]["timeSeries"] if 'temps' in ts["areas"][0]]
                if temp_info_section:
                    temp_info = temp_info_section[0]["areas"][0]
                    max_temp = temp_info['temps'][1] if len(temp_info['temps']) > 1 else "データ未取得"
                    min_temp = temp_info['temps'][0] if len(temp_info['temps']) > 0 else "データ未取得"
                else:
                    max_temp, min_temp = "データ未取得", "データ未取得"

                # 日付の情報を取得
                report_datetime = weather_data[0]["reportDatetime"]
                date = datetime.datetime.fromisoformat(report_datetime).strftime('%Y-%m-%d')

                # 天気情報のテキスト表示を更新
                weather_text.value = (
                    f"地域: {weather_info['area']['name']}\n"
                    f"日付: {date}\n"
                    f"天気: {weather_info['weathers'][0]}\n"
                    f"風: {weather_info['winds'][0]}\n"
                    f"最高気温: {max_temp}°C\n"
                    f"最低気温: {min_temp}°C\n"
                )
            except (IndexError, KeyError) as e:
                weather_text.value = "天気情報の解析中にエラーが発生しました。"
        else:
            weather_text.value = "天気情報が取得できませんでした。"
        page.update()

    # 地域が変更されたときのイベントハンドラ
    def on_area_change(area_code):
        display_weather(area_code)

    # ページにコンポーネントを追加
    page.add(area_dropdown, weather_text)

# アプリケーションの実行
ft.app(target=main)