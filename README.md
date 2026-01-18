# 🎙️ V2T 2.0 - Voice to Text

<div align="center">

**Transcription vocale intelligente avec interface moderne**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/UI-PyQt6-41CD52.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

*Application élégante pour transcrire votre voix en texte avec un design futuriste violet/noir*

</div>

---

## ✨ Nouveautés V2.0

| Fonctionnalité | Description |
|----------------|-------------|
| 🎨 **UI Premium** | Design moderne avec thème violet/noir et animations fluides |
| 📊 **Waveform** | Visualisation audio temps réel avec gradient violet |
| 🌐 **Mode Online** | Transcription rapide via Groq Whisper API |
| 💻 **Mode Offline** | Transcription locale avec faster-whisper (modèle base) |
| 📝 **Historique** | Sauvegarde et consultation de toutes vos transcriptions |
| ⌨️ **Hotkey Global** | Raccourci clavier personnalisable (F8 par défaut) |
| 📋 **Auto-Paste** | Le texte est automatiquement collé dans votre application |

---

## 🖼️ Aperçu

L'interface suit un design futuriste avec :
- Fond sombre `#0D0D0D`
- Accents violets `#8B5CF6` à `#A855F7`
- Bouton micro animé avec effet glow pulsant
- Visualisation audio en barres verticales
- Cartes avec bordures lumineuses

---

## 📋 Prérequis

- **Python 3.10+**
- **Windows 10/11**
- **Microphone** fonctionnel
- **Clé API Groq** (gratuite) pour le mode online
- **GPU NVIDIA** (optionnel, pour accélérer le mode offline)

---

## 🚀 Installation

### 1. Cloner le projet

```bash
git clone https://github.com/qurnt1/V2T.git
cd V2T
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
venv\Scripts\activate
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

### Navigation

| Page | Description |
|------|-------------|
| 🏠 **Accueil** | Bouton micro et waveform |
| 📝 **Transcription** | Animation pendant le traitement |
| 📂 **Historique** | Toutes vos transcriptions sauvegardées |
| ⚙️ **Paramètres** | Configuration de l'app |

---

## ⚙️ Configuration

### Paramètres disponibles

| Option | Description | Défaut |
|--------|-------------|--------|
| 🎙️ **Microphone** | Appareil audio | Auto-détection |
| 🌍 **Langue** | FR, EN, ES, DE, IT, PT, JA, ZH | Français |
| 🔑 **Clé API** | Clé Groq pour mode online | - |
| ⌨️ **Raccourci** | Touche pour enregistrer | F8 |
| 🤖 **Mode** | Online (Groq) ou Offline (Whisper) | Online |
| 📋 **Auto-Paste** | Coller automatiquement | Activé |
| 🔊 **Sons** | Feedback sonore | Activé |

---

## 🏗️ Architecture

```
V2T/
├── main.py                 # Point d'entrée
├── requirements.txt        # Dépendances
├── .env                    # Clé API (non versionné)
│
├── src/
│   ├── app.py              # Application principale
│   │
│   ├── core/               # Logique métier
│   │   ├── audio_recorder.py
│   │   ├── groq_transcriber.py
│   │   ├── whisper_transcriber.py
│   │   └── hotkey_manager.py
│   │
│   ├── services/           # Services
│   │   ├── settings.py
│   │   ├── storage.py
│   │   └── tray_icon.py
│   │
│   ├── ui/                 # Interface
│   │   ├── main_window.py
│   │   ├── pages/
│   │   ├── widgets/
│   │   └── styles/
│   │
│   └── utils/              # Utilitaires
│       └── constants.py
│
└── data/
    ├── settings.json       # Configuration
    └── transcripts.db      # Historique (SQLite)
```

---

## 📦 Dépendances Principales

| Package | Usage |
|---------|-------|
| **PyQt6** | Interface graphique moderne |
| **sounddevice** | Capture audio (remplace PyAudio) |
| **numpy/scipy** | Traitement signal pour waveform |
| **groq** | API transcription online |
| **faster-whisper** | Transcription offline locale |
| **keyboard** | Hotkey global |
| **peewee** | ORM SQLite pour l'historique |

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

**V2T 2.0** - Fait avec ❤️ par qurnt1

</div>
