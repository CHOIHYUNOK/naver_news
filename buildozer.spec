[app]
# 앱 제목과 패키지 이름
title = NaverNews
package.name = navernews
package.domain = org.test

# 소스 코드 위치 (현재 폴더)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# 버전
version = 0.1

# 필수 라이브러리 (중요!)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,requests,urllib3,chardet,idna,certifi

# 안드로이드 설정
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21

# P4A (Python for Android) 설정
p4a.branch = master
p4a.bootstrap = sdl2
android.accept_sdk_license = True
# [중요] NDK 버전을 25b로 고정 (Kivy 2.2.1과 호환되는 유일한 버전)
android.ndk = 25b
android.api = 33
android.minapi = 21



