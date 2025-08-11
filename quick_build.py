#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速APK构建脚本 - 直接使用buildozer命令
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("=" * 50)
    print("手机时间限制器 - 快速APK构建")
    print("=" * 50)
    
    # 准备main.py文件
    print("准备应用文件...")
    
    if Path('phone_time_limiter_basic_fixed.py').exists():
        shutil.copy2('phone_time_limiter_basic_fixed.py', 'main.py')
        print("✅ 使用基础修复版本")
    elif Path('phone_time_limiter_fixed.py').exists():
        shutil.copy2('phone_time_limiter_fixed.py', 'main.py')
        print("✅ 使用桌面修复版本")
    else:
        print("❌ 未找到应用文件")
        return
    
    # 创建简化的buildozer.spec
    print("创建buildozer配置...")
    
    spec_content = '''[app]
title = 手机时间限制器
package.name = phonelimiter
package.domain = com.timelimiter
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
requirements = python3,kivy
orientation = portrait

[buildozer]
log_level = 2

[android]
android.permissions = CALL_PHONE
android.api = 30
android.minapi = 21
android.archs = arm64-v8a
'''
    
    with open('buildozer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 配置文件创建完成")
    
    # 显示构建命令
    print("\n" + "=" * 50)
    print("📱 APK构建说明")
    print("=" * 50)
    print()
    print("现在请在命令行中执行以下步骤：")
    print()
    print("1️⃣ 初始化buildozer（如果是第一次）：")
    print("   buildozer init")
    print()
    print("2️⃣ 构建APK：")
    print("   buildozer android debug")
    print()
    print("⚠️  重要提示：")
    print("• 首次构建需要下载Android SDK/NDK，可能需要1-2小时")
    print("• 需要稳定的网络连接")
    print("• 构建完成后APK文件在 bin/ 目录下")
    print()
    print("3️⃣ 如果构建成功，APK文件路径：")
    print("   ./bin/phonelimiter-1.0-debug.apk")
    print()
    print("4️⃣ 将APK传输到Android设备并安装")
    print()
    
    # 询问是否自动执行
    choice = input("是否现在自动执行构建命令? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n开始自动构建...")
        print("⚠️  如果卡住，请按Ctrl+C取消，然后手动执行上述命令")
        
        try:
            # 执行buildozer命令
            os.system('buildozer android debug')
            
            # 检查是否生成了APK
            bin_dir = Path('./bin')
            if bin_dir.exists():
                apk_files = list(bin_dir.glob('*.apk'))
                if apk_files:
                    print(f"\n🎉 APK构建成功！")
                    print(f"📱 APK文件: {apk_files[0].absolute()}")
                    
                    # 复制到当前目录
                    new_name = "手机时间限制器.apk"
                    shutil.copy2(apk_files[0], new_name)
                    print(f"📱 APK已复制到: {Path(new_name).absolute()}")
                else:
                    print("\n⚠️  构建完成但未找到APK文件")
            else:
                print("\n⚠️  未找到bin目录")
                
        except KeyboardInterrupt:
            print("\n\n构建已取消")
        except Exception as e:
            print(f"\n❌ 构建出错: {e}")
    else:
        print("\n请手动执行上述命令进行构建")
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()