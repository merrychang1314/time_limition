import time
import threading
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

class PhoneApp:
    """模拟手机应用的类"""
    def __init__(self, name, icon="phone.png", is_call_related=False):
        self.name = name
        self.icon = icon
        self.is_call_related = is_call_related  # 标记是否为通话相关应用

class PhoneTimeLimiter(BoxLayout):
    def __init__(self, **kwargs):
        super(PhoneTimeLimiter, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # 设置背景颜色
        with self.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # 浅灰色背景
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)
        
        # 初始化应用状态
        self.time_limit = 30 * 60  # 30分钟，以秒为单位
        self.time_remaining = self.time_limit
        self.timer_running = False
        self.timer_thread = None
        self.start_time = None
        self.warning_shown = False
        self.time_up = False
        
        # 创建应用列表
        self.apps = [
            PhoneApp("电话", icon="phone.png", is_call_related=True),
            PhoneApp("短信", icon="sms.png"),
            PhoneApp("微信", icon="wechat.png"),
            PhoneApp("浏览器", icon="browser.png"),
            PhoneApp("相机", icon="camera.png"),
            PhoneApp("游戏", icon="game.png"),
            PhoneApp("音乐", icon="music.png"),
            PhoneApp("视频", icon="video.png"),
            PhoneApp("设置", icon="settings.png")
        ]
        
        # 创建UI组件
        self.status_label = Label(
            text="手机使用时间限制: 30分钟",
            size_hint=(1, 0.1),
            color=(0, 0, 0, 1)  # 黑色文字
        )
        self.add_widget(self.status_label)
        
        self.time_label = Label(
            text="剩余时间: 30:00",
            size_hint=(1, 0.1),
            color=(0, 0, 0, 1)
        )
        self.add_widget(self.time_label)
        
        # 控制按钮
        control_layout = BoxLayout(size_hint=(1, 0.1), spacing=10, padding=10)
        
        self.start_button = Button(
            text="开始计时",
            background_color=(0.2, 0.7, 0.3, 1)  # 绿色
        )
        self.start_button.bind(on_press=self.start_timer)
        control_layout.add_widget(self.start_button)
        
        self.reset_button = Button(
            text="重置",
            background_color=(0.7, 0.2, 0.2, 1)  # 红色
        )
        self.reset_button.bind(on_press=self.reset_timer)
        control_layout.add_widget(self.reset_button)
        
        self.add_widget(control_layout)
        
        # 应用网格
        self.app_grid = GridLayout(cols=3, spacing=10, padding=10, size_hint=(1, 0.7))
        self.update_app_grid()
        self.add_widget(self.app_grid)
        
        # 设置定时器更新UI
        Clock.schedule_interval(self.update_ui, 1)
    
    def _update_rect(self, instance, value):
        """更新背景矩形大小"""
        self.rect.size = instance.size
        self.rect.pos = instance.pos
    
    def update_app_grid(self):
        """更新应用网格"""
        self.app_grid.clear_widgets()
        for app in self.apps:
            # 检查是否应该显示此应用
            if self.time_up and not app.is_call_related:
                # 时间到，只显示通话相关应用
                continue
                
            app_button = Button(text=app.name)
            app_button.background_normal = ''
            
            # 设置不同的背景颜色
            if app.is_call_related:
                app_button.background_color = (0.2, 0.6, 0.8, 1)  # 蓝色
            else:
                app_button.background_color = (0.5, 0.5, 0.5, 1)  # 灰色
                
            app_button.bind(on_press=lambda btn, app_name=app.name: self.open_app(app_name))
            self.app_grid.add_widget(app_button)
    
    def open_app(self, app_name):
        """打开应用"""
        if self.time_up:
            # 检查是否为通话相关应用
            app = next((a for a in self.apps if a.name == app_name), None)
            if app and not app.is_call_related:
                self.show_popup("使用时间已到", "只能使用通话功能！")
                return
        
        self.show_popup("打开应用", f"正在打开 {app_name}")
    
    def show_popup(self, title, content):
        """显示弹窗"""
        popup = Popup(
            title=title,
            content=Label(text=content),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def start_timer(self, instance):
        """开始计时"""
        if not self.timer_running:
            self.timer_running = True
            self.start_time = datetime.now()
            self.start_button.text = "暂停"
            self.start_button.background_color = (0.8, 0.8, 0.2, 1)  # 黄色
        else:
            self.timer_running = False
            self.start_button.text = "继续"
            self.start_button.background_color = (0.2, 0.7, 0.3, 1)  # 绿色
    
    def reset_timer(self, instance):
        """重置计时器"""
        self.timer_running = False
        self.time_remaining = self.time_limit
        self.warning_shown = False
        self.time_up = False
        self.start_button.text = "开始计时"
        self.start_button.background_color = (0.2, 0.7, 0.3, 1)  # 绿色
        self.update_app_grid()
    
    def update_ui(self, dt):
        """更新UI"""
        if self.timer_running:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            self.time_remaining = max(0, self.time_limit - elapsed)
            
            # 检查是否需要显示警告（25分钟）
            warning_threshold = 5 * 60  # 5分钟 = 300秒
            if self.time_remaining <= warning_threshold and not self.warning_shown:
                self.warning_shown = True
                self.show_popup("时间警告", "还剩5分钟使用时间！")
            
            # 检查时间是否用完
            if self.time_remaining <= 0 and not self.time_up:
                self.time_up = True
                self.timer_running = False
                self.show_popup("时间到", "使用时间已结束，只能使用通话功能！")
                self.update_app_grid()
        
        # 更新时间显示
        minutes = int(self.time_remaining // 60)
        seconds = int(self.time_remaining % 60)
        self.time_label.text = f"剩余时间: {minutes:02d}:{seconds:02d}"
        
        # 更新状态显示
        if self.time_up:
            self.status_label.text = "使用时间已结束，只能使用通话功能"
            self.status_label.color = (1, 0, 0, 1)  # 红色
        elif self.timer_running:
            self.status_label.text = "计时中..."
            self.status_label.color = (0, 0.7, 0, 1)  # 绿色
        else:
            self.status_label.text = "手机使用时间限制: 30分钟"
            self.status_label.color = (0, 0, 0, 1)  # 黑色

class PhoneTimeLimiterApp(App):
    def build(self):
        return PhoneTimeLimiter()

if __name__ == '__main__':
    PhoneTimeLimiterApp().run()