# SLRResearchAI — TD04 étudiant

Le TD04 consomme l'artefact de recherche du TD03 et contrôle une décision de
screening titre/résumé.

```text
TD03 → artifacts/search_results.json → TD04 ScreeningAgent
```

## Démarrage

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest -v
python main.py
python -m streamlit run streamlit_app.py
```

Commencez par `ENONCE_TD04.md`, puis complétez successivement
`slrresearch/screening_agent.py` et `slrresearch/llm_screening_agent.py`.
Le fournisseur réel est choisi dans `.env`, jamais dans l'interface.

Pour comprendre et exécuter la construction cumulative TD01 → TD04, consultez
`CONSTRUIRE_PROJET_BOUT_EN_BOUT.md`.
