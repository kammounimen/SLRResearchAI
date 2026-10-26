# Construire SLRResearchAI de bout en bout

## 1. Le dépôt est cumulatif

```text
TD01 : sujet → questions de recherche libres
  ↓
TD02 : validation/repair → questions et requêtes structurées
  ↓ search_plan.json
TD03 : ReAct contrôlé + outils réels → titres, résumés et traces
  ↓ search_results.json
TD04 : screening déterministe + screening LLM + arbitrage humain
```

Le TD04 conserve les acquis du TD03 dans `slrresearch/` : contrats, registre
d'outils, APIs réelles, runtime, état, workflow et agent ReAct. Les anciens
points d'entrée restent consultables dans `historique/TD03/`.

Le travail nouveau porte uniquement sur `screening_agent.py` et
`llm_screening_agent.py`.

## 2. Origine de l'artefact distribué

`artifacts/search_results.json` contient de vrais articles scientifiques. Il a
été produit avant la séance par le ReAct contrôlé du TD03 :

1. chargement des requêtes du TD02 ;
2. sélection successive des outils autorisés ;
3. appels réels à OpenAlex, Crossref et Semantic Scholar ;
4. conversion de chaque réponse en observation ;
5. mise à jour et déduplication du `SearchState` ;
6. sérialisation manuelle du résultat pour préparer le TD04.

Résultat de la collecte fournie :

```text
OpenAlex          → succès
Crossref          → succès
Semantic Scholar  → 429 rate_limited
Articles uniques  → 16
Avec résumé       → 10
```

Le champ suivant permet de vérifier qu'il ne s'agit pas du catalogue fictif :

```json
"pedagogical_fixture": false
```

## 3. Ce qui reste volontairement à construire

Le dépôt ne contient pas de script qui relance TD03 et écrase automatiquement
l'artefact du TD04. Cette connexion est une amélioration attendue dans le
projet personnel.

L'étudiant devra proposer une fonction qui reçoit un `SearchState` terminé et
produit un `SearchArtifact`, puis tester les propriétés suivantes :

- `origin == "TD03"` ;
- conservation des requêtes et sources tentées ;
- transmission des vrais titres, résumés, DOI et URL ;
- cohérence entre `unique_results` et le nombre de papiers ;
- absence de dépendance de TD04 envers l'interface Streamlit du TD03.

## 4. Installer

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Dans `.env`, sélectionner Ollama :

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.1:8b
```

ou Groq :

```env
LLM_PROVIDER=groq
GROQ_API_KEY=votre_cle
GROQ_MODEL=openai/gpt-oss-20b
```

## 5. Vérifier les acquis

```bash
python -m pytest -v tests/acquis_td03
```

Ces 23 tests protègent les capacités déjà développées. Il ne faut pas refaire
les TODO du TD03 dans le TD04.

## 6. Réaliser TD04

```bash
python -m pytest -v -k "todo_1"
# continuer jusqu'à todo_10
python -m pytest -v tests/test_td04.py tests/test_td04_llm.py
python -m pytest -v
```

Résultats attendus après correction :

```text
14 tests TD04
37 tests cumulatifs
```

## 7. Examiner les vrais papiers

```bash
python -m streamlit run streamlit_app.py
```

Dans l'interface :

1. vérifiez `pedagogical_fixture = false` et l'origine `TD03` ;
2. ouvrez le résumé intégral et la véritable notice scientifique ;
3. exécutez A seule et interprétez sa politique ;
4. rechargez si nécessaire puis exécutez B seule pour vérifier son indépendance ;
5. lorsque A et B existent, comparez manuellement leurs colonnes ;
6. lancez C et observez comment elle transforme les deux sorties en accords,
   désaccords et arbitrages ;
7. justifiez les décisions humaines.

C ne relance ni A ni B. Cette contrainte matérialise une coopération par
artefacts : chaque agent produit sa décision, puis un composant de contrôle
consomme les deux résultats.

Certains papiers n'ont pas de résumé : cette absence vient des métadonnées
réelles. Elle doit provoquer l'abstention ou l'intervention humaine, et non une
invention du LLM.

## 8. Suite du projet

La version personnelle devra automatiser le handoff TD03 → TD04, conserver la
trace des erreurs d'API comme le `429`, puis transmettre les verdicts du TD04 au
futur agent de téléchargement. Chaque étape échange un artefact validé ; elle
n'importe jamais l'interface du TD précédent.
