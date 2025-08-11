@echo off
chcp 65001 >nul
title Leo's Studio - CSV转TXT GUI工具

echo.
echo ===============================================
echo           💖 Leo's Studio 💖
echo        CSV转TXT图形界面工具
echo ===============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未检测到Python
    echo 请先安装Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python环境检测正常
echo 🚀 正在启动GUI界面...
echo.

REM 启动GUI程序
python csv_to_txt_gui.py

REM 如果程序异常退出，显示错误信息
if errorlevel 1 (
    echo.
    echo ❌ 程序运行出现错误
    echo 请检查Python环境和依赖库
    echo.
    pause
)