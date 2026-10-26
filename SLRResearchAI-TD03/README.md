# SLRResearchAI — TD03

Le TD03 compare un workflow outillé contrôlé et un SearchAgent ReAct
contrôlé. Il charge réellement `artifacts/search_plan.json` au lieu de recopier
les requêtes dans un module Python.

Le JSON fourni est prérempli afin que le TD reste autonome. Consultez
`CONTINUITE_REELLE_TD02.md` pour le faire produire automatiquement par le TD02.

Les fichiers `slrresearch/research_questions.py` et
`slrresearch/search_plan.py` sont les acquis complets des TD01–TD02. Ils sont
conservés dans le dépôt cumulatif et ne doivent pas être recommencés.

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

## Travail

Lisez `ENONCE_TD03.md`, puis avancez avec les tests ciblés :

```bash
python -m pytest -v -k "todo_1"
python -m pytest -v -k "todo_2"
python -m pytest -v -k "todo_3"
python -m pytest -v -k "todo_4"
python -m pytest -v -k "todo_5"
python -m pytest -v -k "todo_6"
python -m pytest -v -k "todo_7"
python -m pytest -v -k "todo_8"
```

Validation finale :

```bash
python -m pytest -v
python main.py
python -m streamlit run streamlit_app.py
```

Le mode reproductible ne dépend ni d'Internet ni d'un LLM. Le mode LLM réel
utilise Groq ou Ollama selon `.env`.
