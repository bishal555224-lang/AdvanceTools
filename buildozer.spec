[app]
title = Advance Tools Pro
package.name = advancetools
package.domain = org.advancetools

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 3.0.0

# REQUIREMENTS:
# Added pillow back as GitHub Actions can handle it
# Cython is handled in main.yml for security
requirements = python3,kivy==2.2.0,kivymd==1.1.1,requests,beautifulsoup4,plyer,urllib3,idna,chardet,pillow

orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.private_storage = True
android.entrypoint = org.kivy.android.PythonActivity

# THE FIX IS HERE:
# Added 'arm64-v8a' alongside 'armeabi-v7a'
# This ensures it installs on ALL modern Android phones
android.archs = arm64-v8a, armeabi-v7a

# Security
android.allow_backup = False

android.release_artifact = apk
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
