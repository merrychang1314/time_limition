"""
应用启动器
提供友好的启动界面和选项
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_dependencies():
    """检查依赖包"""
    try:
        import kivy
        print(f"✓ Kivy {kivy.__version__}")
        return True
    except ImportError:
        print("错误: 未安装Kivy")
        print("请运行: pip install kivy")
        return False

def install_dependencies():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖包安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖包安装失败")
        return False

def run_app(app_file):
    """运行应用"""
    if not Path(app_file).exists():
        print(f"错误: 找不到应用文件 {app_file}")
        return False
    
    print(f"启动应用: {app_file}")
    try:
        subprocess.run([sys.executable, app_file])
        return True
    except Exception as e:
        print(f"启动应用失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("手机时间限制器 - 启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查依赖
    if not check_dependencies():
        choice = input("是否自动安装依赖包? (y/n): ").strip().lower()
        if choice == 'y':
            if not install_dependencies():
                input("按回车键退出...")
                return
        else:
            print("请手动安装依赖包后重试")
            input("按回车键退出...")
            return
    
    # 选择要运行的版本
    print("\n选择要运行的版本:")
    print("1. 桌面版 (推荐，无需Java环境)")
    print("2. 增强版 (需要完整环境)")
    print("3. 基础版")
    print("4. 构建Android APK")
    print("5. 一键部署")
    print("6. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-6): ").strip()
            
            if choice == '1':
                run_app("phone_time_limiter_fixed.py")
                break
            elif choice == '2':
                run_app("phone_time_limiter_basic_fixed.py")
                break
            elif choice == '3':
                run_app("phone_time_limiter_enhanced.py")
                break
            elif choice == '4':
                run_app("build_android.py")
                break
            elif choice == '5':
                run_app("deploy.py")
                break
            elif choice == '6':
                print("退出启动器")
                break
            else:
                print("无效选择，请输入1-6")
                
        except KeyboardInterrupt:
            print("\n\n已取消")
            break
        except Exception as e:
            print(f"错误: {e}")
            break
    
    input("按回车键退出...")

if __name__ == "__main__":
    main()