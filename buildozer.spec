[app]
# App Name
title = Advance Tools Pro
package.name = advancetools
package.domain = org.advancetools

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# REQUIREMENTS (SECURE MODE)
# Added 'cython' -> Converts Python to C (Hard to hack)
# Added 'openssl' -> Secure Connection
requirements = python3,kivy==2.2.0,kivymd==1.1.1,requests,beautifulsoup4,plyer,urllib3,idna,chardet,pillow,openssl,cython

version = 3.0.0
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# API Settings
android.api = 33
android.minapi = 21

# SECURITY: Private Storage (Data hidden inside root)
android.private_storage = True

# Entry Point
android.entrypoint = org.kivy.android.PythonActivity

# SECURITY: Disable Backup (Prevents ADB hacking)
android.allow_backup = False

# Architecture (Using armeabi-v7a for stability & compatibility)
android.archs = armeabi-v7a

# Artifacts
android.release_artifact = apk
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
