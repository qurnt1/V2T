# 🎙️ V2T 2.2 - Voice to Text

<div align="center">

**Transcription vocale intelligente avec interface moderne**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*Application desktop élégante pour transcrire votre voix en texte avec un design futuriste violet/noir*

</div>

---

## 🆕 Nouveautés v2.2

| Nouveauté | Description |
|-----------|-------------|
| 🧠 **Gestionnaire Whisper** | Téléchargez, installez et désinstallez les modèles (Tiny, Base, Small, Medium, Large) directement depuis les paramètres |
| 📊 **Barre de Progression** | Suivi précis du téléchargement des modèles avec pourcentage et feedback visuel |
| 🔔 **Notification Exit** | Notification native "V2T Fermé" lors de la fermeture de l'application |
| 🛠️ **Correctifs** | Suppression des avertissements "Symlinks" sur Windows et corrections UI |
| 🧵 **Threading corrigé** | Plus d'erreurs "Timers cannot be stopped from another thread" |
| 🏠 **UX simplifiée** | Restez sur la page principale pendant la transcription (plus de popup) |
| ✨ **Correction IA** | Corrigez l'orthographe/grammaire via l'IA Groq directement depuis l'historique |

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 🎨 **UI Premium** | Design moderne thème violet/noir avec animations fluides |
| 📊 **Waveform** | Visualisation audio temps réel avec gradient violet |
| 🌐 **Mode Online** | Transcription ultra-rapide via Groq Whisper API |
| 💻 **Mode Offline** | Transcription locale avec faster-whisper (GPU/CPU) |
| 📝 **Historique** | Sauvegarde et consultation de toutes vos transcriptions |
| ⌨️ **Hotkey Global** | Raccourci clavier personnalisable (F8 par défaut) |
| 📋 **Auto-Paste** | Le texte est automatiquement collé dans votre application |
| 🔔 **System Tray** | L'app reste en arrière-plan, accessible depuis la barre des tâches |
| 🎚️ **Toggles visuels** | Switches vert/rouge intuitifs pour ON/OFF |

---

## 🖼️ Interface

L'interface suit un design futuriste avec :
- Fond sombre `#0D0D0D`
- Accents violets `#8B5CF6` à `#A855F7`
- Bouton micro animé avec effet glow pulsant
- Visualisation audio en barres verticales
- Cartes avec bordures lumineuses au survol

---

## 📋 Prérequis

- **Python 3.10+**
- **Windows 10/11**
- **Microphone** fonctionnel
- **Clé API Groq** (gratuite) pour le mode online
- **GPU NVIDIA** (optionnel, accélère le mode offline)

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/qurnt1/V2T.git
cd V2T
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la clé API Groq

Créez un fichier `.env` à la racine :

```env
key_groq_api = "votre_clé_api_groq"
```

> 💡 Obtenez votre clé gratuite sur [console.groq.com](https://console.groq.com)

---

## 📖 Utilisation

### Lancer l'application

```bash
python main.py
```

### Enregistrer et transcrire

1. **Appuyez sur F8** (ou cliquez sur le micro) pour démarrer
2. Parlez dans votre microphone
3. **Appuyez à nouveau sur F8** pour arrêter
4. Le texte est transcrit et collé automatiquement !

### System Tray

- **Fermer (X)** → L'app se cache dans la barre des tâches
- **Clic droit sur l'icône** → Menu avec options
- **Afficher V2T** → Réouvre la fenêtre
- **Quitter** → Ferme complètement l'application

### Pages

| Page | Description |
|------|-------------|
| 🏠 **Accueil** | Bouton micro, waveform et statut de transcription |
| 📂 **Historique** | Transcriptions sauvegardées avec correction IA |
| ⚙️ **Paramètres** | Configuration de l'app |

---

## ⚙️ Configuration

| Option | Description | Défaut |
|--------|-------------|--------|
| **Microphone** | Appareil audio | Auto-détection |
| **Langue** | FR, EN, ES, DE, IT, PT, JA, ZH | Français |
| **Clé API** | Clé Groq pour mode online | - |
| **Raccourci** | Touche pour enregistrer | F8 |
| **Mode** | Online (Groq) ou Offline (Whisper) | Online |
| **Auto-Paste** | Coller automatiquement | ✅ Activé |
| **Sons** | Feedback sonore | ✅ Activé |
| **Arrêt auto** | Arrêter après silence | ❌ Désactivé |

---

## 🏗️ Architecture

```
V2T/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances
├── .env                    # Clé API (non versionné)
│
├── src/
│   ├── app.py              # Application principale + TrayBridge
│   │
│   ├── core/               # Logique métier
│   │   ├── audio_recorder.py
│   │   ├── groq_transcriber.py   # + correct_grammar()
│   │   ├── whisper_transcriber.py
│   │   ├── hotkey_manager.py
│   │   └── transcriber.py
│   │
│   ├── services/           # Services
│   │   ├── settings.py
│   │   ├── storage.py
│   │   └── tray_icon.py
│   │
│   ├── ui/                 # Interface PyQt6
│   │   ├── main_window.py
│   │   ├── pages/
│   │   │   ├── home_page.py
│   │   │   ├── history_page.py
│   │   │   └── settings_page.py
│   │   ├── widgets/
│   │   │   ├── mic_button.py
│   │   │   ├── waveform.py
│   │   │   └── transcript_card.py
│   │   └── styles/
│   │       └── theme.py
│   │
│   └── utils/
│       └── constants.py
│
└── data/
    ├── settings.json       # Configuration utilisateur
    └── transcripts.db      # Historique (SQLite)
```

---

## 📦 Dépendances

| Package | Usage |
|---------|-------|
| **PyQt6** | Interface graphique moderne |
| **sounddevice** | Capture audio |
| **numpy** | Traitement signal pour waveform |
| **groq** | API transcription online + correction IA |
| **faster-whisper** | Transcription offline locale |
| **torch** | Support GPU pour faster-whisper |
| **keyboard** | Hotkey global |
| **pystray** | Icône System Tray |
| **peewee** | ORM SQLite pour l'historique |
| **Pillow** | Génération icône tray |
| **pyperclip** | Copie presse-papier |

---

## 🔧 Mode Offline

Le mode offline utilise `faster-whisper` avec le modèle `base` (~150 MB).

### Premier lancement offline

Le modèle sera téléchargé automatiquement. Cela peut prendre quelques minutes.

### Performance

| Type | Temps (30s audio) |
|------|-------------------|
| **GPU NVIDIA** | ~2-3 secondes |
| **CPU** | ~10-15 secondes |

---

## ⚠️ Dépannage

### L'app ne démarre pas

```bash
pip install --upgrade PyQt6 sounddevice
```

### Erreur audio

1. Vérifiez les permissions microphone Windows
2. Sélectionnez le bon micro dans Paramètres

### Mode offline lent

- Utilisez un GPU NVIDIA avec CUDA
- Ou activez le mode online (plus rapide)

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

---

<div align="center">

**V2T 2.1** - Fait avec ❤️ par qurnt1

</div>
