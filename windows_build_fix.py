#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows系统APK构建修复脚本
"""

import os
import sys
import subprocess
import platform

def main():
    print("=" * 60)
    print("🔧 Windows系统APK构建问题修复")
    print("=" * 60)
    
    # 检查系统
    if platform.system() != "Windows":
        print("❌ 此脚本仅适用于Windows系统")
        return
    
    print("📋 检测到的问题：")
    print("• Buildozer在Windows上不支持Android构建")
    print("• 需要Linux环境来构建Android APK")
    print()
    
    print("💡 推荐解决方案：")
    print()
    
    print("1️⃣ 使用WSL2（最推荐）")
    print("   - 在Windows中运行Linux子系统")
    print("   - 完全兼容buildozer Android构建")
    print("   - 安装命令：wsl --install -d Ubuntu")
    print()
    
    print("2️⃣ 使用Docker")
    print("   - 容器化构建环境")
    print("   - 一次配置，多次使用")
    print()
    
    print("3️⃣ 使用在线构建服务")
    print("   - GitHub Actions")
    print("   - Replit.com")
    print("   - CodeSandbox.io")
    print()
    
    print("4️⃣ 使用虚拟机")
    print("   - VirtualBox + Ubuntu")
    print("   - VMware + Linux")
    print()
    
    # 检查WSL是否可用
    try:
        result = subprocess.run(['wsl', '--list'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ 检测到WSL已安装！")
            print("您可以在WSL中构建APK：")
            print("1. wsl")
            print("2. cd /mnt/c/Users/Administrator/Desktop/LEO\\ AIDE/time_limition/")
            print("3. buildozer android debug")
        else:
            print("⚠️  WSL未安装，建议安装WSL2")
    except:
        print("⚠️  WSL未安装，建议安装WSL2")
    
    print()
    print("🎯 快速解决方案：")
    print("如果您需要立即获得APK文件，建议：")
    print("• 将代码上传到GitHub并使用GitHub Actions构建")
    print("• 使用在线Linux环境（如Replit）构建")
    print("• 寻求有Linux系统的朋友帮助")
    print()
    
    # 创建WSL安装脚本
    wsl_script = """@echo off
echo 正在安装WSL2...
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
echo.
echo 请重启电脑，然后运行：
echo wsl --install -d Ubuntu-20.04
pause
"""
    
    with open("install_wsl.bat", "w", encoding="utf-8") as f:
        f.write(wsl_script)
    
    print("📝 已创建 install_wsl.bat 脚本")
    print("双击运行可自动安装WSL2")
    print()
    
    choice = input("是否现在打开WSL安装指南？(y/n): ").strip().lower()
    if choice == 'y':
        os.system("start https://docs.microsoft.com/zh-cn/windows/wsl/install")
    
    print()
    print("📚 详细解决方案请查看：Windows构建解决方案.md")
    input("按回车键退出...")

if __name__ == "__main__":
    main()