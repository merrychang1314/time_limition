"""
Android权限管理模块
用于处理Android系统权限和设备管理功能
"""

try:
    from jnius import autoclass, cast
    from android.permissions import request_permissions, Permission
    from android.broadcast import BroadcastReceiver
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False
    print("Android模块不可用，运行在桌面模式")

class AndroidPermissionManager:
    """Android权限管理器"""
    
    def __init__(self):
        self.permissions_granted = False
        self.device_admin_enabled = False
        
        if ANDROID_AVAILABLE:
            self.setup_android_permissions()
    
    def setup_android_permissions(self):
        """设置Android权限"""
        try:
            # 请求必要权限
            permissions = [
                Permission.CALL_PHONE,
                Permission.SYSTEM_ALERT_WINDOW,
                Permission.WRITE_SETTINGS,
                Permission.MODIFY_PHONE_STATE,
                Permission.ACCESS_NOTIFICATION_POLICY
            ]
            
            request_permissions(permissions)
            self.permissions_granted = True
            print("权限请求已发送")
            
        except Exception as e:
            print(f"权限请求失败: {e}")
    
    def enable_device_admin(self):
        """启用设备管理员权限"""
        if not ANDROID_AVAILABLE:
            return False
            
        try:
            # 获取设备管理员组件
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            ComponentName = autoclass('android.content.ComponentName')
            DevicePolicyManager = autoclass('android.app.admin.DevicePolicyManager')
            
            activity = PythonActivity.mActivity
            
            # 创建设备管理员意图
            intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN)
            component = ComponentName(activity, 'com.example.phonelimiter.DeviceAdminReceiver')
            intent.putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, component)
            intent.putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, "需要设备管理员权限来限制应用使用")
            
            activity.startActivity(intent)
            return True
            
        except Exception as e:
            print(f"启用设备管理员失败: {e}")
            return False
    
    def block_apps(self, app_packages):
        """阻止指定应用运行"""
        if not ANDROID_AVAILABLE:
            print("模拟阻止应用:", app_packages)
            return True
            
        try:
            # 使用设备管理员API阻止应用
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            DevicePolicyManager = autoclass('android.app.admin.DevicePolicyManager')
            
            activity = PythonActivity.mActivity
            dpm = activity.getSystemService('device_policy')
            
            for package in app_packages:
                try:
                    dpm.setApplicationHidden(None, package, True)
                    print(f"已阻止应用: {package}")
                except Exception as e:
                    print(f"阻止应用 {package} 失败: {e}")
            
            return True
            
        except Exception as e:
            print(f"阻止应用失败: {e}")
            return False
    
    def unblock_apps(self, app_packages):
        """解除应用阻止"""
        if not ANDROID_AVAILABLE:
            print("模拟解除应用阻止:", app_packages)
            return True
            
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            DevicePolicyManager = autoclass('android.app.admin.DevicePolicyManager')
            
            activity = PythonActivity.mActivity
            dpm = activity.getSystemService('device_policy')
            
            for package in app_packages:
                try:
                    dpm.setApplicationHidden(None, package, False)
                    print(f"已解除阻止: {package}")
                except Exception as e:
                    print(f"解除阻止 {package} 失败: {e}")
            
            return True
            
        except Exception as e:
            print(f"解除应用阻止失败: {e}")
            return False
    
    def get_installed_apps(self):
        """获取已安装应用列表"""
        if not ANDROID_AVAILABLE:
            # 返回模拟应用列表
            return [
                {"name": "微信", "package": "com.tencent.mm"},
                {"name": "QQ", "package": "com.tencent.mobileqq"},
                {"name": "抖音", "package": "com.ss.android.ugc.aweme"},
                {"name": "淘宝", "package": "com.taobao.taobao"},
                {"name": "支付宝", "package": "com.eg.android.AlipayGphone"},
                {"name": "Chrome", "package": "com.android.chrome"},
                {"name": "游戏中心", "package": "com.android.game"}
            ]
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            PackageManager = autoclass('android.content.pm.PackageManager')
            
            activity = PythonActivity.mActivity
            pm = activity.getPackageManager()
            
            # 获取所有已安装应用
            packages = pm.getInstalledPackages(PackageManager.GET_META_DATA)
            apps = []
            
            for package in packages:
                app_info = {
                    "name": str(package.applicationInfo.loadLabel(pm)),
                    "package": str(package.packageName)
                }
                apps.append(app_info)
            
            return apps
            
        except Exception as e:
            print(f"获取应用列表失败: {e}")
            return []

class PhoneCallManager:
    """电话功能管理器"""
    
    def __init__(self):
        self.call_allowed = True
    
    def make_call(self, phone_number):
        """拨打电话"""
        if not ANDROID_AVAILABLE:
            print(f"模拟拨打电话: {phone_number}")
            return True
        
        try:
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            activity = PythonActivity.mActivity
            
            # 创建拨号意图
            intent = Intent(Intent.ACTION_CALL)
            intent.setData(Uri.parse(f"tel:{phone_number}"))
            
            activity.startActivity(intent)
            return True
            
        except Exception as e:
            print(f"拨打电话失败: {e}")
            return False
    
    def get_emergency_numbers(self):
        """获取紧急联系人号码"""
        return [
            {"name": "报警", "number": "110"},
            {"name": "火警", "number": "119"},
            {"name": "急救", "number": "120"},
            {"name": "交通事故", "number": "122"}
        ]

# 设备管理员接收器（需要在Java中实现）
DEVICE_ADMIN_RECEIVER_JAVA = '''
package com.example.phonelimiter;

import android.app.admin.DeviceAdminReceiver;
import android.content.Context;
import android.content.Intent;
import android.widget.Toast;

public class DeviceAdminReceiver extends DeviceAdminReceiver {
    
    @Override
    public void onEnabled(Context context, Intent intent) {
        super.onEnabled(context, intent);
        Toast.makeText(context, "设备管理员已启用", Toast.LENGTH_SHORT).show();
    }
    
    @Override
    public void onDisabled(Context context, Intent intent) {
        super.onDisabled(context, intent);
        Toast.makeText(context, "设备管理员已禁用", Toast.LENGTH_SHORT).show();
    }
}
'''

# Android清单文件权限配置
ANDROID_MANIFEST_PERMISSIONS = '''
<!-- 电话权限 -->
<uses-permission android:name="android.permission.CALL_PHONE" />
<uses-permission android:name="android.permission.READ_PHONE_STATE" />
<uses-permission android:name="android.permission.MODIFY_PHONE_STATE" />

<!-- 系统权限 -->
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
<uses-permission android:name="android.permission.WRITE_SETTINGS" />
<uses-permission android:name="android.permission.ACCESS_NOTIFICATION_POLICY" />

<!-- 设备管理员权限 -->
<uses-permission android:name="android.permission.BIND_DEVICE_ADMIN" />

<!-- 应用管理权限 -->
<uses-permission android:name="android.permission.PACKAGE_USAGE_STATS" />
<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />

<!-- 设备管理员接收器 -->
<receiver android:name=".DeviceAdminReceiver"
    android:permission="android.permission.BIND_DEVICE_ADMIN">
    <meta-data android:name="android.app.device_admin"
        android:resource="@xml/device_admin" />
    <intent-filter>
        <action android:name="android.app.action.DEVICE_ADMIN_ENABLED" />
    </intent-filter>
</receiver>
'''