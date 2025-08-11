[app]

# (str) 应用标题
title = 手机时间限制器

# (str) 包名
package.name = phonelimiter

# (str) 包域名
package.domain = com.example

# (str) 源码目录
source.dir = .

# (list) 源码包含的文件模式
source.include_exts = py,png,jpg,kv,atlas

# (str) 应用版本
version = 1.0

# (list) 应用需求
requirements = python3,kivy

# (str) 预设
presplashscreen.filename = %(source.dir)s/presplash.png

# (str) 图标
icon.filename = %(source.dir)s/icon.png

# (str) 支持的方向
orientation = portrait

# (bool) 全屏显示
fullscreen = 0

[buildozer]

# (int) 日志级别
log_level = 2

# (int) 显示警告
warn_on_root = 1

[android]

# (list) 权限
android.permissions = CALL_PHONE,SYSTEM_ALERT_WINDOW,DEVICE_ADMIN,WRITE_SETTINGS,MODIFY_PHONE_STATE,ACCESS_NOTIFICATION_POLICY

# (int) API级别
android.api = 30

# (int) 最小API级别
android.minapi = 21

# (str) NDK版本
android.ndk = 23b

# (str) SDK版本
android.sdk = 30

# (bool) 接受SDK许可
android.accept_sdk_license = True

# (str) 架构
android.archs = arm64-v8a, armeabi-v7a

[buildozer:global]

# (str) 构建目录
build_dir = ./.buildozer

# (str) 二进制目录
bin_dir = ./bin