#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Android APK构建脚本
专门用于构建手机时间限制器APK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_buildozer():
    """检查buildozer是否安装"""
    try:
        # 在Windows上使用timeout避免卡住
        result = subprocess.run(['buildozer', 'version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Buildozer已安装")
            return True
        else:
            print("❌ Buildozer未正确安装")
            return False
    except FileNotFoundError:
        print("❌ 未找到Buildozer")
        return False
    except subprocess.TimeoutExpired:
        print("⚠️  Buildozer响应超时，但可能已安装")
        # 尝试直接导入buildozer模块
        try:
            import buildozer
            print("✅ Buildozer模块可用")
            return True
        except ImportError:
            print("❌ Buildozer模块不可用")
            return False
    except Exception as e:
        print(f"⚠️  检查Buildozer时出错: {e}")
        # 尝试直接导入buildozer模块
        try:
            import buildozer
            print("✅ Buildozer模块可用")
            return True
        except ImportError:
            print("❌ Buildozer模块不可用")
            return False

def install_buildozer():
    """安装buildozer"""
    print("正在安装Buildozer...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "buildozer", "cython"
        ])
        print("✅ Buildozer安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Buildozer安装失败: {e}")
        return False

def prepare_main_py():
    """准备main.py文件"""
    print("准备main.py文件...")
    
    # 使用修复版本作为main.py
    if Path('phone_time_limiter_fixed.py').exists():
        shutil.copy2('phone_time_limiter_fixed.py', 'main.py')
        print("✅ 使用桌面修复版本作为main.py")
    elif Path('phone_time_limiter_basic_fixed.py').exists():
        shutil.copy2('phone_time_limiter_basic_fixed.py', 'main.py')
        print("✅ 使用基础修复版本作为main.py")
    else:
        print("❌ 未找到可用的应用文件")
        return False
    
    return True

def create_simple_buildozer_spec():
    """创建简化的buildozer.spec"""
    print("创建buildozer.spec配置文件...")
    
    spec_content = '''[app]
title = 手机时间限制器
package.name = phonelimiter
package.domain = com.timelimiter

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = 1.0
requirements = python3,kivy

presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1

[android]
android.permissions = CALL_PHONE,SYSTEM_ALERT_WINDOW,DEVICE_ADMIN,WRITE_SETTINGS
android.api = 30
android.minapi = 21
android.ndk = 23b
android.sdk = 30
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a
'''
    
    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ buildozer.spec创建完成")
    return True

def build_apk():
    """构建APK"""
    print("开始构建APK...")
    print("⚠️  首次构建可能需要很长时间（30分钟到2小时）")
    print("⚠️  需要稳定的网络连接下载Android SDK和NDK")
    
    try:
        # 构建debug APK
        print("执行: buildozer android debug")
        result = subprocess.run(['buildozer', 'android', 'debug'], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ APK构建成功！")
            
            # 查找生成的APK文件
            bin_dir = Path('./bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"📱 APK文件位置: {apk_file.absolute()}")
                    
                    # 复制到当前目录
                    new_name = "手机时间限制器.apk"
                    shutil.copy2(apk_file, new_name)
                    print(f"📱 APK已复制到: {Path(new_name).absolute()}")
                    
                    return True
            
            print("⚠️  APK构建完成但未找到输出文件")
            return False
        else:
            print("❌ APK构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("手机时间限制器 - Android APK构建工具")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要3.7+")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 检查或安装buildozer
    if not check_buildozer():
        print("\n正在安装Buildozer...")
        if not install_buildozer():
            print("❌ 无法安装Buildozer，请手动安装:")
            print("pip install buildozer cython")
            return False
    
    # 准备文件
    if not prepare_main_py():
        return False
    
    if not create_simple_buildozer_spec():
        return False
    
    # 检查图标文件
    if not Path('icon.png').exists():
        print("⚠️  未找到icon.png，将使用默认图标")
    
    if not Path('presplash.png').exists():
        print("⚠️  未找到presplash.png，将使用默认启动画面")
    
    # 构建APK
    print("\n开始构建APK...")
    print("注意：")
    print("1. 首次构建需要下载Android SDK/NDK，可能需要很长时间")
    print("2. 需要稳定的网络连接")
    print("3. 构建过程中请不要关闭终端")
    
    choice = input("\n是否继续构建APK? (y/n): ").strip().lower()
    if choice != 'y':
        print("已取消构建")
        return False
    
    success = build_apk()
    
    if success:
        print("\n🎉 APK构建成功！")
        print("📱 现在可以将APK文件传输到Android设备安装")
        print("⚠️  安装时需要允许'未知来源'应用安装")
    else:
        print("\n❌ APK构建失败")
        print("请检查错误信息并重试")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n构建已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        input("\n按回车键退出...")