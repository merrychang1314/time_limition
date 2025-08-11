#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows环境下的Android APK构建脚本
专门用于构建手机时间限制器APK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_environment():
    """检查构建环境"""
    print("检查构建环境...")
    
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要3.7+")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # 检查buildozer模块
    try:
        import buildozer
        print("✅ Buildozer模块已安装")
    except ImportError:
        print("❌ Buildozer模块未安装")
        return False
    
    # 检查kivy
    try:
        import kivy
        print("✅ Kivy已安装")
    except ImportError:
        print("❌ Kivy未安装")
        return False
    
    return True

def prepare_files():
    """准备构建文件"""
    print("\n准备构建文件...")
    
    # 准备main.py
    main_source = None
    if Path('phone_time_limiter_fixed.py').exists():
        main_source = 'phone_time_limiter_fixed.py'
        print("✅ 找到桌面修复版本")
    elif Path('phone_time_limiter_basic_fixed.py').exists():
        main_source = 'phone_time_limiter_basic_fixed.py'
        print("✅ 找到基础修复版本")
    else:
        print("❌ 未找到可用的应用文件")
        return False
    
    # 复制为main.py
    shutil.copy2(main_source, 'main.py')
    print(f"✅ 已将 {main_source} 复制为 main.py")
    
    # 创建buildozer.spec
    create_buildozer_spec()
    
    # 检查图标文件
    if Path('icon.png').exists():
        print("✅ 找到应用图标")
    else:
        print("⚠️  未找到icon.png，将使用默认图标")
    
    if Path('presplash.png').exists():
        print("✅ 找到启动画面")
    else:
        print("⚠️  未找到presplash.png，将使用默认启动画面")
    
    return True

def create_buildozer_spec():
    """创建buildozer.spec配置文件"""
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

def show_manual_instructions():
    """显示手动构建说明"""
    print("\n" + "="*60)
    print("🔧 手动构建APK说明")
    print("="*60)
    print()
    print("由于Windows环境下buildozer可能存在兼容性问题，")
    print("建议您按照以下步骤手动构建APK：")
    print()
    print("1️⃣ 打开新的命令提示符窗口")
    print("2️⃣ 切换到当前目录：")
    print(f"   cd \"{Path.cwd()}\"")
    print()
    print("3️⃣ 执行以下命令初始化buildozer：")
    print("   buildozer init")
    print()
    print("4️⃣ 构建debug APK：")
    print("   buildozer android debug")
    print()
    print("⚠️  注意事项：")
    print("• 首次构建需要下载Android SDK/NDK，可能需要1-2小时")
    print("• 需要稳定的网络连接")
    print("• 构建过程中不要关闭命令窗口")
    print("• 如果遇到错误，请检查网络连接后重试")
    print()
    print("5️⃣ 构建完成后，APK文件位于：")
    print("   ./bin/phonelimiter-1.0-debug.apk")
    print()
    print("6️⃣ 将APK文件传输到Android设备并安装")
    print("   • 需要在设备上允许'未知来源'应用安装")
    print("   • 安装时可能需要授予相关权限")
    print()

def try_auto_build():
    """尝试自动构建"""
    print("\n尝试自动构建APK...")
    print("⚠️  如果卡住或出错，请使用手动构建方式")
    
    try:
        # 尝试初始化buildozer
        print("初始化buildozer...")
        result = subprocess.run(['buildozer', 'init'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"⚠️  初始化警告: {result.stderr}")
        
        # 询问是否继续构建
        print("\n准备开始构建APK...")
        choice = input("是否继续自动构建? (y/n，建议选择n使用手动方式): ").strip().lower()
        
        if choice != 'y':
            print("已取消自动构建")
            return False
        
        # 构建APK
        print("开始构建APK（这可能需要很长时间）...")
        result = subprocess.run(['buildozer', 'android', 'debug'], 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ APK构建成功！")
            
            # 查找APK文件
            bin_dir = Path('./bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"📱 APK文件: {apk_file.absolute()}")
                    
                    # 复制到当前目录
                    new_name = "手机时间限制器.apk"
                    shutil.copy2(apk_file, new_name)
                    print(f"📱 APK已复制到: {Path(new_name).absolute()}")
                    return True
            
            print("⚠️  构建完成但未找到APK文件")
            return False
        else:
            print("❌ APK构建失败")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️  命令执行超时")
        return False
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("手机时间限制器 - Windows APK构建工具")
    print("=" * 60)
    
    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请先安装必要的依赖")
        input("按回车键退出...")
        return False
    
    # 准备文件
    if not prepare_files():
        print("\n❌ 文件准备失败")
        input("按回车键退出...")
        return False
    
    print("\n✅ 环境检查和文件准备完成")
    
    # 显示构建选项
    print("\n请选择构建方式：")
    print("1. 自动构建（可能在Windows上不稳定）")
    print("2. 显示手动构建说明（推荐）")
    print("3. 退出")
    
    while True:
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == '1':
            success = try_auto_build()
            if success:
                print("\n🎉 APK构建成功！")
            else:
                print("\n❌ 自动构建失败，建议使用手动方式")
                show_manual_instructions()
            break
        elif choice == '2':
            show_manual_instructions()
            break
        elif choice == '3':
            print("已退出")
            break
        else:
            print("无效选择，请输入1-3")
    
    input("\n按回车键退出...")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n构建已取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
    finally:
        input("\n按回车键退出...")