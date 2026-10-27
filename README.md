# 📚 SLRResearchAI — Assistant LLM contrôlé pour revues systématiques de la littérature

> Assistant basé sur des **LLM** pour accompagner les **revues systématiques de la littérature (SLR)** : formulation de questions de recherche, **agent ReAct**, **screening** des articles et **RAG**. Projet pédagogique organisé en cinq travaux dirigés (TD).

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-core-1C3C3C)
![Ollama](https://img.shields.io/badge/LLM%20local-Ollama-000000)
![Groq](https://img.shields.io/badge/LLM%20cloud-Groq-F55036)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Pydantic](https://img.shields.io/badge/Validation-Pydantic%20v2-E92063)

---

## 📌 Table des matières

1. [Contexte et objectifs](#contexte-et-objectifs)
2. [Pourquoi un assistant « contrôlé » ?](#pourquoi-un-assistant--contrôlé-)
3. [Fonctionnalités](#fonctionnalités)
4. [Structure du dépôt](#structure-du-dépôt)
5. [Progression pédagogique (TD01 à TD05)](#progression-pédagogique-td01-à-td05)
6. [Stack technique](#stack-technique)
7. [Prérequis](#prérequis)
8. [Installation](#installation)
9. [Configuration](#configuration)
10. [Utilisation](#utilisation)
11. [Tests](#tests)
12. [Bonnes pratiques et limites](#bonnes-pratiques-et-limites)
13. [Dépannage](#dépannage)
14. [Contribuer](#contribuer)
15. [Auteur](#auteur)

---

## Contexte et objectifs

Une **revue systématique de la littérature (SLR)** est une méthode rigoureuse et reproductible pour recenser, sélectionner et synthétiser les travaux existants sur un sujet. Chaque étape (questions de recherche, requêtes, sélection, extraction, synthèse) est longue et sujette aux biais.

**SLRResearchAI** explore comment des LLM peuvent assister ces étapes **sans sacrifier la rigueur méthodologique**. C'est un **projet pédagogique** : l'objectif est d'apprendre à construire des applications LLM structurées, traçables et testables.

**Objectifs d'apprentissage :**

- Structurer les sorties d'un LLM avec des schémas **Pydantic**
- Construire un **agent ReAct** (raisonnement + actions avec outils)
- Automatiser le **screening** des articles selon des critères d'inclusion/exclusion
- Mettre en place un pipeline **RAG** (Retrieval-Augmented Generation)
- Exécuter les modèles en **local** (Ollama) ou dans le **cloud** (Groq)
- Tester et exposer le tout via une interface **Streamlit**

---

## Pourquoi un assistant « contrôlé » ?

Un LLM utilisé tel quel peut inventer des références, mal appliquer des critères ou produire des résultats non reproductibles. L'approche « contrôlée » consiste à :

| Principe | Mise en œuvre |
|---|---|
| **Sorties structurées** | Schémas Pydantic validés, pas de texte libre non vérifié |
| **Traçabilité** | Chaque décision (ex. inclusion/exclusion) est accompagnée d'une justification |
| **Humain dans la boucle** | Le chercheur valide ; l'IA propose, elle ne tranche pas seule |
| **Ancrage dans les sources** | RAG pour répondre à partir des documents fournis |
| **Reproductibilité** | Paramètres, prompts et modèles explicitement configurés |
| **Testabilité** | Tests automatisés avec `pytest` |

> ✏️ Adaptez ce tableau aux mécanismes de contrôle réellement implémentés dans vos TD.

---

## Fonctionnalités

- ❓ **Génération et affinement de questions de recherche** (cadre type PICO ou équivalent)
- 🤖 **Agent ReAct** qui alterne raisonnement et appels d'outils
- 🔎 **Screening** des articles (titre/résumé) selon des critères d'inclusion et d'exclusion
- 📖 **RAG** : interrogation d'un corpus d'articles avec réponses ancrées dans les sources
- 🖥️ **Interface Streamlit** pour utiliser l'assistant sans code
- 🔌 **Choix du fournisseur LLM** : local via **Ollama** ou cloud via **Groq**

> ✏️ Retirez ou ajustez les fonctionnalités selon l'état réel d'avancement de chaque TD.

---

## Structure du dépôt

```
SLRResearchAI/
├── SLRResearchAI-TD01/          # Travail dirigé 1
├── SLRResearchAI-TD02/          # Travail dirigé 2
├── SLRResearchAI-TD03/          # Travail dirigé 3
├── SLRResearchAI-TD04/          # Travail dirigé 4
├── SLRResearchAI-TD05/          # Travail dirigé 5
├── GUIDE_INSTALLATION_TP1 (1).md   # Guide d'installation de l'environnement
├── requirements.txt             # Dépendances Python
└── .gitignore
```

---

## Progression pédagogique (TD01 à TD05)

Le projet se construit par étapes : chaque TD s'appuie sur le précédent.

| TD | Thème | Objectif |
|---|---|---|
| **TD01** | ✏️ *à compléter* | ✏️ ex. : prise en main de l'environnement, premier appel LLM |
| **TD02** | ✏️ *à compléter* | ✏️ ex. : sorties structurées (Pydantic), questions de recherche |
| **TD03** | ✏️ *à compléter* | ✏️ ex. : agent ReAct et outils |
| **TD04** | ✏️ *à compléter* | ✏️ ex. : screening des articles |
| **TD05** | ✏️ *à compléter* | ✏️ ex. : RAG et interface Streamlit |

> ✏️ Les thèmes ci-dessus sont des **suggestions** déduites de la description du projet. Remplacez-les par le contenu réel de chaque dossier.

---

## Stack technique

| Composant | Technologie | Rôle |
|---|---|---|
| Langage | Python | Langage principal |
| Orchestration LLM | `langchain-core` | Chaînes, prompts, outils |
| LLM local | `langchain-ollama` | Exécution de modèles en local via Ollama |
| LLM cloud | `langchain-groq` | Accès à des modèles hébergés par Groq |
| Validation | `pydantic` v2 | Schémas et validation des sorties |
| Configuration | `python-dotenv` | Variables d'environnement (clés API) |
| Interface | `streamlit` | Application web interactive |
| Client HTTP | `httpx` | Appels HTTP (API, sources bibliographiques) |
| Tests | `pytest` | Tests automatisés |

---

## Prérequis

- **Python** 3.10 ou supérieur
- **Git**
- *Au choix (ou les deux) :*
  - **[Ollama](https://ollama.com)** pour exécuter un modèle en local
  - Un compte **[Groq](https://console.groq.com)** avec une clé API

---

## Installation

> Un guide détaillé est disponible dans `GUIDE_INSTALLATION_TP1 (1).md`.

```bash
# 1. Cloner le dépôt
git clone https://github.com/kammounimen/SLRResearchAI.git
cd SLRResearchAI

# 2. Créer et activer un environnement virtuel
python -m venv venv

# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt
```

### Modèle local avec Ollama (optionnel)

```bash
ollama pull llama3.1        # ✏️ remplacez par le modèle utilisé dans vos TD
ollama serve
```

---

## Configuration

Créez un fichier **`.env`** à la racine (ou dans le dossier du TD concerné) :

```env
# ── Fournisseur LLM ────────────────────────────────────
# Cloud (Groq)
GROQ_API_KEY=votre_cle_groq_ici

# Local (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
```

> ✏️ Ajustez les noms de variables à ceux réellement lus par votre code.

⚠️ Ne committez jamais `.env` : vérifiez qu'il est dans `.gitignore`.

---

## Utilisation

Chaque TD est autonome dans son dossier. Exemple de workflow :

```bash
cd SLRResearchAI-TD01
# ✏️ Consultez le README ou l'énoncé du TD pour les instructions précises
```

### Lancer l'interface Streamlit

```bash
streamlit run app.py         # ✏️ adaptez le chemin du fichier Streamlit
```

L'interface est alors disponible sur **http://localhost:8501**.

### Exemple d'enchaînement type d'une SLR assistée

```
Sujet de recherche
      │
      ▼
 Questions de recherche (LLM + schéma Pydantic)
      │
      ▼
 Agent ReAct : recherche et collecte d'articles
      │
      ▼
 Screening : inclusion / exclusion justifiée
      │
      ▼
 RAG : questions sur le corpus retenu → synthèse sourcée
      │
      ▼
 Validation par le chercheur (humain dans la boucle)
```

---

## Tests

```bash
pytest                  # tous les tests
pytest -v               # mode détaillé
pytest SLRResearchAI-TD02   # tests d'un TD précis
```

---

## Bonnes pratiques et limites

- 🧪 **Vérifiez toujours** les références et les affirmations générées : un LLM peut halluciner.
- 🔁 **Documentez** le modèle, la version, la température et les prompts utilisés pour garantir la reproductibilité.
- 👤 **Gardez l'humain dans la boucle** : le screening automatisé doit être contrôlé, idéalement par un second relecteur.
- 🔒 **Confidentialité** : avec Groq, les données transitent par un service tiers ; privilégiez Ollama en local pour des données sensibles.
- 📏 Les résultats dépendent fortement du **modèle choisi** (taille, langue, qualité du raisonnement).

---

## Dépannage

| Problème | Piste de solution |
|---|---|
| `ModuleNotFoundError` | Vérifier que l'environnement virtuel est activé, puis `pip install -r requirements.txt` |
| `Connection refused` (Ollama) | Lancer `ollama serve` et vérifier l'URL (`http://localhost:11434`) |
| Modèle introuvable | `ollama pull <nom-du-modèle>` |
| Erreur 401 / clé invalide (Groq) | Vérifier `GROQ_API_KEY` dans `.env` |
| Erreur 429 (Groq) | Limite de débit atteinte : patienter ou réduire la fréquence des appels |
| Sortie non conforme au schéma Pydantic | Baisser la température, préciser le prompt, ou relancer avec validation/réessai |

---

## Contribuer

Ce projet étant pédagogique, les suggestions et retours sont les bienvenus :

1. Forkez le dépôt
2. Créez une branche : `git checkout -b feature/ma-amelioration`
3. Committez vos changements et poussez la branche
4. Ouvrez une Pull Request

---

## Auteur

**kammounimen** — [github.com/kammounimen](https://github.com/kammounimen)

*Projet pédagogique — assistant LLM contrôlé pour revues systématiques de la littérature.*
