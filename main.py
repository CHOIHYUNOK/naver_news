from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.toast import toast
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.text import LabelBase

import requests
import csv
import re
import html
import os
from datetime import datetime
import webbrowser
import threading

# 데스크톱 화면 크기 설정
if platform != 'android':
    Window.size = (360, 640)

class NaverNewsApp(MDApp):
    def build(self):
        # =========================================================
        # [핵심] KivyMD 기본 폰트(Roboto)를 나눔고딕으로 바꿔치기
        # =========================================================
        # KivyMD는 내부적으로 'Roboto'라는 이름을 찾는데,
        # 이걸 나눔고딕 파일로 연결해버리면 모든 곳에서 한글이 나옵니다.
        
        # 일반, 굵은 글씨, 얇은 글씨 모두 나눔고딕으로 연결
        LabelBase.register(name="Roboto", fn_regular="NanumGothic.ttf")
        LabelBase.register(name="RobotoBold", fn_regular="NanumGothic.ttf") 
        LabelBase.register(name="RobotoThin", fn_regular="NanumGothic.ttf")
        LabelBase.register(name="RobotoMedium", fn_regular="NanumGothic.ttf")

        # 앱 기본 테마 색상 설정
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        
        # =========================================================

        self.news_data = []
        
        # 화면 구성
        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 1. API 설정
        self.client_id = MDTextField(
            hint_text="Client ID",
            size_hint_y=None, height="40dp",
            mode="rectangle"
        )
        self.client_secret = MDTextField(
            hint_text="Client Secret",
            size_hint_y=None, height="40dp",
            password=True,
            mode="rectangle"
        )
        
        # 2. 검색창
        search_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height="65dp")
        
        self.keyword = MDTextField(
            hint_text="검색어 입력",
            size_hint_x=0.7,
            mode="rectangle"
        )
        
        search_btn = MDRaisedButton(
            text="검색",
            size_hint_x=0.3,
            on_release=self.search_news
        )
        
        search_layout.add_widget(self.keyword)
        search_layout.add_widget(search_btn)
        
        # 3. 결과창
        scroll = MDScrollView()
        self.result_list = MDList()
        scroll.add_widget(self.result_list)
        
        # 4. 저장 버튼
        download_btn = MDRaisedButton(
            text="CSV 저장 (내부 저장소)",
            size_hint_y=None,
            height="50dp",
            size_hint_x=1,
            on_release=self.download_csv
        )

        layout.add_widget(self.client_id)
        layout.add_widget(self.client_secret)
        layout.add_widget(search_layout)
        layout.add_widget(scroll)
        layout.add_widget(download_btn)
        
        screen.add_widget(layout)
        return screen

    def clean_text(self, text):
        text = re.sub('<.*?>', '', text)
        text = html.unescape(text)
        return text

    def format_date(self, date_str):
        try:
            dt = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return date_str

    def search_news(self, instance):
        keyword = self.keyword.text.strip()
        c_id = self.client_id.text.strip()
        c_secret = self.client_secret.text.strip()
        
        if not keyword or not c_id or not c_secret:
            toast("모든 필드를 입력해주세요.")
            return
            
        self.result_list.clear_widgets()
        # 로딩 메시지도 한글로 잘 나올 겁니다.
        self.result_list.add_widget(ThreeLineListItem(text="검색 중...", secondary_text="잠시만 기다려주세요."))
        
        thread = threading.Thread(target=self._fetch_news, args=(keyword, c_id, c_secret))
        thread.daemon = True
        thread.start()

    def _fetch_news(self, keyword, client_id, client_secret):
        url = "https://openapi.naver.com/v1/search/news.json"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        params = {"query": keyword, "display": 20, "sort": "date"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])
            
            self.news_data = []
            for item in items:
                self.news_data.append({
                    "title": self.clean_text(item['title']),
                    "link": item['originallink'] or item['link'],
                    "date": self.format_date(item['pubDate']),
                    "description": self.clean_text(item['description'])
                })
            self.update_ui_success()
        except Exception as e:
            self.update_ui_error(str(e))

    @mainthread
    def update_ui_success(self):
        self.result_list.clear_widgets()
        if not self.news_data:
            toast("검색 결과가 없습니다.")
            return
        for item in self.news_data:
            self.result_list.add_widget(ThreeLineListItem(
                text=item['title'],
                secondary_text=item['date'],
                tertiary_text=item['description'],
                on_release=lambda x, url=item['link']: webbrowser.open(url)
            ))
        toast(f"{len(self.news_data)}개의 뉴스 검색 완료")

    @mainthread
    def update_ui_error(self, error_msg):
        self.result_list.clear_widgets()
        toast(f"오류: {error_msg}")

    def download_csv(self, instance):
        if not self.news_data:
            toast("데이터가 없습니다.")
            return
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            dir_path = primary_external_storage_path() + '/Download'
        else:
            dir_path = os.getcwd()

        filename = f"뉴스검색_{self.keyword.text}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        full_path = os.path.join(dir_path, filename)

        try:
            with open(full_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['제목', '링크', '날짜', '요약'])
                for item in self.news_data:
                    writer.writerow([item['title'], item['link'], item['date'], item['description']])
            toast(f"저장 완료: {filename}")
        except Exception as e:
            toast(f"저장 실패: {e}")

if __name__ == "__main__":
    NaverNewsApp().run()