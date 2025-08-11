"""
一键部署脚本
自动完成应用的构建、打包和部署
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from datetime import datetime

class DeployManager:
    """部署管理器"""
    
    def __init__(self):
        self.project_dir = Path.cwd()
        self.version = "1.0.0"
        self.app_name = "手机时间限制器"
        self.release_dir = self.project_dir / "release"
        
    def create_release_package(self):
        """创建发布包"""
        print(f"创建 {self.app_name} v{self.version} 发布包...")
        
        # 创建发布目录
        if self.release_dir.exists():
            shutil.rmtree(self.release_dir)
        self.release_dir.mkdir()
        
        # 创建子目录
        (self.release_dir / "source").mkdir()
        (self.release_dir / "android").mkdir()
        (self.release_dir / "docs").mkdir()
        
        # 复制源码文件
        source_files = [
            "phone_time_limiter_enhanced.py",
            "android_permissions.py",
            "requirements.txt",
            "buildozer.spec",
            "create_icon.py"
        ]
        
        for file in source_files:
            if (self.project_dir / file).exists():
                shutil.copy2(self.project_dir / file, self.release_dir / "source" / file)
        
        # 复制文档
        doc_files = ["README.md", "INSTALL.md"]
        for file in doc_files:
            if (self.project_dir / file).exists():
                shutil.copy2(self.project_dir / file, self.release_dir / "docs" / file)
        
        # 复制图标文件
        if (self.project_dir / "icon.png").exists():
            shutil.copy2(self.project_dir / "icon.png", self.release_dir / "android" / "icon.png")
        
        # 创建版本信息文件
        version_info = {
            "app_name": self.app_name,
            "version": self.version,
            "build_date": datetime.now().isoformat(),
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }
        
        with open(self.release_dir / "version.json", "w", encoding="utf-8") as f:
            json.dump(version_info, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 发布包创建完成: {self.release_dir}")
        return True
    
    def build_all_platforms(self):
        """构建所有平台版本"""
        print("开始构建所有平台版本...")
        
        success = True
        
        # 构建Android版本
        try:
            print("\n构建Android APK...")
            from build_android import AndroidBuilder
            
            builder = AndroidBuilder()
            if builder.check_requirements() and builder.prepare_build():
                apk_path = builder.build_debug()
                if apk_path:
                    # 复制APK到发布目录
                    apk_dest = self.release_dir / "android" / f"{self.app_name}_v{self.version}_debug.apk"
                    shutil.copy2(apk_path, apk_dest)
                    print(f"✓ Android APK: {apk_dest}")
                else:
                    print("✗ Android APK构建失败")
                    success = False
            else:
                print("✗ Android构建环境检查失败")
                success = False
                
        except Exception as e:
            print(f"✗ Android构建出错: {e}")
            success = False
        
        return success
    
    def create_installer_scripts(self):
        """创建安装脚本"""
        print("创建安装脚本...")
        
        # Windows批处理安装脚本
        windows_installer = '''@echo off
echo 手机时间限制器 - Windows安装脚本
echo ================================

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo 安装依赖包...
pip install -r source\\requirements.txt

echo 创建桌面快捷方式...
set SCRIPT_DIR=%~dp0
set SHORTCUT_PATH=%USERPROFILE%\\Desktop\\手机时间限制器.bat

echo @echo off > "%SHORTCUT_PATH%"
echo cd /d "%SCRIPT_DIR%source" >> "%SHORTCUT_PATH%"
echo python phone_time_limiter_enhanced.py >> "%SHORTCUT_PATH%"
echo pause >> "%SHORTCUT_PATH%"

echo 安装完成！
echo 可以通过桌面快捷方式启动应用
pause
'''
        
        with open(self.release_dir / "install_windows.bat", "w", encoding="gbk") as f:
            f.write(windows_installer)
        
        # Linux/macOS安装脚本
        unix_installer = '''#!/bin/bash
echo "手机时间限制器 - Unix安装脚本"
echo "================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装"
    exit 1
fi

echo "安装依赖包..."
pip3 install -r source/requirements.txt

echo "创建启动脚本..."
cat > ~/Desktop/手机时间限制器.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")/source"
python3 phone_time_limiter_enhanced.py
EOF

chmod +x ~/Desktop/手机时间限制器.sh

echo "安装完成！"
echo "可以通过桌面的启动脚本运行应用"
'''
        
        with open(self.release_dir / "install_unix.sh", "w", encoding="utf-8") as f:
            f.write(unix_installer)
        
        # 设置执行权限
        try:
            os.chmod(self.release_dir / "install_unix.sh", 0o755)
        except:
            pass
        
        print("✓ 安装脚本创建完成")
        return True
    
    def create_readme(self):
        """创建发布包说明文件"""
        readme_content = f'''# {self.app_name} v{self.version}

## 文件说明

### 目录结构
```
release/
├── source/                 # 源代码文件
│   ├── phone_time_limiter_enhanced.py  # 主程序
│   ├── android_permissions.py          # Android权限管理
│   ├── requirements.txt                # Python依赖
│   └── buildozer.spec                  # Android构建配置
├── android/                # Android版本
│   ├── {self.app_name}_v{self.version}_debug.apk  # 调试版APK
│   └── icon.png                        # 应用图标
├── docs/                   # 文档
│   ├── README.md                       # 项目说明
│   └── INSTALL.md                      # 安装指南
├── install_windows.bat     # Windows安装脚本
├── install_unix.sh         # Linux/macOS安装脚本
└── version.json           # 版本信息
```

## 快速开始

### Android设备
1. 将 `android/{self.app_name}_v{self.version}_debug.apk` 复制到手机
2. 启用"未知来源"安装
3. 安装APK文件
4. 运行应用并授予必要权限

### Windows系统
1. 双击运行 `install_windows.bat`
2. 等待安装完成
3. 使用桌面快捷方式启动应用

### Linux/macOS系统
1. 在终端中运行: `bash install_unix.sh`
2. 等待安装完成
3. 使用桌面启动脚本运行应用

## 详细说明

请查看 `docs/INSTALL.md` 获取完整的安装和使用指南。

## 技术支持

如遇问题，请检查：
1. Python版本是否为3.7+
2. 是否正确安装了所有依赖
3. Android设备是否授予了必要权限

## 版本信息

- 版本: {self.version}
- 构建日期: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- 支持平台: Windows, macOS, Linux, Android

---
{self.app_name} - 帮助您合理控制手机使用时间
'''
        
        with open(self.release_dir / "README.txt", "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        print("✓ 发布包说明文件创建完成")
        return True
    
    def create_archive(self):
        """创建压缩包"""
        print("创建发布压缩包...")
        
        try:
            archive_name = f"{self.app_name}_v{self.version}_{datetime.now().strftime('%Y%m%d')}"
            
            # 创建ZIP压缩包
            shutil.make_archive(
                self.project_dir / archive_name,
                'zip',
                self.release_dir
            )
            
            archive_path = self.project_dir / f"{archive_name}.zip"
            archive_size = archive_path.stat().st_size / 1024 / 1024
            
            print(f"✓ 压缩包创建完成: {archive_path}")
            print(f"  文件大小: {archive_size:.2f} MB")
            
            return str(archive_path)
            
        except Exception as e:
            print(f"✗ 创建压缩包失败: {e}")
            return None
    
    def deploy(self):
        """执行完整部署流程"""
        print("=" * 60)
        print(f"开始部署 {self.app_name} v{self.version}")
        print("=" * 60)
        
        steps = [
            ("创建发布包", self.create_release_package),
            ("构建所有平台", self.build_all_platforms),
            ("创建安装脚本", self.create_installer_scripts),
            ("创建说明文件", self.create_readme),
            ("创建压缩包", self.create_archive)
        ]
        
        for step_name, step_func in steps:
            print(f"\n[{step_name}]")
            try:
                result = step_func()
                if not result:
                    print(f"✗ {step_name}失败")
                    return False
            except Exception as e:
                print(f"✗ {step_name}出错: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 部署完成！")
        print("=" * 60)
        print(f"发布包位置: {self.release_dir}")
        print(f"压缩包位置: {self.project_dir}")
        print("\n可以将压缩包分发给用户使用。")
        
        return True

def main():
    """主函数"""
    try:
        deployer = DeployManager()
        
        print("手机时间限制器 - 一键部署工具")
        print("=" * 40)
        
        choice = input("是否开始部署? (y/n): ").strip().lower()
        if choice != 'y':
            print("部署已取消")
            return
        
        success = deployer.deploy()
        
        if success:
            print("\n部署成功完成！")
        else:
            print("\n部署过程中出现错误，请检查日志")
            
    except KeyboardInterrupt:
        print("\n\n部署已被用户取消")
    except Exception as e:
        print(f"\n部署过程出现未知错误: {e}")

if __name__ == "__main__":
    main()