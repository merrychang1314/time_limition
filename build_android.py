"""
Android APK构建脚本
使用Buildozer自动构建Android应用
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class AndroidBuilder:
    """Android应用构建器"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.build_dir = self.project_dir / ".buildozer"
        self.bin_dir = self.project_dir / "bin"
        
    def check_requirements(self):
        """检查构建要求"""
        print("检查构建环境...")
        
        # 检查Python
        try:
            python_version = sys.version_info
            if python_version.major < 3 or python_version.minor < 7:
                print("错误: 需要Python 3.7或更高版本")
                return False
            print(f"✓ Python {python_version.major}.{python_version.minor}")
        except Exception as e:
            print(f"错误: 无法检查Python版本 - {e}")
            return False
        
        # 检查Buildozer
        try:
            result = subprocess.run(['buildozer', '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Buildozer已安装")
            else:
                print("错误: Buildozer未正确安装")
                return False
        except FileNotFoundError:
            print("错误: 未找到Buildozer，请先安装")
            print("安装命令: pip install buildozer")
            return False
        
        # 检查必要文件
        required_files = ['buildozer.spec', 'phone_time_limiter_enhanced.py']
        for file in required_files:
            if not (self.project_dir / file).exists():
                print(f"错误: 缺少必要文件 {file}")
                return False
            print(f"✓ {file}")
        
        return True
    
    def prepare_build(self):
        """准备构建环境"""
        print("准备构建环境...")
        
        # 创建必要目录
        self.bin_dir.mkdir(exist_ok=True)
        
        # 复制主程序文件
        main_file = self.project_dir / "main.py"
        if not main_file.exists():
            shutil.copy2("phone_time_limiter_enhanced.py", "main.py")
            print("✓ 创建main.py")
        
        # 检查图标文件
        if not (self.project_dir / "icon.png").exists():
            print("警告: 未找到icon.png，将使用默认图标")
            try:
                subprocess.run([sys.executable, "create_icon.py"], check=True)
                print("✓ 创建应用图标")
            except subprocess.CalledProcessError:
                print("警告: 无法创建图标")
        
        # 更新requirements.txt
        requirements = [
            "kivy>=2.1.0",
            "pyjnius",
            "plyer"
        ]
        
        with open("requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(requirements))
        print("✓ 更新requirements.txt")
        
        return True
    
    def build_debug(self):
        """构建调试版本"""
        print("开始构建调试版本...")
        
        try:
            # 初始化buildozer（如果需要）
            if not self.build_dir.exists():
                print("初始化Buildozer...")
                subprocess.run(['buildozer', 'init'], check=True, cwd=self.project_dir)
            
            # 构建调试APK
            print("构建APK...")
            result = subprocess.run(['buildozer', 'android', 'debug'], 
                                  cwd=self.project_dir, 
                                  capture_output=True, 
                                  text=True)
            
            if result.returncode == 0:
                print("✓ APK构建成功！")
                
                # 查找生成的APK文件
                apk_files = list(self.bin_dir.glob("*.apk"))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"APK文件位置: {apk_file}")
                    print(f"文件大小: {apk_file.stat().st_size / 1024 / 1024:.2f} MB")
                    return str(apk_file)
                else:
                    print("警告: 未找到生成的APK文件")
                    return None
            else:
                print("构建失败:")
                print(result.stdout)
                print(result.stderr)
                return None
                
        except subprocess.CalledProcessError as e:
            print(f"构建过程出错: {e}")
            return None
        except Exception as e:
            print(f"未知错误: {e}")
            return None
    
    def build_release(self):
        """构建发布版本"""
        print("开始构建发布版本...")
        
        try:
            result = subprocess.run(['buildozer', 'android', 'release'], 
                                  cwd=self.project_dir,
                                  capture_output=True,
                                  text=True)
            
            if result.returncode == 0:
                print("✓ 发布版APK构建成功！")
                
                # 查找生成的APK文件
                apk_files = list(self.bin_dir.glob("*-release-unsigned.apk"))
                if apk_files:
                    apk_file = apk_files[0]
                    print(f"发布版APK: {apk_file}")
                    print("注意: 发布版APK需要签名才能安装")
                    return str(apk_file)
                else:
                    print("警告: 未找到生成的发布版APK文件")
                    return None
            else:
                print("发布版构建失败:")
                print(result.stdout)
                print(result.stderr)
                return None
                
        except Exception as e:
            print(f"构建发布版出错: {e}")
            return None
    
    def install_to_device(self, apk_path):
        """安装APK到设备"""
        if not apk_path or not Path(apk_path).exists():
            print("错误: APK文件不存在")
            return False
        
        print("尝试安装到连接的Android设备...")
        
        try:
            # 检查ADB
            result = subprocess.run(['adb', 'devices'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("错误: ADB不可用，请安装Android SDK")
                return False
            
            # 检查连接的设备
            devices = [line for line in result.stdout.split('\n') 
                      if line.strip() and 'device' in line and 'List' not in line]
            
            if not devices:
                print("错误: 未找到连接的Android设备")
                print("请确保:")
                print("1. 设备已连接并启用USB调试")
                print("2. 已安装设备驱动")
                print("3. 已授权计算机调试权限")
                return False
            
            print(f"找到 {len(devices)} 个设备")
            
            # 安装APK
            print(f"安装 {apk_path}...")
            result = subprocess.run(['adb', 'install', '-r', apk_path], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ APK安装成功！")
                print("可以在设备上找到'手机时间限制器'应用")
                return True
            else:
                print("安装失败:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except FileNotFoundError:
            print("错误: 未找到ADB工具")
            print("请安装Android SDK Platform Tools")
            return False
        except Exception as e:
            print(f"安装过程出错: {e}")
            return False
    
    def clean_build(self):
        """清理构建文件"""
        print("清理构建文件...")
        
        try:
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)
                print("✓ 清理.buildozer目录")
            
            if self.bin_dir.exists():
                shutil.rmtree(self.bin_dir)
                print("✓ 清理bin目录")
            
            # 清理临时文件
            temp_files = ['main.py']
            for file in temp_files:
                file_path = self.project_dir / file
                if file_path.exists() and file_path.name != "phone_time_limiter_enhanced.py":
                    file_path.unlink()
                    print(f"✓ 清理 {file}")
            
            print("构建文件清理完成")
            
        except Exception as e:
            print(f"清理过程出错: {e}")

def main():
    """主函数"""
    builder = AndroidBuilder()
    
    print("=" * 50)
    print("手机时间限制器 - Android构建工具")
    print("=" * 50)
    
    # 检查构建要求
    if not builder.check_requirements():
        print("\n构建环境检查失败，请解决上述问题后重试")
        return
    
    # 准备构建
    if not builder.prepare_build():
        print("\n构建准备失败")
        return
    
    print("\n选择构建选项:")
    print("1. 构建调试版APK")
    print("2. 构建发布版APK")
    print("3. 清理构建文件")
    print("4. 退出")
    
    while True:
        try:
            choice = input("\n请选择 (1-4): ").strip()
            
            if choice == '1':
                apk_path = builder.build_debug()
                if apk_path:
                    install_choice = input("\n是否安装到连接的设备? (y/n): ").strip().lower()
                    if install_choice == 'y':
                        builder.install_to_device(apk_path)
                break
                
            elif choice == '2':
                apk_path = builder.build_release()
                if apk_path:
                    print("\n发布版APK构建完成")
                    print("注意: 需要对APK进行签名才能正常安装")
                break
                
            elif choice == '3':
                builder.clean_build()
                break
                
            elif choice == '4':
                print("退出构建工具")
                break
                
            else:
                print("无效选择，请输入1-4")
                
        except KeyboardInterrupt:
            print("\n\n构建已取消")
            break
        except Exception as e:
            print(f"\n错误: {e}")
            break

if __name__ == "__main__":
    main()