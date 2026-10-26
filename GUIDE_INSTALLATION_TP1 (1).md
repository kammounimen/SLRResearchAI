# SLRResearchAI — Guide d’installation avant le TP1

Ce guide contient uniquement les installations nécessaires pour préparer l’environnement du TP1.

## 1. Installer les logiciels nécessaires

Installez :

- **Python 3.11 ou une version plus récente, en 64 bits** : <https://www.python.org/downloads/>
- **Git** : <https://git-scm.com/downloads>
- **Visual Studio Code** : <https://code.visualstudio.com/Download>
- un navigateur récent : Firefox, Chrome, Edge ou Safari.

### Vérification sous macOS/Linux

```bash
python3 --version
git --version
```

La version affichée doit être Python 3.11 ou une version plus récente.

### Vérification sous Windows

```powershell
py -3 --version
git --version
```

La version affichée doit être Python 3.11 ou une version plus récente.

## 2. Préparer le dossier d’installation

Conservez les deux fichiers du kit dans un même dossier :

```text
Kit_Installation_Etudiants/
├── GUIDE_INSTALLATION_TP1.md
└── requirements.txt
```

Ouvrez un terminal dans ce dossier.

## 3. Créer l’environnement virtuel

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Si PowerShell bloque l’activation :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Cette autorisation est limitée au terminal courant.

## 4. Installer les bibliothèques du TP1

Avec `.venv` activé, exécutez :

```bash
python -m pip install -r requirements.txt
```

Vérifiez l’installation :

```bash
python --version
python -m pip check
python -c "import pydantic, dotenv, langchain_core, langchain_ollama, langchain_groq, pytest, streamlit; print('Environnement Python : OK')"
```

Le chemin de l’interpréteur doit contenir `.venv` :

```bash
python -c "import sys; print(sys.executable)"
```

## 5. Préparer un fournisseur de LLM

Vous devez préparer **au moins une** des deux options suivantes.

### Option A — Ollama : modèle local

Choisissez cette option si votre ordinateur dispose de ressources suffisantes, idéalement 16 Go de RAM.

1. Installez Ollama depuis <https://ollama.com/download>.
2. Démarrez l’application ou le service Ollama.
3. Téléchargez le modèle du TP1 :

```bash
ollama pull llama3.1:8b
```

4. Vérifiez sa présence :

```bash
ollama list
```

5. Testez le modèle :

```bash
ollama run llama3.1:8b "Réponds uniquement par : installation réussie"
```

6. Vérifiez que le service local répond :

```bash
curl http://localhost:11434/api/tags
```

### Option B — Groq : API distante

Choisissez cette option si votre ordinateur ne peut pas exécuter confortablement un modèle local. Une connexion Internet est obligatoire.

1. Créez un compte sur <https://console.groq.com/>.
2. Créez une clé personnelle sur <https://console.groq.com/keys>.
3. Conservez-la dans un gestionnaire de mots de passe.

Ne placez jamais cette clé dans un fichier Python et ne la partagez avec personne.

### Test temporaire de Groq sous macOS/Linux

```bash
export GROQ_API_KEY="votre_cle_personnelle"
python -c "from langchain_groq import ChatGroq; print(ChatGroq(model='llama-3.1-8b-instant').invoke('Réponds uniquement par OK').content)"
unset GROQ_API_KEY
```

### Test temporaire de Groq sous Windows PowerShell

```powershell
$env:GROQ_API_KEY="votre_cle_personnelle"
python -c "from langchain_groq import ChatGroq; print(ChatGroq(model='llama-3.1-8b-instant').invoke('Réponds uniquement par OK').content)"
Remove-Item Env:GROQ_API_KEY
```

Si le modèle indiqué n’est plus disponible, consultez la liste des modèles actifs dans la console Groq et remplacez son nom dans la commande de test.

## 6. Vérification finale

- [ ] Python 3.11 ou une version plus récente est installé.
- [ ] Git fonctionne.
- [ ] Visual Studio Code est installé.
- [ ] `.venv` a été créé et peut être activé.
- [ ] `python -m pip install -r requirements.txt` se termine sans erreur.
- [ ] `python -m pip check` ne signale aucun conflit.
- [ ] Le chemin affiché par `sys.executable` contient `.venv`.
- [ ] Au moins une option est prête : Ollama ou Groq.
- [ ] Avec Ollama, `llama3.1:8b` apparaît dans `ollama list` et répond.
- [ ] Avec Groq, une clé personnelle a été créée et testée.
