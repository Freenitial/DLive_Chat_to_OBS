#0.1

import configparser
import os, re, sys
import time
from datetime import datetime, timedelta
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
from threading import Thread
from PIL import Image
from io import BytesIO
import colorama
from colorama import Fore, Style
import tkinter as tk
import requests

colorama.init()
config = configparser.ConfigParser()
config.read('config.ini')
OBS_HOST = config.get('OBS', 'HOST')
OBS_PORT = config.getint('OBS', 'PORT')
OBS_PASSWORD = config.get('OBS', 'PASSWORD')
FLASK_PORT = config.getint('FLASK', 'PORT')
CHAT_URL = config.get('CHAT', 'URL')
ws = obsws(OBS_HOST, OBS_PORT, OBS_PASSWORD)
obs_chat_name=None
source_found = False




def connect_ws():
    if not ws.ws or not ws.ws.connected:
        try:
            ws.connect()
        except ConnectionFailure as e:
            print(Fore.RED + f"Erreur de connexion : {e}" + Style.RESET_ALL)

def disconnect_ws():
    if ws.ws and ws.ws.connected:
        try:
            ws.disconnect()
        except ConnectionFailure as e:
            print(Fore.RED + f"Erreur de déconnexion : {e}" + Style.RESET_ALL)

def get_active_scene_name():
    scene_list = ws.call(obs_request.GetSceneList())
    active_scene_name = scene_list.getCurrentScene()
    print("Scène active :", active_scene_name)
    return active_scene_name

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
    height_label = tk.Label(height_frame, text="Hauteur: 600", bg='#2E3B4E', fg='white', font=f)
    height_label.pack(side='left')
    height_button = tk.Button(height_frame, text="Copier", command=lambda: copy_to_clipboard("600", root),
                              bg='#4682B4', fg='white', font=('Arial', 12, 'bold'))
    height_button.pack(side='left', padx=10)

    width_frame = tk.Frame(dialog, bg='#2E3B4E')
    width_frame.pack(pady=5, padx=20)
    width_label = tk.Label(width_frame, text="Largeur: 230", bg='#2E3B4E', fg='white', font=f)
    width_label.pack(side='left')
    width_button = tk.Button(width_frame, text="Copier", command=lambda: copy_to_clipboard("230", root),
                             bg='#4682B4', fg='white', font=('Arial', 12, 'bold'))
    width_button.pack(side='left', padx=10)

    tk.Frame(dialog, height=60, bg='#2E3B4E').pack()  # Ajout de 60 pixels d'espace

    def on_enter(e): e.widget['background'] = '#3E8EDE'
    def on_leave(e): e.widget['background'] = e.widget.orig_color
    def retry():
        dialog.destroy()
        if not check_chat_obs():
            show_dialog(root)
        else:
            root.destroy()  # Ferme proprement la fenêtre Tkinter et termine le script
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
    if not check_chat_obs():
        show_dialog(root)
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
    message = str(message).strip()
    message = re.sub(r'\s+', ' ', message)
    try:
        timestamp, rest = message.split(' ', 1)
        pseudo, content = rest.split(' : ', 1)
    except ValueError:
        return None, None, message
    return timestamp, pseudo, content






class MessageManager:
    def __init__(self, socketio):
        self.messages = []
        self.socketio = socketio

    def process_message(self, full_message, timestamp, pseudo, content):
        self.messages.append(full_message)
        self.socketio.emit('new_message', {'timestamp': timestamp, 'pseudo': pseudo, 'content': content})
        print(f"Message added = {full_message}")

    def delete_message(self, full_message, content):
        self.socketio.emit('delete_message', content)
        print(f"Message deleted = {full_message}")

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
        chrome_options.add_argument("--log-level=3")
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
            const targetNode = document.querySelector('div.chatbody');
            if (!targetNode) {{
                console.error('No targetNode found.');
                return;
            }}

            console.log('Observing targetNode:', targetNode);

            const config = {{ childList: true, subtree: true }};
            const knownMessages = new Set();

            const extractMessageText = (node) => {{
                let messageText = '';
                node.childNodes.forEach(child => {{
                    if (child.nodeType === Node.TEXT_NODE) {{
                        messageText += child.textContent.replace(/\\s+/g, ' ');
                    }} else if (child.nodeType === Node.ELEMENT_NODE) {{
                        if (child.classList.contains('emoji')) {{
                            const emojiId = child.querySelector('img').getAttribute('src').split('/').pop().replace('.png', '');
                            messageText += `:::$EMOJI_ID:::`.replace('$EMOJI_ID', emojiId);
                        }} else {{
                            messageText += extractMessageText(child);
                        }}
                    }}
                }});
                return messageText;
            }};

            const generateUniqueId = (index, text) => `${{index}}-${{text.trim().replace(/\\s+/g, '-')}}`;

            const getCurrentDivIds = () => {{
                return Array.from(targetNode.querySelectorAll('div')).map((div, index) => generateUniqueId(index, extractMessageText(div)));
            }};

            let previousDivIds = getCurrentDivIds();

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

                            if (isAdded) {{
                                if (!knownMessages.has(uniqueId)) {{
                                    knownMessages.add(uniqueId);
                                    console.log('New message detected:', messageText);
                                    fetch('http://localhost:{FLASK_PORT}/new_message', {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{ message: messageText }})
                                    }}).then(response => response.text())
                                    .then(data => console.log('Response from server (new_message):', data))
                                    .catch(error => console.error('Error:', error));
                                }}
                            }} else {{
                                if (knownMessages.has(uniqueId)) {{
                                    knownMessages.delete(uniqueId);
                                    console.log('Message removed:', messageText);
                                    fetch('http://localhost:{FLASK_PORT}/remove_message', {{
                                        method: 'POST',
                                        headers: {{ 'Content-Type': 'application/json' }},
                                        body: JSON.stringify({{ message: messageText }})
                                    }}).then(response => response.text())
                                    .then(data => console.log('Response from server (remove_message):', data))
                                    .catch(error => console.error('Error:', error));
                                }}
                            }}
                        }}
                    }}
                }}
            }};

            const callback = (mutationsList) => {{
                const currentDivIds = getCurrentDivIds();

                // Variable pour suivre si une suppression a été détectée
                let deletionDetected = false;

                // Détection du premier message supprimé uniquement
                const removedId = previousDivIds.find(id => !currentDivIds.includes(id));
                if (removedId) {{
                    const removedText = removedId.split('-').slice(1).join(' ').replace(/-/g, ' ').replace(/\\s+/g, ' ').trim();
                    console.log('Message removed:', removedText);
                    deletionDetected = true;
                    fetch('http://localhost:{FLASK_PORT}/remove_message', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ message: removedText }})
                    }}).then(response => response.text())
                    .then(data => console.log('Response from server (remove_message):', data))
                    .catch(error => console.error('Error:', error));
                }}

                // Détection des nouveaux messages ou suppressions, en tenant compte de la suppression détectée
                for (const mutation of mutationsList) {{
                    if (mutation.type === 'childList') {{
                        handleMessage(mutation.addedNodes, true, deletionDetected);
                        handleMessage(mutation.removedNodes, false, deletionDetected);
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



    def run(self):
        @app.route('/')
        def index():
            return render_template('chat_panel.html')
        
        @app.route('/emojis/<filename>')
        def serve_emoji(filename):
            return send_from_directory(EMOJI_FOLDER, filename)
        
        @app.route('/download_emoji', methods=['POST'])
        def download_emoji():
            data = request.json
            emoji_name = data['emoji_name']
            url = f'https://images.prd.dlivecdn.com/emoji/{emoji_name}'
            response = requests.get(url)
            if response.status_code == 200:
                image = Image.open(BytesIO(response.content))
                max_size = 20
                ratio = min(max_size / image.width, max_size / image.height)
                image = image.resize((int(image.width * ratio), int(image.height * ratio)), Image.LANCZOS)
                # Vérifiez que le dossier existe
                if not os.path.exists(EMOJI_FOLDER):
                    os.makedirs(EMOJI_FOLDER)
                path = os.path.join(EMOJI_FOLDER, f'{emoji_name}.png')
                image.save(path)
                return jsonify({'status': 'success', 'path': path})
            else:
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


        @app.route('/new_message', methods=['POST'])
        def new_message():
            full_message = request.get_json().get('message', '')
            timestamp, pseudo, content = split_message(full_message)
            if content :
                if "vient de suivre !" in content:
                    self.event_manager.detect_event(content)
            self.message_manager.process_message(full_message, timestamp, pseudo, content)
            return 'OK', 200            

        @app.route('/remove_message', methods=['POST'])
        def removed_message():
            full_message = request.get_json().get('message', '')
            timestamp, pseudo, content = split_message(full_message)
            print("To delete = ", timestamp, pseudo, content)
            self.message_manager.delete_message(full_message, content)
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
                time.sleep(5)
        except KeyboardInterrupt:
            print("Script interrompu par l'utilisateur.")
        finally:
            self.driver.quit()



app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

notifier = Scrapper(socketio)
notifier.run()
