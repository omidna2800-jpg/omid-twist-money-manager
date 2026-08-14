[app]
title = مدیریت سرمایه پیچشی
package.name = omid_twist_money_manager
package.domain = org.omid
version = 1.0.0
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
requirements = python3,kivy==2.2.1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 30
android.minapi = 21
android.archs = armeabi-v7a,arm64-v8a
orientation = portrait
fullscreen = 0
android.package = com.omid.twistmoney

[buildozer]
log_level = 2
warn_on_root = 1
