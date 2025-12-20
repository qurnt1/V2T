import flet as ft
from flet import Icons
import speech_recognition as sr
import keyboard
import pyaudio
import time
import os
import sys
import subprocess
import pyperclip
import threading
import json
import audioop
import tkinter as tk
from pystray import Icon as TrayIcon, MenuItem as Item
from PIL import Image, ImageDraw, ImageTk
from dotenv import load_dotenv
from groq import Groq
import tempfile
import wave
import pygame
import warnings
from plyer import notification

# --- Configuration des avertissements ---
# Ignore les avertissements liés à pkg_resources souvent présents avec certaines libs
warnings.filterwarnings("ignore", message=r"pkg_resources is deprecated as an API.*")

# ==========================================
# 1. CONSTANTES & CHEMINS
# ==========================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Création du dossier de données s'il n'existe pas
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Chemins des fichiers ressources
ENV_PATH = os.path.join(BASE_DIR, ".env")
SOUND_FILE = os.path.join(DATA_DIR, "pop.mp3")
ICON_FILE = os.path.join(DATA_DIR, "icon.ico")
CONFIG_FILE = os.path.join(DATA_DIR, "settings.json")
SKIN_FILE = os.path.join(DATA_DIR, "skin.png")

# Configuration Audio (Constantes PyAudio)
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Variables globales d'état
APP_RUNNING = True
IS_RECORDING = False
CURRENT_RMS = 0
SETTINGS_LOCK = threading.Lock()

# Paramètres par défaut
SETTINGS = {
    "mic_index": None,
    "use_ai": True,
    "hotkey": "F8",
    "language": "fr",
    "sound_enabled": True
}

# Mapping pour la reconnaissance Google (fallback)
GOOGLE_LANG_MAP = {
    "fr": "fr-FR", "en": "en-US", "es": "es-ES", 
    "de": "de-DE", "it": "it-IT", "pt": "pt-PT", 
    "ja": "ja-JP", "zh": "zh-CN"
}

# Chargement des variables d'environnement
load_dotenv(ENV_PATH, override=True)
GROQ_API_KEY = os.getenv("key_groq_api")


# ==========================================
# 2. GESTION DES PARAMÈTRES (I/O)
# ==========================================

def normalize_lang_code(code):
    """Normalise le code langue (ex: fr-FR -> fr)."""
    if not code:
        return "fr"
    return str(code).strip().split("-")[0].split("_")[0].lower() or "fr"

def load_settings():
    """Charge les paramètres depuis le fichier JSON."""
    global SETTINGS
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            with SETTINGS_LOCK:
                SETTINGS.update(data)
                # Nettoyage d'anciennes clés obsolètes si nécessaire
                if "ai_cleanup" in SETTINGS:
                    del SETTINGS["ai_cleanup"]
        except Exception:
            pass
            
    # Assurance que la langue est toujours définie
    with SETTINGS_LOCK:
        SETTINGS["language"] = normalize_lang_code(SETTINGS.get("language", "fr"))

def save_settings():
    """Sauvegarde les paramètres actuels dans le fichier JSON."""
    try:
        with SETTINGS_LOCK:
            payload = dict(SETTINGS)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
    except Exception:
        pass

def update_api_key(new_key):
    """Met à jour la clé API dans le fichier .env et en mémoire."""
    global GROQ_API_KEY
    GROQ_API_KEY = new_key
    try:
        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.write(f'key_groq_api = "{new_key}"')
    except Exception:
        pass

# Chargement initial
load_settings()


# ==========================================
# 3. FONCTIONS UTILITAIRES & AUDIO
# ==========================================

def send_notification(title, message):
    """Envoie une notification système native."""
    try:
        app_icon = ICON_FILE if os.path.exists(ICON_FILE) else None
        notification.notify(
            title=title, 
            message=message, 
            app_name="V2T Skin", 
            app_icon=app_icon, 
            timeout=3
        )
    except Exception:
        pass

# --- Gestion Pygame (Sons) ---
_PYGAME_INIT_DONE = False
_PYGAME_LOCK = threading.Lock()

def _ensure_pygame_audio():
    """Initialise le mixer Pygame de manière thread-safe."""
    global _PYGAME_INIT_DONE
    with _PYGAME_LOCK:
        if _PYGAME_INIT_DONE:
            return
        try:
            pygame.mixer.init()
            _PYGAME_INIT_DONE = True
        except Exception:
            _PYGAME_INIT_DONE = False

def play_sound(duration_sec=0.10):
    """Joue un petit son 'pop' pour indiquer le début/fin d'enregistrement."""
    with SETTINGS_LOCK:
        if not SETTINGS.get("sound_enabled", True):
            return
            
    if not os.path.exists(SOUND_FILE):
        return

    def _run():
        _ensure_pygame_audio()
        if not _PYGAME_INIT_DONE:
            return
        try:
            pygame.mixer.music.load(SOUND_FILE)
            pygame.mixer.music.set_volume(0.05)
            pygame.mixer.music.play()
            time.sleep(max(0.01, float(duration_sec)))
            pygame.mixer.music.stop()
        except Exception:
            pass
            
    threading.Thread(target=_run, daemon=True).start()

# --- Gestion PyAudio (Micro) ---

def get_microphones():
    """Récupère la liste des microphones disponibles."""
    p = pyaudio.PyAudio()
    mics = []
    try:
        info = p.get_host_api_info_by_index(0)
        for i in range(info.get("deviceCount")):
            di = p.get_device_info_by_host_api_device_index(0, i)
            if di.get("maxInputChannels", 0) > 0:
                try:
                    name = di.get('name').encode("latin-1").decode("utf-8")
                except Exception:
                    name = di.get('name')
                mics.append(f"{i}: {name}")
        return mics
    finally:
        try:
            p.terminate()
        except Exception:
            pass

def open_input_stream(pa, idx, frames_per_buffer):
    """Ouvre un flux audio en entrée sur le device spécifié."""
    kwargs = dict(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=RATE, 
        input=True, 
        frames_per_buffer=frames_per_buffer
    )
    if idx is not None:
        kwargs["input_device_index"] = idx
    return pa.open(**kwargs)


# ==========================================
# 4. TRANSCRIPTION (Whisper / Google)
# ==========================================

def transcribe_with_groq_whisper(audio_data):
    """Envoie l'audio à l'API Groq (modèle Whisper Large V3)."""
    if not GROQ_API_KEY:
        return None
        
    tmp_filename = None
    pa = pyaudio.PyAudio()
    
    try:
        # Conversion des données raw en fichier WAV temporaire
        sample_width = pa.get_sample_size(FORMAT)
        raw = audio_data.get_raw_data(convert_rate=RATE, convert_width=sample_width)
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
            tmp_filename = tmp_file.name
            
        with wave.open(tmp_filename, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(RATE)
            wf.writeframes(raw)
            
        with SETTINGS_LOCK:
            groq_lang = normalize_lang_code(SETTINGS.get("language", "fr"))
            
        client = Groq(api_key=GROQ_API_KEY)
        
        with open(tmp_filename, "rb") as file:
            trans = client.audio.transcriptions.create(
                file=(tmp_filename, file.read()), 
                model="whisper-large-v3",
                temperature=0.0, 
                language=groq_lang, 
                response_format="text"
            )
            
        # Nettoyage du fichier temporaire
        try:
            os.remove(tmp_filename)
        except OSError:
            pass
            
        return trans.strip()
        
    except Exception as e:
        print(f"Erreur Whisper: {e}")
        try: 
            if tmp_filename:
                os.remove(tmp_filename)
        except OSError:
            pass
        return None
        
    finally:
        try:
            pa.terminate()
        except Exception:
            pass

def paste_text(text):
    """Copie le texte dans le presse-papier et simule CTRL+V."""
    if text:
        pyperclip.copy(text)
        time.sleep(0.05)
        keyboard.press_and_release("ctrl+v")
        play_sound(0.10)


# ==========================================
# 5. OVERLAY (SKIN VISUEL)
# ==========================================

class StatusOverlay(threading.Thread):
    """
    Fenêtre Tkinter transparente qui affiche une animation (pulsation)
    lorsque l'enregistrement est en cours.
    """
    def __init__(self):
        super().__init__(daemon=True)
        self.root = None
        self.max_rms = 3000
        self.base_size = 100
        self.current_vol = 0.0
        self.skin_image = None
        self.tk_image = None
        self.has_skin = False
        # Couleur très sombre pour la transparence (évite les halos blancs sur Windows)
        self.transparent_key = "#000001" 

    def load_skin(self):
        """Charge l'image du skin (skin.png) si elle existe."""
        if os.path.exists(SKIN_FILE):
            try:
                img = Image.open(SKIN_FILE).convert("RGBA")
                max_anim_size = int(self.base_size * 1.5)
                img.thumbnail((max_anim_size, max_anim_size), Image.Resampling.LANCZOS)
                self.skin_image = img
                self.has_skin = True
            except Exception as e:
                print(f"Erreur skin: {e}")
                self.has_skin = False
        else:
            self.has_skin = False

    def run(self):
        """Initialise la fenêtre Tkinter."""
        self.load_skin()
        self.root = tk.Tk()
        self.root.geometry(f"{self.base_size}x{self.base_size}+50+50")
        
        # Configuration fenêtre sans bordure et toujours au-dessus
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg=self.transparent_key)
        
        # Définition de la couleur de transparence
        self.root.wm_attributes("-transparentcolor", self.transparent_key)
        
        self.canvas = tk.Canvas(
            self.root, 
            width=self.base_size, 
            height=self.base_size, 
            bg=self.transparent_key, 
            highlightthickness=0
        )
        self.canvas.pack()

        if not self.has_skin:
            # Fallback : Un simple cercle rouge si pas d'image
            cx, cy = self.base_size // 2, self.base_size // 2
            self.fallback_id = self.canvas.create_oval(cx-20, cy-20, cx+20, cy+20, fill="red", outline="white")
        else:
            # Placeholder pour l'image
            self.image_id = self.canvas.create_image(self.base_size // 2, self.base_size // 2, image=None)

        self.root.withdraw() # Caché par défaut
        self.animate()
        self.root.mainloop()

    def animate(self):
        """Boucle d'animation : met à jour la taille de l'image selon le volume."""
        if not APP_RUNNING:
            try:
                self.root.destroy()
            except Exception:
                pass
            return

        if IS_RECORDING:
            self.root.deiconify() # Afficher la fenêtre
            
            # Calcul du volume lissé pour l'animation
            target_vol = min(CURRENT_RMS, self.max_rms) / self.max_rms
            self.current_vol += (target_vol - self.current_vol) * 0.3
            vol = self.current_vol

            if self.has_skin and self.skin_image:
                # Animation de pulsation (scale)
                scale = 0.8 + (vol * 0.2)
                target_size = int(self.base_size * scale)
                
                # Redimensionnement de l'image
                resized_img = self.skin_image.resize((target_size, target_size), Image.Resampling.BILINEAR)
                
                # NOTE: J'ai supprimé ici la partie qui dessinait le texte "REC"
                
                self.tk_image = ImageTk.PhotoImage(resized_img)
                self.canvas.itemconfig(self.image_id, image=self.tk_image)
            
            else:
                # Mode sans skin (Cercle qui grossit)
                r = 20 + (vol * 10)
                cx, cy = self.base_size // 2, self.base_size // 2
                self.canvas.coords(self.fallback_id, cx-r, cy-r, cx+r, cy+r)
        else:
            self.root.withdraw()
            self.current_vol = 0.0

        # Rappel de la fonction dans 30ms (environ 33 FPS)
        self.root.after(30, self.animate)


# ==========================================
# 6. LOGIQUE PRINCIPALE (SERVICE MODE)
# ==========================================

def run_service_mode():
    """Mode 'Service' : tourne en arrière-plan, gère le hotkey et l'audio."""
    global APP_RUNNING, IS_RECORDING, CURRENT_RMS
    
    # Lancement de l'overlay visuel
    overlay = StatusOverlay()
    overlay.start()

    def settings_watcher():
        """Surveille les modifications du fichier settings.json."""
        last_mtime = None
        while APP_RUNNING:
            try:
                if os.path.exists(CONFIG_FILE):
                    mtime = os.path.getmtime(CONFIG_FILE)
                    if last_mtime is None or mtime != last_mtime:
                        last_mtime = mtime
                        load_settings()
            except Exception:
                pass
            time.sleep(0.5)
            
    threading.Thread(target=settings_watcher, daemon=True).start()

    def hotkey_loop():
        """Boucle principale de détection de touche et d'enregistrement."""
        global IS_RECORDING, APP_RUNNING, CURRENT_RMS
        
        r = sr.Recognizer()
        pa = pyaudio.PyAudio()
        rec_stream = None
        frames = []
        is_rec = False
        prev_pressed = False

        def close_rec():
            nonlocal rec_stream
            try:
                if rec_stream:
                    rec_stream.stop_stream()
                    rec_stream.close()
            except Exception:
                pass
            rec_stream = None

        while APP_RUNNING:
            with SETTINGS_LOCK:
                hk = SETTINGS.get("hotkey", "F8")
                use_ai = SETTINGS.get("use_ai", True)
                mic_idx = SETTINGS.get("mic_index")
                lang = SETTINGS.get("language", "fr")

            # Détection de la touche
            try:
                pressed = keyboard.is_pressed(hk)
            except Exception:
                pressed = False

            # Logique Toggle (Appui pour ON, Appui pour OFF)
            # On détecte le "Front Montant" (quand on vient d'appuyer)
            if pressed and not prev_pressed:
                if not is_rec:
                    # DÉBUT ENREGISTREMENT
                    is_rec = True
                    IS_RECORDING = True
                    CURRENT_RMS = 0
                    play_sound(0.10)
                    frames = []
                    try:
                        rec_stream = open_input_stream(pa, mic_idx, CHUNK)
                    except Exception:
                        # Fallback sur micro par défaut si erreur
                        rec_stream = open_input_stream(pa, None, CHUNK)
                else:
                    # FIN ENREGISTREMENT
                    is_rec = False
                    IS_RECORDING = False
                    CURRENT_RMS = 0
                    play_sound(0.10)
                    close_rec()
                    
                    if frames:
                        audio = sr.AudioData(b"".join(frames), RATE, 2)
                        txt = ""
                        
                        if use_ai and GROQ_API_KEY:
                            txt = transcribe_with_groq_whisper(audio)
                        else:
                            # Fallback Google Speech
                            try:
                                code = normalize_lang_code(lang)
                                google_lang = GOOGLE_LANG_MAP.get(code, "fr-FR")
                                txt = r.recognize_google(audio, language=google_lang)
                            except Exception:
                                pass
                        
                        if txt:
                            paste_text(txt)

            prev_pressed = pressed

            # Capture audio si en cours
            if is_rec and rec_stream:
                try:
                    data = rec_stream.read(CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    CURRENT_RMS = audioop.rms(data, 2)
                except Exception:
                    pass
            else:
                CURRENT_RMS = 0
                
            time.sleep(0.01)

        # Nettoyage à la fermeture
        close_rec()
        try:
            pa.terminate()
        except Exception:
            pass

    threading.Thread(target=hotkey_loop, daemon=True).start()

    def launch_settings_ui():
        """Lance l'interface de configuration dans un processus séparé."""
        try:
            cmd = [sys.executable, os.path.abspath(__file__), "--settings"]
            if os.name == "nt":
                # DETACHED_PROCESS flag pour Windows
                subprocess.Popen(cmd, creationflags=0x08000000, cwd=BASE_DIR)
            else:
                subprocess.Popen(cmd, cwd=BASE_DIR)
        except Exception:
            pass

    def tray_process():
        """Gère l'icône dans la barre des tâches (System Tray)."""
        def create_image():
            if os.path.exists(ICON_FILE):
                try:
                    return Image.open(ICON_FILE)
                except Exception:
                    pass
            # Image par défaut (cercle vert)
            img = Image.new("RGB", (64, 64), (0, 0, 0))
            d = ImageDraw.Draw(img)
            d.ellipse((10, 10, 54, 54), fill=(0, 255, 0))
            return img

        def on_quit(icon, item):
            global APP_RUNNING
            APP_RUNNING = False
            send_notification("Au revoir", "V2T est bien fermé")
            time.sleep(1.5)
            icon.stop()
            os._exit(0)

        icon = TrayIcon(
            "V2T_App", 
            create_image(), 
            "V2T Skin", 
            menu=(
                Item("Paramètres", lambda i, It: launch_settings_ui(), default=True),
                Item("Quitter", on_quit),
            )
        )
        icon.run()

    threading.Thread(target=tray_process, daemon=True).start()
    
    time.sleep(0.5)
    send_notification("V2T Démarré", "V2T est prêt à être utilisé")
    
    # Maintien du thread principal en vie
    while True:
        time.sleep(1)


# ==========================================
# 7. INTERFACE PARAMÈTRES (FLET UI)
# ==========================================

class AppColors:
    BG = "#121212"
    ACCENT = "#00D2FC"

def run_settings_ui():
    """Lance l'interface utilisateur Flet pour les réglages."""
    load_settings()

    def main(page: ft.Page):
        page.title = "Paramètres V2T"
        page.bgcolor = AppColors.BG
        page.padding = 15
        
        try:
            if page.window:
                page.window.icon = ICON_FILE
                page.window.width = 320
                page.window.height = 700
                page.window.resizable = False
        except Exception:
            pass
            
        page.fonts = {"Poppins": "https://fonts.gstatic.com/s/poppins/v20/pxiByp8kv8JHgFVrLGT9Z1xlFQ.woff2"}
        page.theme = ft.Theme(font_family="Poppins")

        # --- Composants UI ---
        
        header = ft.Row(
            [ft.Icon(Icons.SETTINGS, color=AppColors.ACCENT, size=20), 
             ft.Text("V2T Settings", weight="bold", size=14, color="white")], 
            alignment="center"
        )
        
        mic_bar = ft.ProgressBar(
            width=280, height=8, value=0.0, 
            color=AppColors.ACCENT, bgcolor="#333333", 
            bar_height=8, border_radius=4
        )

        # Dropdown Microphones
        mics = get_microphones()
        with SETTINGS_LOCK:
            cur_idx = SETTINGS.get("mic_index")
            
        cur_val = "Par défaut"
        if cur_idx is not None:
            for m in mics:
                if m.startswith(f"{cur_idx}:"):
                    cur_val = m
                    break
        
        def update_mic(val):
            with SETTINGS_LOCK:
                SETTINGS["mic_index"] = None if val == "Par défaut" else int(val.split(":")[0])
            save_settings()
            
        mic_drop = ft.Dropdown(
            options=[ft.dropdown.Option("Par défaut")] + [ft.dropdown.Option(m) for m in mics], 
            value=cur_val, text_size=11, border_color="#333333", 
            bgcolor="#111111", color="white", 
            on_change=lambda e: update_mic(mic_drop.value)
        )

        # Champ API Key
        api_field = ft.TextField(
            value=GROQ_API_KEY or "", password=True, 
            can_reveal_password=True, text_size=11, 
            border_color="#333333", bgcolor="#111111", 
            color="white", hint_text="Clé API Groq"
        )
        
        def save_api(e):
            update_api_key(api_field.value)
            btn_save.text = "Sauvegardé !"
            page.update()
            time.sleep(0.8)
            btn_save.text = "Sauvegarder"
            page.update()
            
        btn_save = ft.ElevatedButton(
            "Sauvegarder", on_click=save_api, 
            bgcolor="#333333", color="white", width=280
        )

        # Dropdown Langue
        langs = {
            "Français": "fr", "English": "en", "Español": "es", 
            "Deutsch": "de", "Italiano": "it", "Português": "pt", 
            "日本語": "ja", "中文": "zh"
        }
        with SETTINGS_LOCK:
            cur_code = SETTINGS.get("language", "fr")
        cur_lbl = next((k for k, v in langs.items() if v == cur_code), "Français")
        
        def update_lang(lbl):
            with SETTINGS_LOCK:
                SETTINGS["language"] = langs.get(lbl, "fr")
            save_settings()
            
        lang_drop = ft.Dropdown(
            label="Langue", 
            options=[ft.dropdown.Option(k) for k in langs], 
            value=cur_lbl, text_size=11, border_color="#333333", 
            bgcolor="#111111", color="white", 
            on_change=lambda e: update_lang(lang_drop.value)
        )

        # Bouton Hotkey
        with SETTINGS_LOCK:
            hk = SETTINGS.get("hotkey", "F8")
        hk_btn = ft.ElevatedButton(
            text=f"Touche: {hk}", bgcolor=AppColors.ACCENT, 
            color="black", width=280
        )
        
        def chg_hotkey(e):
            hk_btn.text = "Appuyez..."
            hk_btn.bgcolor = "#FF0044"
            page.update()
            time.sleep(0.2)
            try:
                k = keyboard.read_hotkey(suppress=False)
                with SETTINGS_LOCK:
                    SETTINGS["hotkey"] = k
                save_settings()
                hk_btn.text = f"Touche: {k}"
                hk_btn.bgcolor = AppColors.ACCENT
                page.update()
            except Exception:
                pass
        hk_btn.on_click = chg_hotkey

        # Switchs
        with SETTINGS_LOCK:
            ai_v = bool(SETTINGS.get("use_ai", True))
            snd_v = bool(SETTINGS.get("sound_enabled", True))
            
        def upd_bool(key, val):
            with SETTINGS_LOCK:
                SETTINGS[key] = val
            save_settings()
            
        sw_ai = ft.Switch(
            label="Utiliser Groq Whisper", value=ai_v, 
            active_color=AppColors.ACCENT, 
            on_change=lambda e: upd_bool("use_ai", sw_ai.value)
        )
        sw_snd = ft.Switch(
            label="Effets sonores", value=snd_v, 
            active_color=AppColors.ACCENT, 
            on_change=lambda e: upd_bool("sound_enabled", sw_snd.value)
        )

        # Ajout des éléments à la page
        page.add(
            header, 
            ft.Divider(color="#333333"), 
            ft.Text("Test Micro (Visuel)", size=10, color="grey"), mic_bar, ft.Container(height=10),
            ft.Text("Microphone", size=10, color="grey"), mic_drop, ft.Container(height=5),
            ft.Text("Langue", size=10, color="grey"), lang_drop, ft.Container(height=5),
            ft.Text("API Groq", size=10, color="grey"), api_field, btn_save, ft.Container(height=10),
            hk_btn, ft.Container(height=10),
            sw_ai, sw_snd
        )

        # Boucle de mise à jour de la barre de volume (Test micro)
        def ui_loop():
            pa = pyaudio.PyAudio()
            stream = None
            last_mic = object()
            MAX_RMS = 2500
            
            while True:
                try:
                    with SETTINGS_LOCK:
                        idx = SETTINGS.get("mic_index")
                        
                    # Recharger le flux si le micro change
                    if stream is None or idx != last_mic:
                        if stream:
                            stream.stop_stream()
                            stream.close()
                        stream = open_input_stream(pa, idx, 1024)
                        last_mic = idx
                        
                    data = stream.read(1024, exception_on_overflow=False)
                    rms = audioop.rms(data, 2)
                    val = min(rms, MAX_RMS) / MAX_RMS
                    if val < 0.02: val = 0.0
                    
                    mic_bar.value = val
                    page.update()
                except Exception:
                    time.sleep(0.5)
                time.sleep(0.05)
                
        threading.Thread(target=ui_loop, daemon=True).start()

    try:
        ft.app(target=main)
    except Exception:
        ft.app(target=main)

# ==========================================
# 8. POINT D'ENTRÉE
# ==========================================
if __name__ == "__main__":
    if "--settings" in sys.argv:
        run_settings_ui()
    else:
        run_service_mode()