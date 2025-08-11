@echo off
chcp 65001 >nul
echo CSV到文本文件转换工具
echo ========================

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未检测到Python，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 正在启动转换工具...
echo 工具将自动查找当前目录中的CSV文件
echo.

REM 直接运行Python脚本，不需要参数
python csv_to_txt_converter.py

echo.
pause