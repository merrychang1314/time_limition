# 🔧 Windows系统APK构建解决方案

## ❌ 问题分析
您遇到的错误 "Unknown command/target android" 是因为：
- Buildozer在Windows上对Android构建支持有限
- 需要Linux环境或WSL来正常构建Android APK

## ✅ 解决方案

### 方案1：使用WSL2（推荐）

#### 1. 安装WSL2
```powershell
# 在PowerShell管理员模式下运行
wsl --install -d Ubuntu
```

#### 2. 在WSL2中安装依赖
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python和依赖
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y build-essential git unzip

# 安装Java
sudo apt install -y openjdk-11-jdk

# 安装Android构建依赖
sudo apt install -y autoconf automake libtool pkg-config
sudo apt install -y zlib1g-dev libncurses5-dev libncursesw5-dev
sudo apt install -y libtinfo5 cmake libffi-dev libssl-dev

# 安装Python包
pip3 install buildozer cython kivy
```

#### 3. 在WSL2中构建APK
```bash
# 复制项目文件到WSL2
cp /mnt/c/Users/Administrator/Desktop/LEO\ AIDE/time_limition/* ./

# 构建APK
buildozer android debug
```

### 方案2：使用Docker（简单）

#### 1. 创建Docker构建脚本
```dockerfile
# 创建 Dockerfile
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip git unzip \
    openjdk-11-jdk build-essential \
    autoconf automake libtool pkg-config \
    zlib1g-dev libncurses5-dev cmake \
    libffi-dev libssl-dev

RUN pip3 install buildozer cython kivy

WORKDIR /app
COPY . .

CMD ["buildozer", "android", "debug"]
```

#### 2. 构建Docker镜像并运行
```bash
docker build -t phone-limiter-builder .
docker run -v $(pwd):/app phone-limiter-builder
```

### 方案3：在线构建服务

#### 使用GitHub Actions
创建 `.github/workflows/build.yml`：
```yaml
name: Build APK
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install buildozer cython kivy
    - name: Build APK
      run: buildozer android debug
    - name: Upload APK
      uses: actions/upload-artifact@v2
      with:
        name: apk
        path: bin/*.apk
```

### 方案4：使用云端构建平台

#### Replit构建
1. 访问 replit.com
2. 创建新的Python项目
3. 上传您的代码文件
4. 安装buildozer并构建

#### CodeSandbox构建
1. 访问 codesandbox.io
2. 选择Python模板
3. 上传代码并构建

## 🚀 推荐流程（WSL2方案）

### 1. 快速设置WSL2
```powershell
# 1. 启用WSL功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 2. 重启电脑后安装Ubuntu
wsl --install -d Ubuntu-20.04
```

### 2. 一键安装脚本
创建 `setup_wsl.sh`：
```bash
#!/bin/bash
echo "🔧 设置Android构建环境..."

# 更新系统
sudo apt update -y

# 安装基础依赖
sudo apt install -y python3 python3-pip git unzip openjdk-11-jdk
sudo apt install -y build-essential autoconf automake libtool pkg-config
sudo apt install -y zlib1g-dev libncurses5-dev cmake libffi-dev libssl-dev

# 安装Python包
pip3 install --user buildozer cython kivy

echo "✅ 环境设置完成！"
echo "现在可以运行: buildozer android debug"
```

### 3. 构建APK
```bash
# 在WSL2中
cd /mnt/c/Users/Administrator/Desktop/LEO\ AIDE/time_limition/
buildozer android debug
```

## 📱 临时解决方案

如果您急需APK文件，我建议：

1. **使用在线构建服务**：
   - 上传代码到GitHub
   - 使用GitHub Actions自动构建
   - 下载生成的APK

2. **寻求帮助**：
   - 找有Linux系统的朋友帮忙构建
   - 使用云服务器临时构建

3. **虚拟机方案**：
   - 安装VirtualBox + Ubuntu
   - 在虚拟机中构建APK

## 🎯 最终建议

**最推荐WSL2方案**，因为：
- ✅ 完全兼容Linux构建环境
- ✅ 可以直接访问Windows文件
- ✅ 性能接近原生Linux
- ✅ 一次设置，长期使用

设置完WSL2后，您就可以正常使用buildozer构建Android APK了！