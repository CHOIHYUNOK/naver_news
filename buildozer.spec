[app]
title = NaverNews
package.name = navernews
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# [핵심] openssl 제거, pillow 추가
requirements = python3,kivy==2.2.1,kivymd==1.1.1,pillow,requests,urllib3,chardet,idna,certifi

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

# Python for Android 설정
p4a.bootstrap = sdl2

[buildozer]
log_level = 2

# [핵심] 도커(Root)에서 실행할 때 에러가 나지 않도록 강제 허용
warn_on_root = 0
