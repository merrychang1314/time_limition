#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Android APK构建脚本
专门用于构建手机时间限制器APK
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class APKBuilder:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.app_name = "手机时间限制器"
        self.package_name = "com.timelimiter.app"
        self.version = "1.0.0"
        
    def check_environment(self):
        """检查构建环境"""
        print("检查构建环境...")
        
        # 检查Python
        if sys.version_info < (3, 7):
            print("❌ Python版本过低，需要3.7+")
            return False
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # 检查buildozer
        try:
            result = subprocess.run(['buildozer', 'version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Buildozer已安装")
            else:
                print("❌ Buildozer未正确安装")
                return False
        except FileNotFoundError:
            print("❌ 未找到Buildozer")
            print("请安装: pip install buildozer")
            return False
        
        return True
    
    def install_buildozer(self):
        """安装buildozer"""
        print("正在安装Buildozer...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "buildozer", "cython"
            ])
            print("✅ Buildozer安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Buildozer安装失败: {e}")
            return False
    
    def prepare_main_app(self):
        """准备主应用文件"""
        print("准备主应用文件...")
        
        # 使用修复版本作为主应用
        main_app_content = '''
# -*- coding: utf-8 -*-
"""
手机时间限制器 - Android版本
实现设定时间后只能拨打电话的功能
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.uix.switch import Switch

# Android权限检查
try:
    from android.permissions import request_permissions, Permission
    from android.broadcast import BroadcastReceiver
    from jnius import autoclass, PythonJavaClass, java_method
    ANDROID_AVAILABLE = True
    print("Android环境检测成功")
except ImportError:
    ANDROID_AVAILABLE = False
    print("非Android环境，使用模拟模式")

class SettingsData:
    """设置数据管理类"""
    def __init__(self):
        self.config_file = "limiter_config.json"
        self.default_config = {
            "time_limit_minutes": 30,
            "warning_minutes": 5,
            "password": "1234",
            "auto_start": False,
            "strict_mode": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            print("配置保存成功")
        except Exception as e:
            print(f"保存配置失败: {e}")

class AndroidController:
    """Android系统控制器"""
    def __init__(self):
        self.is_android = ANDROID_AVAILABLE
        if self.is_android:
            self.setup_android_permissions()
    
    def setup_android_permissions(self):
        """设置Android权限"""
        try:
            # 请求必要权限
            permissions = [
                Permission.CALL_PHONE,
                Permission.SYSTEM_ALERT_WINDOW,
                Permission.DEVICE_ADMIN,
                Permission.WRITE_SETTINGS
            ]
            request_permissions(permissions)
            print("Android权限请求完成")
        except Exception as e:
            print(f"权限请求失败: {e}")
    
    def restrict_apps(self, allowed_apps):
        """限制应用访问（Android版本）"""
        if not self.is_android:
            print("模拟模式：限制应用访问")
            return True
        
        try:
            # 在真实Android环境中实现应用限制
            # 这里需要设备管理员权限
            print(f"限制应用，仅允许: {allowed_apps}")
            return True
        except Exception as e:
            print(f"应用限制失败: {e}")
            return False
    
    def allow_calls_only(self):
        """只允许通话功能"""
        if not self.is_android:
            print("模拟模式：启用仅通话模式")
            return True
        
        try:
            # 实现仅通话模式
            allowed_apps = ["com.android.dialer", "com.android.phone"]
            return self.restrict_apps(allowed_apps)
        except Exception as e:
            print(f"仅通话模式设置失败: {e}")
            return False

class PhoneApp:
    """手机应用类"""
    def __init__(self, name, package_name="", is_call_related=False, category="其他"):
        self.name = name
        self.package_name = package_name
        self.is_call_related = is_call_related
        self.category = category

class MainScreen(Screen):
    """主屏幕"""
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.name = 'main'
        
        # 初始化组件
        self.settings = SettingsData()
        self.android_controller = AndroidController()
        
        # 初始化状态
        self.time_limit = self.settings.config["time_limit_minutes"] * 60
        self.time_remaining = self.time_limit
        self.timer_running = False
        self.start_time = None
        self.warning_shown = False
        self.time_up = False
        
        # 创建应用列表
        self.apps = [
            PhoneApp("电话", "com.android.dialer", True, "通讯"),
            PhoneApp("紧急联系", "com.android.phone", True, "通讯"),
            PhoneApp("短信", "com.android.mms", False, "通讯"),
            PhoneApp("微信", "com.tencent.mm", False, "社交"),
            PhoneApp("QQ", "com.tencent.mobileqq", False, "社交"),
            PhoneApp("浏览器", "com.android.browser", False, "工具"),
            PhoneApp("相机", "com.android.camera", False, "媒体"),
            PhoneApp("游戏中心", "com.android.games", False, "娱乐"),
            PhoneApp("音乐", "com.android.music", False, "媒体"),
            PhoneApp("视频", "com.android.video", False, "媒体"),
            PhoneApp("设置", "com.android.settings", False, "系统"),
            PhoneApp("计算器", "com.android.calculator", False, "工具")
        ]
        
        self.build_ui()
        Clock.schedule_interval(self.update_ui, 1)
    
    def build_ui(self):
        """构建用户界面"""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # 设置背景
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            self.rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_rect, pos=self._update_rect)
        
        # 标题栏
        title_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.status_label = Label(
            text="手机使用时间限制器",
            size_hint=(0.8, 1),
            color=(0.2, 0.2, 0.2, 1),
            font_size='18sp'
        )
        title_layout.add_widget(self.status_label)
        
        settings_btn = Button(
            text="设置",
            size_hint=(0.2, 1),
            background_color=(0.3, 0.6, 0.9, 1)
        )
        settings_btn.bind(on_press=self.open_settings)
        title_layout.add_widget(settings_btn)
        
        main_layout.add_widget(title_layout)
        
        # 时间显示
        self.time_label = Label(
            text=f"剩余时间: {self.settings.config['time_limit_minutes']:02d}:00",
            size_hint=(1, 0.1),
            color=(0.1, 0.1, 0.1, 1),
            font_size='24sp'
        )
        main_layout.add_widget(self.time_label)
        
        # 进度条
        self.progress_label = Label(
            text="████████████████████",
            size_hint=(1, 0.05),
            color=(0.2, 0.8, 0.2, 1)
        )
        main_layout.add_widget(self.progress_label)
        
        # 控制按钮
        control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        self.start_button = Button(
            text="开始限时",
            background_color=(0.2, 0.8, 0.3, 1)
        )
        self.start_button.bind(on_press=self.start_timer)
        control_layout.add_widget(self.start_button)
        
        self.pause_button = Button(
            text="暂停",
            background_color=(0.9, 0.6, 0.2, 1),
            disabled=True
        )
        self.pause_button.bind(on_press=self.pause_timer)
        control_layout.add_widget(self.pause_button)
        
        self.reset_button = Button(
            text="重置",
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.reset_button.bind(on_press=self.reset_timer)
        control_layout.add_widget(self.reset_button)
        
        main_layout.add_widget(control_layout)
        
        # 应用网格
        apps_label = Label(
            text="可用应用:",
            size_hint=(1, 0.05),
            color=(0.2, 0.2, 0.2, 1),
            halign='left'
        )
        apps_label.bind(size=apps_label.setter('text_size'))
        main_layout.add_widget(apps_label)
        
        self.app_grid = GridLayout(cols=3, spacing=5, size_hint=(1, 0.6))
        self.update_app_grid()
        main_layout.add_widget(self.app_grid)
        
        self.add_widget(main_layout)
    
    def _update_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def update_app_grid(self):
        """更新应用网格"""
        self.app_grid.clear_widgets()
        
        for app in self.apps:
            if self.time_up and not app.is_call_related:
                continue
                
            app_layout = BoxLayout(orientation='vertical', spacing=2)
            
            app_button = Button(
                text=app.name,
                size_hint=(1, 0.8)
            )
            
            if app.is_call_related:
                app_button.background_color = (0.2, 0.8, 0.2, 1)
            elif self.time_up:
                app_button.background_color = (0.5, 0.5, 0.5, 1)
            else:
                app_button.background_color = (0.4, 0.6, 0.9, 1)
                
            app_button.bind(on_press=lambda btn, app_name=app.name: self.open_app(app_name))
            app_layout.add_widget(app_button)
            
            category_label = Label(
                text=app.category,
                size_hint=(1, 0.2),
                font_size='10sp',
                color=(0.5, 0.5, 0.5, 1)
            )
            app_layout.add_widget(category_label)
            
            self.app_grid.add_widget(app_layout)
    
    def open_app(self, app_name):
        """打开应用"""
        if self.time_up:
            app = next((a for a in self.apps if a.name == app_name), None)
            if app and not app.is_call_related:
                self.show_popup("访问受限", "使用时间已到！\\n只能使用通话相关功能。", show_password=True)
                return
        
        if app_name in ["电话", "紧急联系"]:
            self.show_popup("通话功能", f"正在启动 {app_name}")
        else:
            self.show_popup("应用启动", f"正在打开 {app_name}")
    
    def show_popup(self, title, content, show_password=False):
        """显示弹窗"""
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        content_label = Label(
            text=content,
            text_size=(300, None),
            halign='center',
            valign='middle'
        )
        popup_layout.add_widget(content_label)
        
        if show_password:
            password_input = TextInput(
                hint_text="请输入管理密码",
                password=True,
                size_hint=(1, None),
                height=40,
                multiline=False
            )
            popup_layout.add_widget(password_input)
            
            button_layout = BoxLayout(size_hint=(1, None), height=40, spacing=10)
            
            def check_password(instance):
                if password_input.text == self.settings.config["password"]:
                    popup.dismiss()
                    self.reset_timer(None)
                    self.show_popup("解锁成功", "限制已解除，可以正常使用手机。")
                else:
                    password_input.text = ""
                    content_label.text = content + "\\n\\n密码错误，请重试！"
            
            confirm_btn = Button(text="确认")
            confirm_btn.bind(on_press=check_password)
            button_layout.add_widget(confirm_btn)
            
            cancel_btn = Button(text="取消")
            cancel_btn.bind(on_press=lambda x: popup.dismiss())
            button_layout.add_widget(cancel_btn)
            
            popup_layout.add_widget(button_layout)
        else:
            close_btn = Button(text="确定", size_hint=(1, None), height=40)
            close_btn.bind(on_press=lambda x: popup.dismiss())
            popup_layout.add_widget(close_btn)
        
        popup = Popup(
            title=title,
            content=popup_layout,
            size_hint=(0.9, 0.6)
        )
        popup.open()
    
    def start_timer(self, instance):
        """开始计时"""
        if not self.timer_running:
            self.timer_running = True
            self.start_time = datetime.now()
            self.start_button.text = "运行中"
            self.start_button.disabled = True
            self.pause_button.disabled = False
            self.start_button.background_color = (0.5, 0.5, 0.5, 1)
    
    def pause_timer(self, instance):
        """暂停计时"""
        self.timer_running = False
        self.start_button.text = "继续"
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.start_button.background_color = (0.2, 0.8, 0.3, 1)
    
    def reset_timer(self, instance):
        """重置计时器"""
        self.timer_running = False
        self.time_remaining = self.time_limit
        self.warning_shown = False
        self.time_up = False
        self.start_button.text = "开始限时"
        self.start_button.disabled = False
        self.pause_button.disabled = True
        self.start_button.background_color = (0.2, 0.8, 0.3, 1)
        self.update_app_grid()
        
        # 解除Android限制
        if hasattr(self, 'android_controller'):
            print("解除应用限制")
    
    def update_ui(self, dt):
        """更新UI"""
        if self.timer_running:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.time_remaining = max(0, self.time_limit - elapsed)
            
            warning_threshold = self.settings.config["warning_minutes"] * 60
            if self.time_remaining <= warning_threshold and not self.warning_shown:
                self.warning_shown = True
                self.show_popup("时间警告", f"还剩 {self.settings.config['warning_minutes']} 分钟使用时间！")
            
            if self.time_remaining <= 0 and not self.time_up:
                self.time_up = True
                self.timer_running = False
                
                # 启用Android限制
                if hasattr(self, 'android_controller'):
                    self.android_controller.allow_calls_only()
                
                self.show_popup("时间到", "使用时间已结束！\\n现在只能使用通话功能。", show_password=True)
                self.update_app_grid()
        
        # 更新时间显示
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        self.time_label.text = f"剩余时间: {minutes:02d}:{seconds:02d}"
        
        # 更新进度条
        if self.time_limit > 0:
            progress = self.time_remaining / self.time_limit
            bar_length = 20
            filled = int(progress * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            self.progress_label.text = bar
            
            if progress > 0.5:
                self.progress_label.color = (0.2, 0.8, 0.2, 1)
            elif progress > 0.2:
                self.progress_label.color = (0.9, 0.7, 0.2, 1)
            else:
                self.progress_label.color = (0.9, 0.2, 0.2, 1)
        
        # 更新状态显示
        if self.time_up:
            self.status_label.text = "限制模式 - 仅通话功能"
            self.status_label.color = (0.9, 0.2, 0.2, 1)
        elif self.timer_running:
            self.status_label.text = "计时中..."
            self.status_label.color = (0.2, 0.7, 0.2, 1)
        else:
            self.status_label.text = "手机使用时间限制器"
            self.status_label.color = (0.2, 0.2, 0.2, 1)
    
    def open_settings(self, instance):
        """打开设置界面"""
        self.manager.current = 'settings'

class SettingsScreen(Screen):
    """设置屏幕"""
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.name = 'settings'
        self.settings = SettingsData()
        self.build_ui()
    
    def build_ui(self):
        """构建设置界面"""
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题栏
        title_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        
        back_btn = Button(
            text="← 返回",
            size_hint=(0.2, 1),
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        title_layout.add_widget(back_btn)
        
        title_label = Label(
            text="设置",
            size_hint=(0.6, 1),
            color=(0.2, 0.2, 0.2, 1),
            font_size='20sp'
        )
        title_layout.add_widget(title_label)
        
        save_btn = Button(
            text="保存",
            size_hint=(0.2, 1),
            background_color=(0.2, 0.8, 0.3, 1)
        )
        save_btn.bind(on_press=self.save_settings)
        title_layout.add_widget(save_btn)
        
        main_layout.add_widget(title_layout)
        
        # 设置项
        settings_layout = BoxLayout(orientation='vertical', spacing=20)
        
        # 时间限制设置
        time_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=80)
        time_layout.add_widget(Label(text="使用时间限制 (分钟):", halign='left', size_hint=(1, 0.4)))
        
        self.time_slider = Slider(
            min=5, max=180, value=self.settings.config["time_limit_minutes"],
            step=5, size_hint=(1, 0.6)
        )
        self.time_value_label = Label(
            text=f"{int(self.time_slider.value)} 分钟",
            size_hint=(1, 0.3)
        )
        self.time_slider.bind(value=self.update_time_label)
        
        time_layout.add_widget(self.time_slider)
        time_layout.add_widget(self.time_value_label)
        settings_layout.add_widget(time_layout)
        
        # 警告时间设置
        warning_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=80)
        warning_layout.add_widget(Label(text="提前警告时间 (分钟):", halign='left', size_hint=(1, 0.4)))
        
        self.warning_slider = Slider(
            min=1, max=15, value=self.settings.config["warning_minutes"],
            step=1, size_hint=(1, 0.6)
        )
        self.warning_value_label = Label(
            text=f"{int(self.warning_slider.value)} 分钟",
            size_hint=(1, 0.3)
        )
        self.warning_slider.bind(value=self.update_warning_label)
        
        warning_layout.add_widget(self.warning_slider)
        warning_layout.add_widget(self.warning_value_label)
        settings_layout.add_widget(warning_layout)
        
        # 密码设置
        password_layout = BoxLayout(orientation='vertical', spacing=5, size_hint=(1, None), height=60)
        password_layout.add_widget(Label(text="管理密码:", halign='left', size_hint=(1, 0.4)))
        
        self.password_input = TextInput(
            text=self.settings.config["password"],
            password=True,
            size_hint=(1, 0.6),
            multiline=False
        )
        password_layout.add_widget(self.password_input)
        settings_layout.add_widget(password_layout)
        
        # 开关设置
        switch_layout = BoxLayout(orientation='vertical', spacing=10)
        
        auto_start_layout = BoxLayout(size_hint=(1, None), height=40)
        auto_start_layout.add_widget(Label(text="启动时自动开始计时:", halign='left'))
        self.auto_start_switch = Switch(active=self.settings.config["auto_start"])
        auto_start_layout.add_widget(self.auto_start_switch)
        switch_layout.add_widget(auto_start_layout)
        
        strict_mode_layout = BoxLayout(size_hint=(1, None), height=40)
        strict_mode_layout.add_widget(Label(text="严格模式:", halign='left'))
        self.strict_mode_switch = Switch(active=self.settings.config["strict_mode"])
        strict_mode_layout.add_widget(self.strict_mode_switch)
        switch_layout.add_widget(strict_mode_layout)
        
        settings_layout.add_widget(switch_layout)
        
        main_layout.add_widget(settings_layout)
        self.add_widget(main_layout)
    
    def update_time_label(self, instance, value):
        self.time_value_label.text = f"{int(value)} 分钟"
    
    def update_warning_label(self, instance, value):
        self.warning_value_label.text = f"{int(value)} 分钟"
    
    def save_settings(self, instance):
        """保存设置"""
        self.settings.config["time_limit_minutes"] = int(self.time_slider.value)
        self.settings.config["warning_minutes"] = int(self.warning_slider.value)
        self.settings.config["password"] = self.password_input.text
        self.settings.config["auto_start"] = self.auto_start_switch.active
        self.settings.config["strict_mode"] = self.strict_mode_switch.active
        
        self.settings.save_config()
        
        popup = Popup(
            title="保存成功",
            content=Label(text="设置已保存！"),
            size_hint=(0.7, 0.4)
        )
        popup.open()
        Clock.schedule_once(lambda dt: popup.dismiss(), 2)
    
    def go_back(self, instance):
        self.manager.current = 'main'

class PhoneTimeLimiterApp(App):
    def build(self):
        self.title = "手机时间限制器"
        
        sm = ScreenManager()
        main_screen = MainScreen()
        settings_screen = SettingsScreen()
        
        sm.add_widget(main_screen)
        sm.add_widget(settings_screen)
        
        return sm

if __name__ == '__main__':
    PhoneTimeLimiterApp().run()
'''
        
        # 写入main.py文件
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(main_app_content)
        
        print("✅ 主应用文件准备完成")
        return True
    
    def create_buildozer_spec(self):
        """创建buildozer.spec配置文件"""
        print("创建buildozer配置文件...")
        
        spec_content = f'''[app]
title = {self.app_name}
package.name = timelimiter
package.domain = com.timelimiter

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

version = {self.version}
requirements = python3,kivy,pyjnius,android

[buildozer]
log_level = 2
warn_on_root = 1

[android]
api = 33
minapi = 21
ndk = 25b
sdk = 33
accept_sdk_license = True

permissions = CALL_PHONE,SYSTEM_ALERT_WINDOW,DEVICE_ADMIN,WRITE_SETTINGS,INTERNET,ACCESS_NETWORK_STATE

arch = arm64-v8a,armeabi-v7a

[android.gradle_dependencies]
implementation 'androidx.appcompat:appcompat:1.4.2'

[android.add_permissions]
android.permission.CALL_PHONE = 1
android.permission.SYSTEM_ALERT_WINDOW = 1
android.permission.DEVICE_ADMIN = 1
android.permission.WRITE_SETTINGS = 1

[android.add_src]
java = java

[android.add_aars]

[android.gradle_repositories]
google()
mavenCentral()

[android.add_gradle_repositories]

[android.add_java_dir]
java