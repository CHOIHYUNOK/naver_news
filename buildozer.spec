[app]
# 앱 기본 정보
title = NaverNews
package.name = navernews
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# 버전
version = 0.1

# [핵심] 필수 라이브러리 (openssl, pillow 제거하여 충돌 방지)
requirements = python3,kivy==2.2.1,kivymd==1.1.1,requests,urllib3,chardet,idna,certifi

# 화면 설정
orientation = portrait
fullscreen = 0
android.presplash_color = #FFFFFF

# [핵심] 안드로이드 권한
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# [핵심] 안드로이드 API 및 NDK 설정 (Kivy 2.2.1 호환 버전 고정)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

# Python for Android 설정
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
