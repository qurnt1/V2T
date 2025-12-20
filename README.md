# 🎙️ V2T - Voice to Text

<div align="center">

**Transcription vocale en temps réel avec IA**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)](https://github.com)

*Une application légère et élégante pour transcrire votre voix en texte avec un simple raccourci clavier*

</div>

---

## ✨ Caractéristiques

- 🎯 **Hotkey personnalisable** - Contrôlez l'enregistrement avec votre touche préférée (F8 par défaut)
- 🤖 **IA Groq Whisper** - Transcription précise et multilingue grâce au modèle Whisper Large V3
- 🌐 **Multilingue** - Support de 8 langues (FR, EN, ES, DE, IT, PT, JA, ZH)
- 📌 **Insertion automatique** - Le texte est collé directement dans votre application
- 👁️ **Overlay visuel** - Animation de pulsation pour visualiser le niveau sonore
- 🔧 **Interface de configuration** - UI moderne et intuitive avec Flet
- 🔔 **Notifications système** - Feedback visuel et sonore
- 🎨 **Customisable** - Icône personnalisée et image de skin
- 🖥️ **Tray Icon** - Contrôle depuis la barre des tâches Windows

---

## 📋 Prérequis

- **Python 3.8+**
- **Windows 10/11** (compatible avec la barre des tâches)
- **Microphone** fonctionnel
- **Clé API Groq** (gratuite sur [console.groq.com](https://console.groq.com))

---

## 🚀 Installation

### 1. Cloner ou télécharger le projet

```bash
git clone https://github.com/qurnt1/V2T.git
cd V2T
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
key_groq_api = "votre_clé_api_groq_ici"
```

> 💡 Obtenez votre clé API gratuite sur [console.groq.com](https://console.groq.com)

### 5. Ajouter les ressources optionnelles

Pour personnaliser l'application, ajoutez ces fichiers dans le dossier `data/` :

```
data/
├── icon.ico          # Icône pour la barre des tâches
└── skin.png          # Image d'overlay (recommandé: 256x256)
```

---

## 📖 Utilisation

### Lancer l'application

```bash
python main.py
```

L'application se lance en mode service et ajoute une icône dans la barre des tâches.

### Mode Service (Arrière-plan)

1. L'app écoute votre hotkey (F8 par défaut)
2. **Appuyez sur F8** pour démarrer l'enregistrement
3. Un son "pop" et un overlay visuel confirment le démarrage
4. Parlez dans votre microphone
5. **Appuyez à nouveau sur F8** pour terminer
6. Le texte transcrit est automatiquement collé

### Paramètres

Cliquez sur **"Paramètres"** dans le tray icon pour accéder à la configuration :

| Paramètre | Description | Défaut |
|-----------|-------------|--------|
| 🎙️ **Microphone** | Sélectionnez votre appareil audio | Auto-détection |
| 🌍 **Langue** | Langue de transcription | Français |
| 🔑 **API Groq** | Clé d'authentification API | - |
| ⌨️ **Hotkey** | Touche pour enregistrer | F8 |
| 🤖 **Groq Whisper** | Activer/désactiver l'IA | Activé |
| 🔊 **Effets sonores** | Sons de début/fin | Activé |

---

## 🔧 Configuration Avancée

### Fichier `settings.json`

Les paramètres sont sauvegardés dans `data/settings.json` :

```json
{
    "mic_index": null,
    "use_ai": true,
    "hotkey": "F8",
    "language": "fr",
    "sound_enabled": true
}
```

### Fichier `.env`

```env
key_groq_api = "gsk_xxxxxxxxxxxxx"
```

> ⚠️ **N'exposez jamais votre clé API** - Ne la pushez pas sur GitHub !

---

## 🎯 Cas d'usage

- ✍️ **Rédaction** - Dictez vos emails, documents, messages
- 📝 **Prise de notes** - Prenez des notes rapidement sans frapper au clavier
- 🎮 **Gaming** - Commandes vocales dans vos jeux
- 🔍 **Recherche** - Dictez vos requêtes sans les taper
- ♿ **Accessibilité** - Alternative au clavier pour les utilisateurs ayant des besoins particuliers

---

## 🏗️ Architecture

```
V2T/
├── main.py                 # Application principale
├── requirements.txt        # Dépendances Python
├── .env                    # Variables d'environnement (non versionné)
├── README.md              # Ce fichier
└── data/
    ├── settings.json      # Paramètres de l'app
    ├── pop.mp3            # Son d'enregistrement
    ├── icon.ico           # Icône de la tray
    └── skin.png           # Image d'overlay
```

### Modules principaux

- **Flet** - Interface de configuration moderne
- **SpeechRecognition** - Capture et traitement audio
- **PyAudio** - Gestion du microphone
- **Groq** - API de transcription IA
- **keyboard** - Détection hotkey global
- **pystray** - Icône système
- **pyperclip** - Gestion du presse-papier
- **pygame** - Lecture des sons
- **Tkinter** - Overlay visuel transparent

---

## ⚙️ Dépannage

### L'app ne démarre pas

1. Vérifiez que Python 3.8+ est installé
2. Activez votre environnement virtuel
3. Vérifiez l'installation des dépendances : `pip list`

### Le microphone ne fonctionne pas

1. Vérifiez que Windows a accès à votre micro
2. Testez votre micro dans Paramètres > Son
3. Sélectionnez le bon appareil dans les Paramètres V2T

### Pas d'IA - Fallback Google Speech

Si Groq ne fonctionne pas :
- Vérifiez votre clé API
- Vérifiez votre connexion internet
- L'app utilise Google Speech en fallback automatique

### L'overlay ne s'affiche pas

- Assurez-vous que `skin.png` est présent dans `data/`
- Ou utilisez le fallback (cercle rouge)

### Texte ne se colle pas

1. Vérifiez que l'app a les permissions système
2. Testez le presse-papier : `Ctrl+V` manuellement
3. Vérifiez que l'app cible est active

---

## 📦 Dépendances

Voir [requirements.txt](requirements.txt) pour la liste complète.

```
flet>=0.20.0
SpeechRecognition>=3.10.0
PyAudio>=0.2.11
keyboard>=0.13.0
groq>=0.4.0
pyperclip>=1.8.2
pystray>=0.19.0
Pillow>=10.0.0
pygame>=2.1.0
plyer>=2.1.0
python-dotenv>=1.0.0
```

---

## 🎨 Personnalisation

### Changer l'icône

Remplacez `data/icon.ico` par votre propre fichier `.ico`

### Ajouter un skin personnalisé

Créez une image `skin.png` (format PNG avec transparence, ~256x256px) dans `data/`

### Modifier les couleurs

Éditez la classe `AppColors` dans [main.py](main.py#L662) :

```python
class AppColors:
    BG = "#121212"      # Fond noir
    ACCENT = "#00D2FC"  # Accent cyan
```

---

## 🤝 Contribution

Les contributions sont bienvenues !

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📝 Licence

Ce projet est sous licence MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## 🔐 Sécurité

⚠️ **Important** :
- Ne commettez jamais votre clé API dans le dépôt
- Utilisez `.env` et `.gitignore` pour les secrets
- Régénérez votre clé si elle a été exposée

---

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifiez la section [Dépannage](#-dépannage)
2. Consultez les [Issues existantes](https://github.com)
3. Ouvrez une nouvelle issue avec :
   - Description du problème
   - Étapes pour reproduire
   - Logs d'erreur si applicable

---

## 🚀 Roadmap

- [ ] Support Mac/Linux
- [ ] Interface web alternative
- [ ] Historique des transcriptions
- [ ] Exportation en PDF/DOCX
- [ ] Intégration avec des services cloud
- [ ] Mode dictionnaire (corrections orthographiques)
- [ ] Support des plugins

---

<div align="center">

**[⬆ Retour au top](#️-v2t---voice-to-text)**

Fait avec ❤️ par [Auteur]

</div>
