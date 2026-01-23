[app]

# (str) Title of your application
title = Advance Tools Pro

# (str) Package name
package.name = advancetools

# (str) Package domain (needed for android/ios packaging)
package.domain = org.advancetools

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# FIXED: Added 'txt' so your text files are included
source.include_exts = py,png,jpg,kv,atlas,txt

# (str) Application versioning (method 1)
version = 3.5.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
# FIXED: Added 'charset-normalizer' (Crucial for requests) & 'pyjnius'
requirements = python3,kivy==2.2.0,kivymd==1.1.1,requests,beautifulsoup4,soupsieve,plyer,urllib3,idna,chardet,charset-normalizer,pillow,openssl,certifi,pyjnius

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# FIXED: Added ACCESS_NETWORK_STATE to prevent network crashes
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 19b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (list) Ouput artifacts to generate
android.release_artifact = apk
android.debug_artifact = apk

# (list) Android architectures to build for, based on python-for-android options
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (Android API >= 23)
android.allow_backup = False

# (str) python-for-android branch to use, defaults to master
#p4a.branch = master

# (bool) Enable AndroidX support. Enable when 'android.api' >= 28.
# CRITICAL FIX: This MUST be True for API 33 + KivyMD to work
android.enable_androidx = True

# (list) Gradle dependencies to add
# Sometimes helpful for KivyMD styling
# android.gradle_dependencies = com.google.android.material:material:1.8.0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
