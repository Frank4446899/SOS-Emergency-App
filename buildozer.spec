
[app]
title = SOS Emergency
package.name = sos
package.domain = org.frank
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,mp4,wav,m4a,json
version = 0.1
requirements = python3,kivy,requests,certifi,pyjnius
orientation = portrait
fullscreen = 0

android.permissions = CAMERA, RECORD_AUDIO, INTERNET, ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True

[buildozer]
log_level = 2
warn_on_root = 0
