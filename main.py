# 에러가 나면 화면에 띄워주는 안전장치 코드
import traceback

try:
    # -----------------------------------------------------------
    # 원래 우리 앱 코드 시작
    # -----------------------------------------------------------
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

    if platform != 'android':
        Window.size = (360, 640)
        try:
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path # download_csv 함수에 필요
        except ImportError:
        # 개발 PC에서는 이 모듈이 없으므로 무시
            Permission = None
            pass

    class NaverNewsApp(MDApp):
        def build(self):
            # 폰트 등록 시도 (여기서 파일 없으면 에러남)
            try:
                LabelBase.register(name="NanumGothic", fn_regular="NanumGothic.ttf")
                LabelBase.register(name="Roboto", fn_regular="NanumGothic.ttf")
                LabelBase.register(name="RobotoBold", fn_regular="NanumGothic.ttf")
                LabelBase.register(name="RobotoThin", fn_regular="NanumGothic.ttf")
                LabelBase.register(name="RobotoMedium", fn_regular="NanumGothic.ttf")
            except Exception as e:
                print(f"폰트 로딩 실패: {e}")
                # 폰트가 없으면 기본 폰트로라도 실행되게 넘어감 (하지만 한글은 깨짐)
                pass

            self.theme_cls.primary_palette = "Blue"
            self.theme_cls.theme_style = "Light"
            
            # 테마 폰트 강제 적용
            for style in self.theme_cls.font_styles:
                self.theme_cls.font_styles[style][0] = "NanumGothic"

            self.news_data = []
            
            screen = MDScreen()
            layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)
            
            self.client_id = MDTextField(hint_text="Client ID", size_hint_y=None, height="40dp", mode="rectangle")
            self.client_secret = MDTextField(hint_text="Client Secret", size_hint_y=None, height="40dp", password=True, mode="rectangle")
            
            search_layout = MDBoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height="65dp")
            self.keyword = MDTextField(hint_text="검색어 입력", size_hint_x=0.7, mode="rectangle")
            search_btn = MDRaisedButton(text="검색", size_hint_x=0.3, on_release=self.search_news)
            
            search_layout.add_widget(self.keyword)
            search_layout.add_widget(search_btn)
            
            scroll = MDScrollView()
            self.result_list = MDList()
            scroll.add_widget(self.result_list)
            
            download_btn = MDRaisedButton(text="CSV 저장", size_hint_y=None, height="50dp", size_hint_x=1, on_release=self.download_csv)

            layout.add_widget(self.client_id)
            layout.add_widget(self.client_secret)
            layout.add_widget(search_layout)
            layout.add_widget(scroll)
            layout.add_widget(download_btn)
            
            screen.add_widget(layout)
            return screen
        
        def on_start(self):
            super().on_start()
        # 앱 시작 후 안드로이드일 경우 권한 요청
            if platform == 'android':
                self._request_android_permissions()

        def _request_android_permissions(self):
        # WRITE_EXTERNAL_STORAGE 권한을 요청합니다.
        # CSV 저장을 위해 외부 저장소 쓰기 권한이 필요합니다.
            permissions_needed = [Permission.WRITE_EXTERNAL_STORAGE]
        
        # 권한 요청 팝업을 띄우고, 결과는 _on_permission_request_result 함수로 받습니다.
            request_permissions(permissions_needed, self._on_permission_request_result)

        def _on_permission_request_result(self, permissions, results):
        # 권한 요청 결과 처리 함수
        # results는 딕셔너리 형태: {Permission.WRITE_EXTERNAL_STORAGE: True/False}
            if results[Permission.WRITE_EXTERNAL_STORAGE]:
                toast("저장소 권한이 승인되었습니다.")
            else:
            # 권한이 거부되면 CSV 저장 불가 안내
                toast("저장소 권한이 거부되어 일부 기능(CSV 저장) 사용에 제한이 있습니다.")

        # ... (기존 함수들 그대로 유지) ...
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

except Exception:
    # -----------------------------------------------------------
    # [비상 사태] 에러 발생 시 빨간 화면에 에러 내용 출력
    # -----------------------------------------------------------
    import traceback
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.scrollview import ScrollView
    
    error_msg = traceback.format_exc()
    
    class ErrorApp(App):
        def build(self):
            # 빨간색 배경의 스크롤 가능한 라벨 생성
            scroll = ScrollView()
            label = Label(
                text=error_msg,
                color=(1, 1, 0, 1), # 노란 글씨
                halign='left',
                valign='top',
                size_hint_y=None
            )
            label.bind(texture_size=label.setter('size'))
            scroll.add_widget(label)
            return scroll
            
    ErrorApp().run()