# SLRResearchAI — Correction du TD03Bis

Cette version contient la correction des sept TODO du TD03Bis. Elle charge
réellement `artifacts/search_plan.json`. Le fichier est prérempli pour le mode
autonome ; `CONTINUITE_REELLE_TD02.md` explique comment le faire produire par
le TD02.

Les fichiers `slrresearch/research_questions.py` et
`slrresearch/search_plan.py` sont également conservés comme acquis complets des
TD01–TD02.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
python main.py
python -m streamlit run streamlit_app.py
```

Résultat attendu : `23 passed`.

Consultez `CORRECTION_DETAILLEE_TD03BIS.md` pour le raisonnement, la correction du
TODO 7 et les réponses aux questions d'interprétation.
