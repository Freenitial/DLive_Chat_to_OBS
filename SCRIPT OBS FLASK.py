import subprocess
import sys
import configparser
import os
import re
import time
from datetime import datetime, timedelta
from threading import Thread
import random
import tkinter as tk
from tkinter import ttk

retry = 0

def install_required_packages():
    try:
        print("Attempting to install/upgrade packages...")
        command = [sys.executable, '-m', 'pip', 'install', '--upgrade',
                   'selenium', 'obs-websocket-py', 'flask', 'flask-cors', 
                   'flask-socketio', 'pillow', 'requests', 'colorama', 'CairoSVG']
        subprocess.check_call(['runas', '/user:Administrator'] + command)
        print("All packages installed/upgraded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to install packages: {e}")

def try_import():
    global retry
    if retry > 1 : 
        print("\n\n   Wrong PIP environnment.\n")
        time.sleep(4)
        sys.exit()
    try:
        from flask import Flask, request, send_from_directory, jsonify, render_template
        from flask_cors import CORS
        from flask_socketio import SocketIO
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from obswebsocket import obsws, requests as obs_request
        from obswebsocket.exceptions import ConnectionFailure
        from PIL import Image, ImageTk, ImageFilter
        from io import BytesIO
        import colorama
        from colorama import Fore, Style
        import requests
        import cairosvg
        print("All modules imported successfully.")
    except ImportError as e:
        retry += 1
        print(f"ImportError occurred: {e}")
        print("Attempting to install the required packages...")
        install_required_packages()
        # Retry imports after installation
        try_import()

# Initial attempt to import
try_import()
#from bs4 import BeautifulSoup


from flask import Flask, request, send_from_directory, jsonify, render_template
from flask_cors import CORS
from flask_socketio import SocketIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from obswebsocket import obsws, requests as obs_request
from obswebsocket.exceptions import ConnectionFailure
from PIL import Image, ImageTk, ImageFilter
from io import BytesIO
import colorama
from colorama import Fore, Style
import requests
import cairosvg


local_app_data = os.environ.get("LOCALAPPDATA")
settings_ini_path = os.path.join(local_app_data, 'OBS_module_chat', 'config.ini')

colorama.init()




OBS_HOST, OBS_PORT, OBS_PASSWORD = None, None, None
FLASK_PORT, CHAT_URL = None, None
SHOW_AVATAR, SHOW_BADGES, DEBUG = None, None, None


default_values = {
    'OBS': {'HOST': 'localhost', 'PORT': str(random.randint(1024, 65535)), 'PASSWORD': ''},
    'FLASK': {'PORT': str(random.randint(5000, 8100))},
    'CHAT': {'URL': 'https://dlive.tv/c/COMPLETE_HERE/COMPLETE+HERE'},
    'DISPLAY': {'SHOW_AVATAR': 'True', 'SHOW_BADGES': 'True'},
    'MISC': {'DEBUG': 'False'}
}

def create_default_config():
    config = configparser.ConfigParser()
    for section, values in default_values.items():
        config[section] = values
    with open(settings_ini_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
    print(f"Default config created at {settings_ini_path}")

def read_config():
    global OBS_HOST, OBS_PORT, OBS_PASSWORD, FLASK_PORT, CHAT_URL, SHOW_AVATAR, SHOW_BADGES, DEBUG
    config = configparser.ConfigParser()
    config.read(settings_ini_path, encoding='utf-8')
    
    missing_values = False

    OBS_HOST = config.get('OBS', 'HOST', fallback=None)
    OBS_PORT = config.getint('OBS', 'PORT', fallback=None)
    OBS_PASSWORD = config.get('OBS', 'PASSWORD', fallback=None)
    FLASK_PORT = config.getint('FLASK', 'PORT', fallback=None)
    CHAT_URL = config.get('CHAT', 'URL', fallback=None)
    SHOW_AVATAR = config.getboolean('DISPLAY', 'SHOW_AVATAR', fallback=None)
    SHOW_BADGES = config.getboolean('DISPLAY', 'SHOW_BADGES', fallback=None)
    DEBUG = config.getboolean('MISC', 'DEBUG', fallback=None)

    if OBS_HOST is None:
        OBS_HOST = default_values['OBS']['HOST']
        missing_values = True
    if OBS_PORT is None:
        OBS_PORT = int(default_values['OBS']['PORT'])
        missing_values = True
    if OBS_PASSWORD is None:
        OBS_PASSWORD = default_values['OBS']['PASSWORD']
        missing_values = True
    if FLASK_PORT is None:
        FLASK_PORT = int(default_values['FLASK']['PORT'])
        missing_values = True
    if CHAT_URL is None:
        CHAT_URL = default_values['CHAT']['URL']
        missing_values = True
    if SHOW_AVATAR is None:
        SHOW_AVATAR = default_values['DISPLAY']['SHOW_AVATAR'] == 'True'
        missing_values = True
    if SHOW_BADGES is None:
        SHOW_BADGES = default_values['DISPLAY']['SHOW_BADGES'] == 'True'
        missing_values = True
    if DEBUG is None:
        DEBUG = default_values['MISC']['DEBUG'] == 'False'
        missing_values = True

    print(f"OBS_HOST: {OBS_HOST}, OBS_PORT: {OBS_PORT}, OBS_PASSWORD: {OBS_PASSWORD}, FLASK_PORT: {FLASK_PORT}, CHAT_URL: {CHAT_URL}, SHOW_AVATAR: {SHOW_AVATAR}, SHOW_BADGES: {SHOW_BADGES}, DEBUG: {DEBUG}")

    if missing_values:
        verify_config_window(config)

def verify_config_window(config):
    def on_confirm():
        global OBS_HOST, OBS_PORT, OBS_PASSWORD, FLASK_PORT, CHAT_URL, SHOW_AVATAR, SHOW_BADGES, DEBUG
        OBS_HOST = entries['OBS_HOST'].get()
        OBS_PORT = int(entries['OBS_PORT'].get())
        OBS_PASSWORD = entries['OBS_PASSWORD'].get()
        FLASK_PORT = int(entries['FLASK_PORT'].get())
        CHAT_URL = entries['CHAT_URL'].get()
        SHOW_AVATAR = entries['DISPLAY_SHOW_AVATAR'].get() == '1'
        SHOW_BADGES = entries['DISPLAY_SHOW_BADGES'].get() == '1'
        DEBUG = entries['MISC_DEBUG'].get() == '1'

        update_config_file()  # Appeler cette fonction pour mettre à jour le fichier

        root.destroy()  # Utiliser root.destroy() pour fermer correctement la fenêtre

    def update_config_file():
        config = configparser.ConfigParser()
        config['OBS'] = {
            'HOST': OBS_HOST,
            'PORT': str(OBS_PORT),
            'PASSWORD': OBS_PASSWORD
        }
        config['FLASK'] = {
            'PORT': str(FLASK_PORT)
        }
        config['CHAT'] = {
            'URL': CHAT_URL
        }
        config['DISPLAY'] = {
            'SHOW_AVATAR': str(SHOW_AVATAR),
            'SHOW_BADGES': str(SHOW_BADGES)
        }
        config['MISC'] = {
            'DEBUG': str(DEBUG)
        }
        
        with open(settings_ini_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        print(f"Config updated at {settings_ini_path}")

    def check_entries(*args):
        all_filled = all(entry.get() for entry in entries.values() if not isinstance(entry, tk.BooleanVar))
        confirm_button.config(state=tk.NORMAL if all_filled else tk.DISABLED)

    root = tk.Tk()
    root.title("Vérifiez la configuration")

    # Fonction pour rediriger la fermeture de la fenêtre à l'annulation
    def on_closing():
        root.quit()
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Configurer les styles pour les boutons
    style = ttk.Style()
    style.configure('TButton', font=('Helvetica', 14, 'bold'))

    entries = {}

    for section, keys in default_values.items():
        frame = ttk.LabelFrame(root, text=section)
        frame.pack(fill="x", padx=10, pady=10)

        for key in keys:
            full_key = f'{section}_{key}'
            label = ttk.Label(frame, text=key)
            label.pack(side="left", padx=5, pady=5)

            if key in ['SHOW_AVATAR', 'SHOW_BADGES', 'DEBUG']:
                var = tk.BooleanVar(value=config.getboolean(section, key, fallback=default_values[section][key] == 'True'))
                entry = ttk.Checkbutton(frame, variable=var)
                entry.pack(side="left", padx=5, pady=5)
                entries[full_key] = var
            else:
                entry = ttk.Entry(frame, font=('Helvetica', 14))
                entry.insert(0, config.get(section, key, fallback=default_values[section][key]))
                entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
                entry.bind("<KeyRelease>", check_entries)
                entries[full_key] = entry

    button_frame = ttk.Frame(root)
    button_frame.pack(fill="x", padx=10, pady=10)

    cancel_button = ttk.Button(button_frame, text="Annuler et Quitter", command=on_closing)
    cancel_button.pack(side="left", padx=5, pady=5)

    confirm_button = ttk.Button(button_frame, text="Confirmer", command=on_confirm, state=tk.DISABLED)
    confirm_button.pack(side="right", padx=5, pady=5)

    check_entries()

    # Ajuster la taille de la fenêtre pour qu'elle s'adapte au contenu
    root.update_idletasks()
    root.minsize(root.winfo_width(), root.winfo_height())

    # Centrer la fenêtre sur l'écran
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - root.winfo_height() / 2)
    position_right = int(screen_width / 2 - root.winfo_width() / 2)
    root.geometry(f"+{position_right}+{position_top}")

    root.mainloop()

# Initial attempt to read the config
read_config()









ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
obs_chat_name=None
source_found = False

def connect_ws():
    try:
        if not ws.ws or not ws.ws.connected:
            ws.connect()
    except ConnectionFailure as e:
        print(Fore.RED + f"Erreur de connexion : {e}" + Style.RESET_ALL)
        show_error_image("ACTIVEZ WEBSOCKET DANS OBS COMME CECI\nParamètre absent ? Relancez OBS")
        raise e

def disconnect_ws():
    if ws.ws and ws.ws.connected:
        try:
            ws.disconnect()
        except ConnectionFailure as e:
            print(Fore.RED + f"Erreur de déconnexion : {e}" + Style.RESET_ALL)

def get_active_scene_name():
    try:
        scene_list = ws.call(obs_request.GetSceneList())
        active_scene_name = scene_list.getCurrentScene()
        print("Scène active :", active_scene_name)
        return active_scene_name
    except Exception as e:
        show_error_image("ACTIVEZ WEBSOCKET DANS OBS COMME CECI\nParamètre absent ? Relancez OBS")
        raise e

def show_error_image(message):
    def retry():
        error_dialog.destroy()
        subprocess.Popen([sys.executable] + sys.argv)

    root = tk.Tk()
    root.withdraw()
    error_dialog = tk.Toplevel(root)
    error_dialog.configure(bg='#2E3B4E')
    error_dialog.title("Erreur")

    f2 = ('Arial', 18, 'bold')
    tk.Label(error_dialog, text=message, bg='#2E3B4E', fg='#FFD700', font=f2, wraplength=660).pack(pady=20, padx=20)

    image_path = os.path.join(local_app_data, 'OBS_module_chat', 'tuto.png')
    image = Image.open(image_path)
    photo = ImageTk.PhotoImage(image)

    img_label = tk.Label(error_dialog, image=photo)
    img_label.image = photo
    img_label.pack(pady=10)

    tk.Button(error_dialog, text="Réessayer", command=retry, bg='#4682B4', fg='white', font=('Arial', 24, 'bold')).pack(pady=20)
    error_dialog.mainloop()



def check_chat_obs():
    global source_found, obs_chat_name
    active_scene = get_active_scene_name()
    sources_response = ws.call(obs_request.GetSceneItemList(sceneName=active_scene))
    sources = sources_response.getSceneItems()
    for source in sources:
        #print(f"Vérification de la source : {source}")  # Impression pour débogage
        if source['sourceType'] == 'input' and source['sourceKind'] == 'browser_source':  # Vérification correcte de la source
            source_settings_response = ws.call(obs_request.GetSourceSettings(sourceName=source['sourceName']))
            #print(f"Réponse de GetSourceSettings pour {source['sourceName']} : {source_settings_response.datain}")  # Impression pour débogage
            source_settings = source_settings_response.getSourceSettings()
            if source_settings.get('url', '').startswith(f'http://localhost:{FLASK_PORT}/chat'):
                print(Fore.GREEN + f"Source flux chat trouvée : {source['sourceName']}" + Fore.RESET)
                obs_chat_name = source['sourceName']
                return True
    return False

def copy_to_clipboard(text, root):
    root.clipboard_clear()
    root.clipboard_append(text)
    root.update()  # nécessaire pour que la mise à jour soit prise en compte

def show_dialog(root):
    dialog = tk.Toplevel(root)
    dialog.configure(bg='#2E3B4E')
    dialog.title("Source Chat non trouvée")
    dialog.geometry("700x550")

    f = ('Arial', 24, 'bold')
    tk.Label(dialog, text="LA SOURCE NAVIGATEUR DU CHAT N'A PAS ETE TROUVEE DANS LA SCENE ACTUELLE OBS",
             bg='#2E3B4E', fg='#FFD700', font=f, wraplength=660).pack(pady=20, padx=20)

    url_frame = tk.Frame(dialog, bg='#2E3B4E')
    url_frame.pack(pady=5, padx=20)
    url_label = tk.Label(url_frame, text=f"http://localhost:{FLASK_PORT}/chat", bg='#2E3B4E', fg='white', font=f)
    url_label.pack(side='left')
    url_button = tk.Button(url_frame, text="Copier", command=lambda: copy_to_clipboard(f"http://localhost:{FLASK_PORT}/chat", root),
                           bg='#4682B4', fg='white', font=('Arial', 12, 'bold'))
    url_button.pack(side='left', padx=10)

    height_frame = tk.Frame(dialog, bg='#2E3B4E')
    height_frame.pack(pady=5, padx=20)
    height_label = tk.Label(height_frame, text="Largeur: 370", bg='#2E3B4E', fg='white', font=f)
    height_label.pack(side='left')
    height_button = tk.Button(height_frame, text="Copier", command=lambda: copy_to_clipboard("370", root),
                              bg='#4682B4', fg='white', font=('Arial', 12, 'bold'))
    height_button.pack(side='left', padx=10)

    width_frame = tk.Frame(dialog, bg='#2E3B4E')
    width_frame.pack(pady=5, padx=20)
    width_label = tk.Label(width_frame, text="Hauteur: 700", bg='#2E3B4E', fg='white', font=f)
    width_label.pack(side='left')
    width_button = tk.Button(width_frame, text="Copier", command=lambda: copy_to_clipboard("700", root),
                             bg='#4682B4', fg='white', font=('Arial', 12, 'bold'))
    width_button.pack(side='left', padx=10)

    tk.Frame(dialog, height=60, bg='#2E3B4E').pack()  # Ajout de 60 pixels d'espace

    def on_enter(e): e.widget['background'] = '#3E8EDE'
    def on_leave(e): e.widget['background'] = e.widget.orig_color
    

    def retry():
        dialog.destroy()
        try:
            if not check_chat_obs():
                show_dialog(root)
            else:
                root.destroy()
        except Exception as e:
            show_error_image("ACTIVEZ WEBSOCKET DANS OBS COMME CECI\nParamètre absent ? Relancez OBS")

    def cancel():
        disconnect_ws()
        root.destroy()
        sys.exit()

    button_frame = tk.Frame(dialog, bg='#2E3B4E')
    button_frame.pack(pady=10, padx=20, fill='both', expand=True)
    button_frame.pack_propagate(False)

    retry_button = tk.Button(button_frame, text="Rechercher à nouveau", command=retry, bg='#FFD700', fg='black', font=f, activebackground='#3E8EDE',
                            activeforeground='white', relief='flat', bd=0)
    retry_button.pack(pady=(0, 5), fill='x')  # Réduire pady pour rapprocher les boutons
    retry_button.orig_color = '#FFD700'
    retry_button.bind("<Enter>", on_enter)
    retry_button.bind("<Leave>", on_leave)

    cancel_button = tk.Button(button_frame, text="Annuler", command=cancel, bg='#B22222', fg='white', font=f, activebackground='#3E8EDE',
                            activeforeground='white', relief='flat', bd=0)
    cancel_button.pack(pady=(5, 0), fill='x')  # Réduire pady pour rapprocher les boutons
    cancel_button.orig_color = '#B22222'
    cancel_button.bind("<Enter>", on_enter)
    cancel_button.bind("<Leave>", on_leave)

    tk.Frame(dialog, bg='#FFD700', height=5).pack(fill='x', pady=5)
    tk.Frame(dialog, bg='#4682B4', height=5).pack(fill='x', pady=5)
    dialog.mainloop()


def main_loop():
    root = tk.Tk()
    root.withdraw()
    try:
        connect_ws()
        if not check_chat_obs():
            show_dialog(root)
    except Exception as e:
        show_error_image("ACTIVEZ WEBSOCKET DANS OBS COMME CECI\nParamètre absent ? Relancez OBS")
    root.quit()

# Démarrage de la boucle de vérification
connect_ws()
try:
    main_loop()
finally:
    disconnect_ws()





EMOJI_FOLDER = os.path.join(os.getcwd(), 'emojis')
if not os.path.exists(EMOJI_FOLDER):
    os.makedirs(EMOJI_FOLDER)
#logging.basicConfig(level=logging.DEBUG)


def split_message(message):
    print(f"\n BEFORE SPLIT MESSAGE :\n  {message}\n")
    message = re.sub(r'\s+', ' ', str(message).strip())

    try:
        # Split the timestamp and the rest of the message
        parts = message.split(' ', 2)
        if len(parts) > 1 and re.match(r'^\d{2}:\d{2}$', parts[0]):
            timestamp = parts[0]
            rest = parts[1]
            if len(parts) == 3:
                rest += ' ' + parts[2]
        else:
            timestamp = None
            rest = message

        # Extract the avatar and badges
        avatar = None
        badges = []
        rest = rest.strip()
        while rest.startswith(':::'):
            end_idx = rest.find(':::', 3)
            if end_idx == -1:
                break
            url = rest[3:end_idx]
            if not avatar:
                avatar = url
            else:
                badges.append(url)
            rest = rest[end_idx + 3:].strip()

        # If there's no avatar, the whole rest is content
        if not avatar:
            pseudo = None
            content = rest
        else:
            # Extract the pseudo and content
            match = re.match(r'(\S+?)\s*:\s*(.*)', rest)
            if match:
                pseudo = match.group(1)
                content = match.group(2).strip()
            else:
                parts = rest.split(' ', 1)
                pseudo = parts[0]
                content = parts[1].strip() if len(parts) > 1 else ''

        # Replace old gift value with new gift value in the content
        #if old_gift_value and new_gift_value:
            #content = re.sub(r'(?<=\s)(\d+)(?=\s)', lambda m: new_gift_value if m.group(1) == old_gift_value else m.group(1), content, 1)

        print(f"\n AFTER SPLIT MESSAGE full :\n  timestamp={timestamp}\n  pseudo={pseudo}\n  content={content}\n  avatar={avatar}\n  badges={badges}\n")
    except ValueError:
        print(f"\n AFTER SPLIT MESSAGE ValueError :\n  message={message}\n")
        return None, None, message, None, []

    return timestamp, pseudo, content, avatar, badges








class MessageManager:
    def __init__(self, socketio):
        #self.messages = []
        self.socketio = socketio

    def process_message(self, timestamp, pseudo, content, avatar, badges, is_gift):
        self.socketio.emit('new_message', {'timestamp': timestamp, 'pseudo': pseudo, 'content': content, 'avatar': avatar, 'badges': badges, 'is_gift': str(is_gift).lower()})

    def delete_message(self, content, pseudo, is_gift):
        self.socketio.emit('delete_message', {'pseudo': pseudo, 'content': content, 'is_gift': str(is_gift).lower()})

    def get_messages(self):
        return self.messages






class EventManager:
    def __init__(self):
        self.event_queue = []
        self.last_trigger_time = datetime.min

    def detect_event(self, message):
        if "vient de suivre !" in message:
            print(f"New follower event detected: {message}")
            self.event_queue.append(message)

    def process_queue(self):
        now = datetime.now()
        if self.event_queue and (now - self.last_trigger_time) > timedelta(seconds=10):
            self.send_to_obs(self.event_queue.pop(0))
            self.last_trigger_time = now

    def send_to_obs(self, message):
        lines = message.split('\n')
        if len(lines) >= 2:
            pseudo = lines[1].split(' ')[0]
            event_text = "Nouveau follower :"
            formatted_message = f"{event_text} {pseudo}"
        else: 
            print("ERREUR : Format du message non reconnu")

        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        ws.call(obs_request.SetTextGDIPlusProperties(source='FollowerAlert', text=formatted_message))
        ws.disconnect()
        print(f"Sent to OBS: {formatted_message}")





class Scrapper:
    def __init__(self, socketio):
        self.driver = self._init_driver()
        self.event_manager = EventManager()
        self.message_manager = MessageManager(socketio)

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--log-level=1")
        chrome_service = Service('C:\\WebDrivers\\chromedriver.exe')
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
        driver.get(str(CHAT_URL))
        time.sleep(2)
        self._click_more_options(driver)
        self._enable_timestamp(driver)
        time.sleep(1)
        self._inject_observer_script(driver)
        return driver


    def _click_more_options(self, driver):
        try:
            print("Clicking the 'More options' button...")
            more_options_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//div[contains(@class, "more-option-btn")]'))
            )
            more_options_button.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error clicking 'More options' button: {e}")


    def _enable_timestamp(self, driver):
        try:
            print("Searching for 'Afficher le timestamp' label...")
            span_elements = driver.find_elements(By.XPATH, '//span[contains(text(), "Afficher le timestamp")]')
            if span_elements:
                print("Found 'Afficher le timestamp' label")
                span_element = span_elements[0]
                parent_div = span_element.find_element(By.XPATH, './ancestor::div[contains(@class, "flex-justify-between")]')
                checkbox = parent_div.find_element(By.XPATH, './/input[@type="checkbox"]')
                is_checked = checkbox.is_selected()
                print(f"Checkbox is selected: {is_checked}")
                if not is_checked:
                    driver.execute_script("arguments[0].click();", checkbox)
                    print("Checkbox clicked via JavaScript")
                    time.sleep(1)
                    is_checked_after = checkbox.is_selected()
                    print(f"Checkbox is selected after click: {is_checked_after}")
                else:
                    print("Checkbox was already selected")
            else:
                print("Did not find 'Afficher le timestamp' label")
        except Exception as e:
            print(f"Error finding 'Afficher le timestamp': {e}")



    def _inject_observer_script(self, driver):
        observer_script = """
        (function() {{
            const logLevels = ['log', 'warn', 'error'];
            logLevels.forEach(level => {{
                const original = console[level];
                console[level] = function(...args) {{
                    original.apply(console, args);
                    fetch('http://localhost:{FLASK_PORT}/console_log', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ level, message: args }})
                    }}).catch(error => original('Failed to send log:', error));
                }};
            }});
            const targetNode = document.querySelector('div.chatbody');
            if (!targetNode) {{
                console.error('No targetNode found.');
                return;
            }}
            console.log('Observing targetNode:', targetNode);
            const config = {{ childList: true, subtree: true, characterData: true, characterDataOldValue: true }};
            const extractMessageText = (node) => {{
                let messageText = '';
                node.childNodes.forEach(child => {{
                    if (child.nodeType === Node.TEXT_NODE) {{
                        messageText += child.textContent.replace(/\\s+/g, ' ');
                    }} else if (child.nodeType === Node.ELEMENT_NODE) {{
                        if (child.tagName === 'IMG') {{
                            let imgSrc = child.currentSrc || child.getAttribute('src');
                            if (imgSrc) {{
                                if (!imgSrc.startsWith('http')) {{
                                    imgSrc = `https://dlive.tv${{imgSrc}}`;
                                }}
                                messageText += ` :::${{imgSrc}}::: `;
                            }}
                        }} else {{
                            messageText += extractMessageText(child);
                        }}
                    }}
                }});
                return messageText;
            }};
            const generateUniqueId = (index, text) => `${{index}}-${{text.trim().replace(/\\s+/g, '£££')}}`;
            const getCurrentDivIds = () => {{
                return Array.from(targetNode.querySelectorAll('div')).map((div, index) => generateUniqueId(index, extractMessageText(div)));
            }};
            let previousDivIds = getCurrentDivIds();
            const containsGiftEmoji = (node) => {{
                if (node.nodeType === Node.ELEMENT_NODE && node.classList.contains('gift-emoji')) {{
                    return true;
                }}
                return Array.from(node.childNodes).some(child => containsGiftEmoji(child));
            }};
            const handleMessage = (nodes, isAdded, ignoreNewMessages) => {{
                if (ignoreNewMessages && isAdded) {{
                    return;
                }}
                for (const node of nodes) {{
                    if (node.nodeType === 1) {{ // Element nodes only
                        const messageText = extractMessageText(node).trim();
                        const parent = node.parentNode;
                        if (parent) {{
                            const uniqueId = generateUniqueId(Array.from(parent.children).indexOf(node), messageText);
                            const isGift = containsGiftEmoji(node);
                            if (isAdded) {{
                                console.log('New message detected:', messageText, 'Is gift:', isGift);
                                fetch('http://localhost:{FLASK_PORT}/new_message', {{
                                    method: 'POST',
                                    headers: {{ 'Content-Type': 'application/json' }},
                                    body: JSON.stringify({{ message: messageText, is_gift: isGift }})
                                }}).then(response => response.text())
                                .then(data => console.log('Response from server (new_message):', data))
                                .catch(error => console.error('Error:', error));
                            }}
                        }}
                    }}
                }}
            }};
            const callback = (mutationsList) => {{
                console.error('\\n\\n******************************************************\\n\\n');
                const currentDivIds = getCurrentDivIds();
                // Variable pour suivre si une suppression a été détectée
                let deletionDetected = false;
                let removedText = null;
                let isGift = null;
                // Détection du premier message supprimé uniquement
                const removedId = previousDivIds.find(id => !currentDivIds.includes(id));
                if (removedId) {{
                    removedText = removedId.substring(removedId.indexOf('-') + 1).replace(/£££/g, ' ').replace(/\\s+/g, ' ').trim();
                    isGift = removedText.includes(":::https://dlive.tv/img/gift_");
                    console.log(' isGift  in  JS:', isGift);
                    if (!isGift) {{
                        console.log('Message removed:', removedText);
                        deletionDetected = true;
                        fetch('http://localhost:{FLASK_PORT}/remove_message', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ message: removedText, is_gift: isGift }})
                        }}).then(response => response.text())
                        .then(data => console.log('Response from server (remove_message):', data))
                        .catch(error => console.error('Error:', error));
                    }} else {{
                        console.log('Mutation detected type GIFT. Mostly an increased GIFT');
                        fetch('http://localhost:{FLASK_PORT}/upgrade_gift', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ old_message: removedText }})
                        }}).then(response => response.text())
                        .then(data => console.log('Response from server (new_message):', data))
                        .catch(error => console.error('Error:', error));
                    }}
                }} else {{
                    for (const mutation of mutationsList) {{
                        if (mutation.type === 'childList') {{
                            console.log('Mutation detected type : childList');
                            handleMessage(mutation.addedNodes, true, deletionDetected);
                            break;
                        }}
                    }}
                }}
                previousDivIds = getCurrentDivIds();
            }};
            const observer = new MutationObserver(callback);
            observer.observe(targetNode, config);
            console.log('MutationObserver attached and observing:', targetNode);
        }})();
        """.format(FLASK_PORT=FLASK_PORT)
        driver.execute_script(observer_script)



    
    def process_manual_div(self):
        def extract_message_text(node):
            message_text = []
            is_gift = False

            def _extract(node):
                nonlocal is_gift
                if node.name is None:
                    if node.string:
                        message_text.append(node.string.replace('\n', ' ').replace('\r', ' ').strip())
                elif node.name == 'img':
                    if 'gift-emoji' in node.get('class', []):
                        is_gift = True
                    img_src = node.get('src')
                    if img_src:
                        if not img_src.startswith('http'):
                            img_src = f'https://dlive.tv{img_src}'
                        message_text.append(f' :::{img_src}::: ')
                else:
                    for child in node.children:
                        _extract(child)

            _extract(node)
            return ' '.join(message_text).strip(), is_gift

        try:
            with open('add_manual_div.txt', 'r', encoding='utf-8') as file:
                div_content = file.read()
            soup = BeautifulSoup(div_content, 'html.parser')
            target_node = soup.select_one('div.chat-row-wrap')
            if not target_node:
                return
            print('Observing targetNode:', target_node)
            message_text, is_gift = extract_message_text(target_node)
            print("IS GIFT :", is_gift)

            timestamp, pseudo, content, avatar, badges = split_message(message_text)
            
            if not pseudo:
                self.event_manager.detect_event(timestamp, pseudo, content, avatar, badges, is_gift)
            self.message_manager.process_message(timestamp, pseudo, content, avatar, badges, is_gift)

        except FileNotFoundError:
            pass
        




    def run(self):
        @app.route('/')
        def index():
            return render_template('chat_panel.html')
        
        @app.route('/emojis/<filename>')
        def serve_emoji(filename):
            return send_from_directory(EMOJI_FOLDER, filename)

        @app.route('/get_image_extension', methods=['POST'])
        def get_image_extension():
            data = request.json
            url = data['url']
            try:
                response = requests.head(url, allow_redirects=True)
                if response.status_code == 200:
                    content_type = response.headers.get('content-type')
                    if content_type:
                        return jsonify({'extension': content_type.split('/')[-1].split('+')[0]})
                return jsonify({'extension': 'unknown'}), 400
            except Exception as e:
                return jsonify({'extension': 'unknown', 'error': str(e)}), 500

        @app.route('/download_emoji', methods=['POST'])
        def download_emoji():
            data = request.json
            print(f"\n Requete de telechargement d'image :\n --> {data}\n")
            emoji_link = data['emoji_link']
            emoji_name = data['emoji_name']
            emoji_extension = "." + data['emoji_extension'].lower()
            
            if is_avatar := data.get('is_avatar', False):
                emoji_link = re.sub(r'/\d+x\d+/', '/50x50/', emoji_link)
            is_badge = data.get('is_badge', False)
            
            response = requests.get(emoji_link)
            if response.status_code == 200:
                if emoji_extension == '.svg':
                    try:
                        # Convertir SVG en PNG
                        print("Conversion de SVG en PNG")
                        png_output = BytesIO()
                        cairosvg.svg2png(bytestring=response.content, write_to=png_output, background_color='none')  # Conserver la transparence
                        print("SVG converti en PNG avec succès")

                        png_output.seek(0)  # Assurez-vous de revenir au début de l'objet BytesIO
                        image = Image.open(png_output)
                        emoji_extension = f".png"
                        print("Image ouverte depuis PNG")
                    except Exception as e:
                        print("Erreur lors de la conversion SVG en PNG : ", e)
                        return jsonify({'status': 'error', 'message': 'Failed to convert SVG to PNG'}), 500
                elif emoji_extension == '.gif':
                    # Si l'extension est .gif, nous voulons simplement sauvegarder le fichier tel quel sans modification
                    path = os.path.join(EMOJI_FOLDER, f'{emoji_name}{emoji_extension}')
                    try:
                        with open(path, 'wb') as f:
                            f.write(response.content)
                        print(f"GIF sauvegardé avec succès à {path}")
                        return jsonify({'status': 'success', 'path': path})
                    except Exception as e:
                        print("Erreur lors de la sauvegarde du GIF : ", e)
                        return jsonify({'status': 'error', 'message': 'Failed to save GIF'}), 500
                else:
                    try:
                        print("Ouverture de l'image depuis BytesIO")
                        image = Image.open(BytesIO(response.content))
                        print("Image ouverte avec succès")
                        if emoji_extension not in ['.gif', '.png']:
                            emoji_extension = f".png"
                    except Exception as e:
                        print("Erreur lors de l'ouverture de l'image : ", e)
                        return jsonify({'status': 'error', 'message': 'Failed to open image'}), 500

                
                if not is_avatar and emoji_extension != '.gif':
                    try:
                        max_size = 18 if is_badge else 150 if "/emote/" in emoji_link else 38 
                        ratio = min(max_size / image.width, max_size / image.height)
                        image = image.resize((int(image.width * ratio), int(image.height * ratio)), Image.LANCZOS)
                        print(f"Image redimensionnée avec succès à {max_size}x{max_size}")
                    except Exception as e:
                        print("Erreur lors du redimensionnement de l'image : ", e)
                        return jsonify({'status': 'error', 'message': 'Failed to resize image'}), 500

                try:
                    # Vérifiez que l'image est en mode RGBA pour conserver la transparence
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=50))
                    print("Netteté de l'avatar augmentée avec succès")
                except Exception as e:
                    print("Erreur lors de l'augmentation de la netteté de l'avatar : ", e)
                    return jsonify({'status': 'error', 'message': 'Failed to enhance avatar sharpness'}), 500

                if not os.path.exists(EMOJI_FOLDER):
                    os.makedirs(EMOJI_FOLDER)
                    print(f"Dossier {EMOJI_FOLDER} créé")

                path = os.path.join(EMOJI_FOLDER, f'{emoji_name}{emoji_extension}')
                try:
                    image.save(path)
                    print(f"Image sauvegardée avec succès à {path}")
                    return jsonify({'status': 'success', 'path': path})
                except Exception as e:
                    print("Erreur lors de la sauvegarde de l'image : ", e)
                    return jsonify({'status': 'error', 'message': 'Failed to save image'}), 500
            else:
                print("Erreur lors du téléchargement de l'emoji, statut de la réponse: ", response.status_code)
                return jsonify({'status': 'error', 'message': 'Failed to download emoji'}), 400




        @socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @socketio.on('console_log')
        def handle_console_log(msg):
            level = msg.get('level')
            message = ' '.join(map(str, msg.get('message')))
            
            if level == 'log':
                print(f'INFO: {Fore.LIGHTCYAN_EX + message + Fore.RESET}')
            elif level == 'warn':
                print(f'WARNING: {Fore.CYAN + message + Fore.RESET}')
            elif level == 'error':
                print(f'ERROR: {Fore.RED + message + Fore.RESET}')

        @app.route('/console_log', methods=['POST'])
        def console_log():
            data = request.get_json()
            level = data.get('level')
            message = ' '.join(map(str, data.get('message')))
            
            if level == 'log':
                print(f'INFO: {Fore.LIGHTGREEN_EX + message + Fore.RESET}')
            elif level == 'warn':
                print(f'WARNING: {Fore.LIGHTYELLOW_EX + message + Fore.RESET}')
            elif level == 'error':
                print(f'ERROR: {Fore.LIGHTMAGENTA_EX + message + Fore.RESET}')
            return jsonify({"status": "success"}), 200

        @app.route('/new_message', methods=['POST'])
        def new_message():
            data = request.get_json()
            full_message = data.get('message', '')
            is_gift = data.get('is_gift', '')
            timestamp, pseudo, content, avatar, badges = split_message(full_message)
            #print('timestamp :', timestamp, '\n pseudo :', pseudo, '\n content :', content, '\n avatar :', avatar, '\n badges :', badges, '\n IS_GIFT :', is_gift)
            if content:
                if "vient de suivre !" in content:
                    self.event_manager.detect_event(content)
            self.message_manager.process_message(timestamp, pseudo, content, avatar, badges, is_gift)
            return 'OK', 200

        @app.route('/upgrade_gift', methods=['POST'])
        def modified_message():
            data = request.get_json()
            old_message = data.get('old_message', '')
            timestamp, pseudo, content, avatar, badges = split_message(old_message)
            self.message_manager.process_message(timestamp, pseudo, content, avatar, badges, True)
            return 'OK', 200            

        @app.route('/config', methods=['GET'])
        def get_config():
            return jsonify({
                'show_avatar': SHOW_AVATAR,
                'show_badges': SHOW_BADGES
            })   

        @app.route('/remove_message', methods=['POST'])
        def removed_message():
            full_message = request.get_json().get('message', '')
            is_gift = request.get_json().get('is_gift', '')
            timestamp, pseudo, content, avatar, badges = split_message(full_message)
            print("To delete = ", timestamp, pseudo, content)
            self.message_manager.delete_message(content, pseudo, is_gift)
            return 'OK', 200

        @app.route('/chat')
        def chat():
            return send_from_directory('.', 'chat_panel.html')

        @app.route('/messages')
        def messages():
            return jsonify(self.message_manager.get_messages())

        flask_thread = Thread(target=socketio.run, args=(app,), kwargs={'port': FLASK_PORT, 'debug': True, 'use_reloader': False})

        flask_thread.start()

        time.sleep(2)
        
        ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
        ws.connect()
        ws.call(obs_request.RefreshBrowserSource(sourceName=obs_chat_name))
        ws.disconnect()

        time.sleep(2)

        test_response = requests.post(f'http://localhost:{FLASK_PORT}/new_message', json={'message': 'Test message'})
        print(f"Test response from Flask: {test_response.text}")





        try:
            while True:
                self.event_manager.process_queue()
                #self.process_manual_div()
                time.sleep(10)
        except KeyboardInterrupt:
            print("Script interrompu par l'utilisateur.")
        finally:
            self.driver.quit()



app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

notifier = Scrapper(socketio)
notifier.run()
