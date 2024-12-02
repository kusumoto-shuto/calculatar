import flet as ft
import requests

# 気象庁のAPIのエンドポイント
AREA_CODE_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

# 地域リストの取得
def get_area_list():
    try:
        response = requests.get(AREA_CODE_URL)
        response.raise_for_status()  # ステータスコードが200でない場合は例外を発生させる
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
        response.raise_for_status()  # ステータスコードが200でない場合は例外を発生させる
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")
    return None

# Fletアプリケーションの定義
def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.vertical_alignment = "start"
    
    # 地域リスト取得
    area_list = get_area_list()
    if not area_list:
        return
    
    # 地域一覧オプションを作成
    area_options = [
        ft.dropdown.Option(text=info["name"], key=code)
        for code, info in area_list.get("offices", {}).items()
    ]
    
    # ドロップダウンリスト
    area_dropdown = ft.Dropdown(
        options=area_options, 
        label="地域を選択", 
        width=300
    )

    # 天気表示エリア
    weather_text = ft.Text("", size=14, width=400)

    # ドロップダウンリストのイベントハンドラ
    def on_area_change(e):
        area_code = area_dropdown.value
        weather_data = get_weather_forecast(area_code)
        if weather_data:
            forecast_info = weather_data[0]["timeSeries"][0]["areas"][0]
            weather_text.value = (
                f"地域: {forecast_info['area']['name']}\n"
                f"天気: {forecast_info['weathers'][0]}\n"
                f"風: {forecast_info['winds'][0]}"
            )
        else:
            weather_text.value = "天気情報が取得できませんでした。"
        page.update()

    area_dropdown.on_change = on_area_change

    # ページにコンポーネントを追加
    page.add(area_dropdown, weather_text)

# アプリケーションの実行
ft.app(target=main)