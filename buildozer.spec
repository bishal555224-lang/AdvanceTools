[app]
title = Advance Tools
package.name = advancetools
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 3.0.0
requirements = python3,kivy==2.2.0,kivymd==1.1.1,requests,beautifulsoup4,plyer,urllib3,idna,chardet,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity
android.archs = armeabi-v7a
android.allow_backup = False
p4a.branch = release-2022.12.20
android.release_artifact = apk
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
