@echo off
chcp 65001 >nul
echo ================================================
echo 手机时间限制器 - 一键构建APK
echo ================================================
echo.

echo 正在准备构建环境...
python quick_build.py

echo.
echo 构建完成！请查看生成的APK文件。
echo.
pause