# SLRResearchAI — Projet cumulatif, TD05 RAG classique

Ce TD construit un pipeline RAG classique fidèle au chapitre RAG du cours :
chunks traçables, TF-IDF, embeddings, Top-k, Precision@k, Recall@k, génération
structurée et contrôle des citations.

Le dépôt conserve les modules Python acquis pendant les TD01 à TD04 dans le
même package `slrresearch`. Le TD05 ajoute `rag_models.py`, `rag_artifacts.py`,
`rag_pipeline.py` et `pdf_loader.py` sans supprimer les agents précédents.
Les artefacts assurent la transmission des données ; ils ne remplacent pas le
code. Consultez `CONSTRUIRE_PROJET_BOUT_EN_BOUT.md` pour relier les exécutions.

Pour revoir la préparation du corpus, la tokenisation, l'indexation, TF-IDF,
BM25, le classement Top-k et les métriques, consultez
`GUIDE_RETRIEVAL_LEXICAL.md`.

La continuité est matérialisée par les artefacts :

```text
TD03/search_results.json
→ TD04/screening_decisions.json
→ document_manifest.json
→ RAG
→ verified_evidence.json
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -v
python -m streamlit run streamlit_app.py
```

Pour le mode réel :

```bash
cp .env.example .env
ollama pull nomic-embed-text
```
