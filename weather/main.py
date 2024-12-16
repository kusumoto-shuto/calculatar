import flet as ft
import requests
import datetime
import json

# 気象庁のAPIのエンドポイント
AREA_CODE_URL = "http://www.jma.go.jp/bosai/common/const/area.json"
FORECAST_URL = "https://www.jma.go.jp/bosai/forecast/data/forecast/{}.json"

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

def save_debug_data(data, filename="weather_data_debug.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"デバッグ情報をファイル '{filename}' に保存しました。")
    except Exception as e:
        print(f"データ保存中にエラーが発生しました: {e}")

def main(page: ft.Page):
    page.title = "天気予報アプリ"
    page.vertical_alignment = ft.MainAxisAlignment.START

    area_list = get_area_list()
    if not area_list:
        return

    area_options = [
        ft.dropdown.Option(str(code), info["name"])
        for code, info in area_list.get("offices", {}).items()
    ]

    area_dropdown = ft.Dropdown(
        options=area_options,
        label="地域を選択",
        on_change=lambda e: on_area_change(e.control.value)
    )

    weather_text = ft.Column(width=400)

    def display_weather(area_code):
        weather_data = get_weather_forecast(area_code)
        if weather_data and len(weather_data) > 0:
            try:
                weather_text.controls.clear()
                
                # デバッグ用にweather_dataをファイルに保存
                save_debug_data(weather_data)

                dates = weather_data[0]["timeSeries"][0]["timeDefines"]
                weather_info = weather_data[0]["timeSeries"][0]["areas"][0]
                weathers = weather_info["weathers"]
                winds = weather_info["winds"]

                temp_info_section = next((ts for ts in weather_data[0]["timeSeries"] if 'temps' in ts["areas"][0]), None)
                max_temps = min_temps = ["データ未取得"] * len(dates)
                if temp_info_section:
                    temps = temp_info_section["areas"][0]["temps"]
                    max_temps = temps[1::2]
                    min_temps = temps[0::2]

                # 日付の数をチェックしながら天気情報を表示
                for i in range(min(len(dates), 4)):  # 次の日から3日後まで
                    if i < len(dates):
                        date_str = datetime.datetime.fromisoformat(dates[i]).strftime('%Y-%m-%d')
                        weather = weathers[i] if i < len(weathers) else "データ未取得"
                        wind = winds[i] if i < len(winds) else "データ未取得"
                        max_temp = max_temps[i] if i < len(max_temps) else "データ未取得"
                        min_temp = min_temps[i] if i < len(min_temps) else "データ未取得"

                        weather_text.controls.append(ft.Text(
                            f"日付: {date_str}\n"
                            f"天気: {weather}\n"
                            f"風: {wind}\n"
                            f"最高気温: {max_temp}\n"
                            f"最低気温: {min_temp}\n"
                        ))

            except (IndexError, KeyError) as e:
                weather_text.controls.append(ft.Text(f"天気情報の解析中にエラーが発生しました: {e}"))
        else:
            weather_text.controls.append(ft.Text("天気情報が取得できませんでした。"))
        page.update()

    def on_area_change(area_code):
        display_weather(area_code)

    page.add(area_dropdown, weather_text)

ft.app(target=main)