# TD04 — Du résultat de recherche au screening contrôlé

## 1. Continuité réelle avec le TD03

Le TD03 recherche des articles auprès de plusieurs sources, normalise leurs
métadonnées et les déduplique. Le TD04 ne recommence pas cette recherche : il
consomme son résultat persistant.

```text
TD03 SearchAgent
   ↓ produit
artifacts/search_results.json
   ↓ validé par Pydantic
TD04 ScreeningAgent
   ↓ produit
include / exclude / uncertain + raisons + file humaine
```

Le fichier distribué est un **instantané réel** produit avant la séance par le
SearchAgent ReAct contrôlé du TD03. Il a appelé OpenAlex, Crossref et Semantic
Scholar avec les requêtes de `search_plan.json`. OpenAlex et Crossref ont
retourné des articles ; Semantic Scholar a répondu `429`. Après normalisation
et déduplication, l'artefact contient 16 articles scientifiques réels, dont 10
avec résumé. Le champ suivant atteste qu'il ne s'agit pas du fixture local :

```json
"pedagogical_fixture": false
```

La boucle qui régénère automatiquement ce fichier n'est volontairement pas
fournie. Dans le projet final, vous devrez connecter l'état final du TD03 à ce
contrat, sans recopier les articles dans le code du TD04.

## 2. Ordre méthodologique

Ce TD applique un screening sur le titre et le résumé avant le téléchargement
des textes intégraux :

```text
recherche → déduplication → screening titre/résumé
          → récupération des PDF retenus → éligibilité texte intégral
```

Dans ce TD, `include` ne signifie pas « article définitivement inclus dans la
SLR ». Il signifie « article à transmettre à l'évaluation sur texte intégral ».
De même, `exclude` est une recommandation issue du titre et du résumé, soumise
à la politique de contrôle définie ci-dessous.

Le prochain TD pourra donc télécharger uniquement les articles retenus ou les
cas incertains nécessitant une vérification approfondie.

## 3. Objectifs pédagogiques

Vous allez apprendre à :

1. consommer un artefact produit par une étape précédente ;
2. distinguer validation du contrat et qualité scientifique des données ;
3. distinguer critères, indicateurs et verdict ;
4. observer des signaux avant d'appliquer une politique ;
5. produire un verdict structuré et justifié ;
6. s'abstenir lorsque les signaux sont insuffisants ;
7. transférer les conflits et cas sensibles à un humain ;
8. reconnaître les limites de la recherche lexicale et de l'artefact fourni ;
9. construire un screening sémantique avec un LLM ;
10. imposer une sortie Pydantic et contrôler que la preuve est ancrée dans la source ;
11. comparer agent déterministe et agent LLM ;
12. transférer leurs désaccords à un évaluateur humain.

## 4. Ce qui est fourni

```text
SLRResearchAI-TD04/
├── artifacts/
│   ├── search_plan.json         # acquis TD02 consommé au TD03
│   └── search_results.json      # sortie TD03 consommée au TD04
├── data/
│   └── papers.json              # catalogue reproductible du TD03
├── slrresearch/
│   ├── artifacts.py             # contrat Pydantic complet, ne pas modifier
│   ├── config.py                # choix Groq/Ollama depuis .env
│   ├── contracts.py             # acquis TD03 : actions, observations, état
│   ├── tools.py / real_tools.py # acquis TD03 : outils locaux et réels
│   ├── runtime.py / workflow.py # acquis TD03 : exécution contrôlée
│   ├── react_agent.py           # acquis TD03 : boucle agentique
│   ├── screening_agent.py       # TODO 1 à 6
│   └── llm_screening_agent.py   # TODO 7 à 10
├── tests/
│   ├── acquis_td03/             # tests de non-régression des acquis
│   ├── test_td04.py
│   └── test_td04_llm.py
├── CONSTRUIRE_PROJET_BOUT_EN_BOUT.md
├── main.py
├── streamlit_app.py
└── ENONCE_TD04.md
```

## 5. Comprendre l'artefact avant de coder

Ouvrez `artifacts/search_results.json` et repérez :

- `origin="TD03"` : provenance obligatoire ;
- `search.queries` : requêtes reçues du TD02 et utilisées par le TD03 ;
- `raw_results` : résultats avant déduplication ;
- `unique_results` : articles transmis après déduplication ;
- `papers` : titres, résumés, DOI, source, URL et accès ouvert.

Les URL et DOI de cet artefact proviennent des API scientifiques. Certaines
notices pointent vers une page DOI et d'autres directement vers un PDF en accès
libre. L'absence de résumé pour certains articles est une limite réelle des
métadonnées reçues, pas une donnée inventée pour le TD.

Le chargeur fourni applique le modèle `SearchArtifact`. Il refuse notamment un
fichier absent, une origine différente de `TD03`, une version inconnue ou une
liste d'articles vide.

Testez uniquement le handoff :

```bash
python -m pytest -v tests/test_td04.py -k "acquis_handoff"
```

Les deux tests doivent déjà réussir, avant toute modification.

### Convention pour exécuter un seul TODO

Chaque commande indique le fichier de tests concerné et ajoute `_` après le
numéro du TODO. Par exemple :

```bash
python -m pytest -v tests/test_td04.py -k "todo_1_"
```

Le suffixe `_` est important : sans lui, `-k "todo_1"` sélectionnerait aussi
un test nommé `todo_10`. Le chemin du fichier empêche également Pytest de
sélectionner les anciens tests `todo_1` hérités du TD03.

## 6. Politique de screening du TD

Les critères sont définis en amont :

```python
include_terms = {"slr", "screening", "systematic review"}
exclude_terms = {"medicine", "clinical trial"}
human_threshold = 0.80
```

Politique de priorité :

```text
signal d'exclusion → exclude, confiance 0.95
sinon signal d'inclusion → include, confiance 0.90
sinon → uncertain, confiance 0.45
```

La confiance est une valeur fixée par la règle. Ce n'est ni une probabilité
apprise, ni une probabilité statistiquement calibrée.

---

# Partie A — Observer les indicateurs

## TODO 1 — Normaliser le titre et le résumé

**Fichier :** `slrresearch/screening_agent.py`  
**Fonction :** `normalize_paper_text()`  
**Repère :** `text = None`

### 1. Identifier le contrat de `paper`

Ne devinez pas les attributs de l'objet `paper`.

1. Ouvrez `slrresearch/artifacts.py`.
2. Recherchez la classe `PaperRecord`.
3. Repérez le champ qui contient le titre et celui qui contient le résumé.
4. Revenez dans `slrresearch/screening_agent.py`, dans la fonction
   `normalize_paper_text()`.

Cette démarche permet de suivre le contrat de données transmis par le TD03 :

```text
normalize_paper_text(paper)
        ↓
PaperRecord dans artifacts.py
        ↓
champs disponibles sur paper
```

### 2. Construire le texte analysé

Utilisez les deux noms de champs trouvés dans `PaperRecord`. Concaténez le
titre, un espace et le résumé, puis convertissez le résultat en minuscules :

```python
text = (paper.________ + " " + paper.________).________()
```

Les trois blancs représentent respectivement :

1. le champ du titre ;
2. le champ du résumé ;
3. la méthode Python de conversion en minuscules.

L'espace évite de coller le dernier mot du titre au premier mot du résumé. Vous
ne devez modifier que la ligne `text = None` du TODO 1. Cette fonction est
testée directement : le TODO 1 ne dépend donc pas du TODO 2.

```bash
python -m pytest -v tests/test_td04.py -k "todo_1_"
```

## TODO 2 — Extraire les signaux sans décider

**Fonction :** `observe_indicators()`  
**Repères :** `inclusion_matches = []` et `exclusion_matches = []`

Complétez deux compréhensions triées :

```python
inclusion_matches = sorted(
    term for term in include_terms
    if term.lower() in text
)
```

Construisez `exclusion_matches` avec le même principe.

Le code fourni calcule ensuite :

```text
information_sufficient = titre non vide ET résumé non vide
conflict = inclusion présente ET exclusion présente
```

À ce stade, vous avez des indicateurs, pas encore une décision.

```bash
python -m pytest -v tests/test_td04.py -k "todo_2_"
```

---

# Partie B — Appliquer les critères

## TODO 3 — Produire le verdict, la confiance et les raisons

**Fonction :** `choose_preliminary_verdict()`

Complétez les trois branches déjà fournies.

### Exclusion

```python
decision = "exclude"
confidence = 0.95
reasons = [
    f"Critère d'exclusion détecté : {term}"
    for term in indicators.exclusion_matches
]
```

### Inclusion

Utilisez `include`, `0.90` et les termes de
`indicators.inclusion_matches`.

### Abstention

Utilisez :

```python
decision = "uncertain"
confidence = 0.45
reasons = ["Aucun signal lexical ne permet de trancher"]
```

L'ordre des branches matérialise la politique d'exclusion prioritaire.

La fonction retourne uniquement :

```python
return decision, confidence, reasons
```

Elle ne construit pas encore un `ScreeningDecision`. Son test est donc
indépendant des TODO 4 et 5.

```bash
python -m pytest -v tests/test_td04.py -k "todo_3_"
```

## TODO 4 — Contrôler l'automatisation

**Fonction :** `requires_human_review()`  
**Repère :** `return None`

La décision ne doit pas être automatisée si une seule de ces conditions est
vraie :

- verdict `uncertain` ;
- confiance inférieure au seuil ;
- conflit entre indicateurs ;
- titre ou résumé insuffisant.

Remplacez `return None` par :

```python
return (
    decision == "________"
    or confidence < ________________
    or indicators.________
    or not indicators.________________________
)
```

Cette fonction reçoit déjà le verdict provisoire, sa confiance et les
indicateurs. Elle est testée directement et ne dépend pas du TODO 5.

```bash
python -m pytest -v tests/test_td04.py -k "todo_4_"
```

## TODO 5 — Retourner le verdict structuré

**Fonction :** `apply_screening_policy()`

Remplacez le `raise NotImplementedError` par la construction suivante, en
complétant les six valeurs :

```python
return ScreeningDecision(
    paper_id=________,
    decision=________,
    confidence=________,
    reasons=________,
    indicators=________,
    needs_human_review=________,
)
```

Le verdict conserve ainsi les indicateurs qui l'ont éclairé et les raisons qui
le rendent justifiable.

```bash
python -m pytest -v tests/test_td04.py -k "todo_5_"
```

---

# Partie C — Orchestrer et transférer

## TODO 6 — Compléter ScreeningAgent

Dans `ScreeningAgent.run()`, remplacez les trois zones incomplètes :

```python
indicators = observe_indicators(
    paper, include_terms, exclude_terms
)

decision = apply_screening_policy(
    paper.id, indicators, human_threshold
)

human_queue = [
    item for item in decisions
    if item.needs_human_review
]
```

La file humaine ne doit pas recalculer la politique. Elle consomme le champ de
contrôle déjà produit avec le verdict.

```bash
python -m pytest -v tests/test_td04.py -k "todo_6_"
python -m pytest -v
```

Résultat attendu :

```text
8 passed
```

---

# Partie D — Comparer règles et compréhension sémantique

La version A est rapide, reproductible et explicable, mais elle ne comprend
pas la négation. Par exemple, le papier P04 contient les mots `medicine` et
`clinical trial` dans la phrase « does not concern… ». Les règles voient les
mots ; le LLM peut interpréter leur contexte. Le LLM peut cependant inventer
ou varier : il reste donc contrôlé.

Tous les TODO suivants se trouvent dans
`slrresearch/llm_screening_agent.py`.

## TODO 7 — Construire le prompt de screening

Complétez `build_screening_messages()`. Le `SystemMessage` doit imposer :

- les trois décisions `include`, `exclude`, `uncertain` ;
- l'usage exclusif du titre et du résumé ;
- l'interdiction d'inventer ;
- une confiance décimale comprise entre `0` et `1` ;
- une preuve copiée exactement du texte fourni ;
- `uncertain` si l'information manque.

Le `HumanMessage` doit transmettre le sujet, les deux listes de critères,
l'identifiant, le titre et le résumé. Utilisez des f-strings :

```python
user_prompt = (
    f"Sujet de la SLR : {topic}\n"
    f"Critères d'inclusion : {', '.join(sorted(inclusion_terms))}\n"
    # Compléter avec exclusion, identifiant, titre et résumé.
)
```

```bash
python -m pytest -v tests/test_td04_llm.py -k "todo_7_"
```

## TODO 8 — Effectuer un seul appel structuré

**Fichier :** `slrresearch/llm_screening_agent.py`  
**Fonction à compléter :** `invoke_structured_screening()`  
**Nombre de blancs :** 1

La construction des messages, le schéma Pydantic et la restitution de
l'identifiant sont déjà fournis. Vous devez uniquement appeler la méthode
LangChain qui exécute le modèle.

Complétez le seul blanc :

```python
decision = structured_model.________(messages)
```

La dernière ligne, déjà fournie, remplace ensuite l'identifiant proposé par le
LLM par `paper.id`. Le LLM décide le contenu sémantique ; l'application conserve
l'identité technique et la traçabilité.

Le contrôle de la preuve n'appartient pas au TODO 8 : il est effectué par
`screen_with_llm()` à l'aide du TODO 9. Le test du TODO 8 appelle directement
`invoke_structured_screening()` ; il reste donc indépendant du TODO 9.

Le test vérifie trois propriétés seulement :

- le schéma transmis est `LLMScreeningDecision` ;
- un seul appel au modèle est effectué ;
- l'identifiant final est celui du papier courant.

```bash
python -m pytest -v tests/test_td04_llm.py -k "todo_8_"
```

## TODO 9 — Contrôler l'ancrage de la preuve

**Fichier :** `slrresearch/llm_screening_agent.py`  
**Fonction à compléter :** `validate_grounding()`  
**Nombre de lignes à compléter :** 2

### Objectif

Le LLM renvoie une chaîne `evidence`. Le programme doit accepter la sortie dans
un seul des deux cas suivants :

1. le LLM choisit `uncertain` et ne fournit aucune preuve ;
2. le LLM fournit une preuve non vide qui apparaît dans le titre ou le résumé.

Tous les autres cas doivent être refusés.

### Variables déjà préparées

Vous ne devez pas écrire le code de normalisation. La fonction fournit déjà :

```python
evidence             # preuve originale, sans espaces au début ou à la fin
normalized_evidence  # preuve normalisée
source_text          # titre + résumé normalisés
```

La normalisation neutralise les différences de casse, de ponctuation et
d'espaces. Elle ne demande pas au LLM une nouvelle génération.

### Les deux questions à traduire en Python

Remplacez uniquement les deux `None` :

```python
valid_empty_evidence = None
evidence_found = None
```

Pour la première ligne, traduisez :

> La preuve est vide ET la décision vaut `uncertain`.

Pour la seconde ligne, traduisez :

> La preuve n'est pas vide ET sa version normalisée est contenue dans
> `source_text`.

Vous pouvez utiliser ces éléments :

```python
not evidence
decision.decision == "uncertain"
bool(evidence)
normalized_evidence in source_text
```

### Vérifier votre raisonnement

| Preuve | Décision | Preuve trouvée dans la source | Résultat |
|---|---|---:|---|
| vide | `uncertain` | non applicable | accepté |
| vide | `include` ou `exclude` | non applicable | refusé |
| non vide | quelconque | oui | accepté |
| non vide | quelconque | non | refusé |

Le `if` final et l'exception sont déjà fournis :

```python
if not (valid_empty_evidence or evidence_found):
    raise ValueError("Preuve LLM absente du titre et du résumé")
```

Vous n'avez pas à modifier ces deux lignes.

### Limite scientifique du contrôle

La validation Pydantic contrôle la forme. Cette fonction contrôle ensuite une
propriété minimale : la preuve doit réellement provenir de l'entrée. Elle ne
garantit ni que la preuve est scientifiquement pertinente, ni qu'elle justifie
correctement le verdict. Dans `screen_with_llm()`, son échec ne doit pas
interrompre les 16 papiers : il transforme uniquement le papier concerné en
`uncertain` et l'envoie à l'humain.

```bash
python -m pytest -v tests/test_td04_llm.py -k "todo_9_"
```

## TODO 10 — Comparer et escalader

**Fichier :** `slrresearch/llm_screening_agent.py`  
**Fonction à compléter :** `compare_decisions()`  
**Nombre de lignes à compléter :** 2

### Objectif de la version C

La fonction reçoit deux recommandations automatiques portant sur le même
papier :

```python
deterministic  # résultat de la version A fondée sur les règles
llm            # résultat de la version B fondée sur le LLM
```

C ne réalise pas un troisième screening. Elle décide uniquement si les deux
sorties peuvent être exploitées automatiquement ou si le cas doit être transmis
à un humain.

### Informations disponibles

Les deux objets possèdent notamment :

```python
.decision            # include, exclude ou uncertain
.needs_human_review  # booléen : True ou False
```

Le code fourni compare déjà les deux verdicts :

```python
agreement = deterministic.decision == llm.decision
```

Vous ne devez pas modifier cette ligne.

### Travail demandé

Lisez maintenant le drapeau `needs_human_review` de chaque objet. Remplacez
uniquement les deux `None` :

```python
deterministic_requests_human = None  # lire le champ de la version A
llm_requests_human = None            # lire le champ de la version B
```

Le résultat de la première ligne doit donc provenir de `deterministic` et celui
de la seconde de `llm`. Il n'est pas nécessaire de recalculer une confiance ou
d'examiner les raisons.

### Règle de routage déjà fournie

```python
needs_human_review = (
    deterministic_requests_human
    or llm_requests_human
    or not agreement
)
```

Le mot-clé `or` signifie qu'une seule alerte suffit. Le cas est transmis à
l'humain si :

- A demande une revue humaine ;
- ou B demande une revue humaine ;
- ou A et B produisent des verdicts différents.

### Exemples à interpréter

| Verdict A | Humain A | Verdict B | Humain B | Résultat de C |
|---|---:|---|---:|---|
| `include` | `False` | `include` | `False` | `AUTO` |
| `include` | `True` | `include` | `False` | `HUMAN` |
| `include` | `False` | `exclude` | `False` | `HUMAN` |
| `uncertain` | `True` | `uncertain` | `True` | `HUMAN` |

Le deuxième cas est important : un accord entre A et B ne suffit pas si l'un
des deux signale que sa recommandation doit être contrôlée.

Les messages d'explication et la construction du `ComparisonResult` sont déjà
fournis. Ne modifiez pas cette partie.

```bash
python -m pytest -v tests/test_td04_llm.py -k "todo_10_"
python -m pytest -v tests/test_td04.py tests/test_td04_llm.py
```

Résultat final attendu :

```text
14 passed pour les tests propres au TD04
```

Le lancement global `python -m pytest -v` inclut également tous les tests de
non-régression des TD précédents et doit produire `37 passed`.

## 7. Observer la transmission et les verdicts

### Ligne de commande

```bash
python main.py
```

Vous devez voir séparément :

1. le bilan du handoff TD03 → TD04 ;
2. les verdicts produits par le TD04.

### Interface

```bash
python -m streamlit run streamlit_app.py
```

L'interface affiche avant l'exécution :

- l'artefact JSON complet transmis par le TD03, consultable et téléchargeable ;
- sa provenance et son bilan de recherche ;
- le nombre de résultats bruts et uniques ;
- les articles avec et sans résumé ;
- les véritables titres et résumés transmis.

L'interface propose trois expériences :

```text
A : règles déterministes ─┐
                          ├─ C : comparaison → AUTO ou HUMAN
B : analyse LLM ──────────┘
```

- A et B peuvent être lancées séparément et dans n'importe quel ordre ;
- leurs résultats sont affichés côte à côte sans conclusion imposée, afin que
  les étudiants les interprètent ;
- C devient disponible lorsque les deux sorties existent ;
- C ne rappelle aucun agent : elle aligne les recommandations automatiques par
  `paper_id`, mesure les accords et désaccords, consulte les deux drapeaux
  `needs_human_review`, puis construit la file humaine ;
- une décision humaine déjà saisie dans A reste visible et finale dans A, mais
  C compare volontairement les sorties automatiques originales de A et B. C se
  situe donc avant l'arbitrage humain final dans cette expérience.

Pour les cas transmis à l'humain, la fiche affiche le titre, le résumé, la
source, le DOI, l'accès libre, le lien bibliographique, les signaux détectés et
la raison de l'escalade. L'évaluateur doit choisir `include`, `exclude` ou
`uncertain`, puis justifier sa décision. Cette justification est obligatoire :
elle matérialise la traçabilité du contrôle humain.

Si l'humain choisit `uncertain`, le papier n'est ni inclus ni exclu : il reste
en attente d'information supplémentaire ou d'une seconde évaluation.

Le bouton **Lire le résumé intégral** ouvre une fenêtre contenant tout le texte
utilisé par les deux agents dans une zone défilable. Une décision ne doit pas
être prise à partir du résumé tronqué visible dans le tableau général.

## 8. Questions d'interprétation

1. Pourquoi utiliser un artefact plutôt qu'importer directement le code du
   TD03 ?
2. Que garantit Pydantic lors du chargement ? Que ne garantit-il pas ?
3. Pourquoi certains papiers réels sans résumé n'empêchent-ils pas le
   chargement ?
4. Quelle différence existe entre un critère et un indicateur ?
5. Pourquoi séparer `observe_indicators()` et
   `apply_screening_policy()` ?
6. Pourquoi l'exclusion est-elle prioritaire dans cette politique ?
7. Pourquoi un papier sur le recrutement contenant le mot `screening` peut-il
   tromper l'agent déterministe ?
8. Pourquoi `uncertain` est-il préférable à une décision forcée ?
9. Pourquoi la confiance du TD n'est-elle pas une probabilité calibrée ?
10. Quelles limites de déduplication subsistent entre les résultats OpenAlex
    et Crossref de l'artefact réel ?
11. Comment améliorer le TD03 pour conserver le meilleur résumé de plusieurs
    sources ?
12. Quels verdicts le TD suivant doit-il utiliser pour décider quels PDF
    télécharger ?
13. Pourquoi le LLM peut-il mieux interpréter le contexte qu'une recherche par
    sous-chaîne ?
14. Pourquoi `with_structured_output()` ne garantit-il ni l'ancrage ni la
    pertinence scientifique de la preuve ?
15. Pourquoi un désaccord entre les deux agents doit-il être visible plutôt
    que résolu silencieusement ?
16. Un accord entre les deux agents suffit-il toujours pour automatiser ?
17. Pourquoi C est-il un mécanisme de coopération et non un troisième
    classifieur ?

## 9. Critères de réussite

- les 14 tests propres au TD04 et les 37 tests cumulatifs passent ;
- l'artefact est chargé et validé avant le screening ;
- aucun article n'est codé directement dans `main.py` ou le ScreeningAgent ;
- critères, indicateurs et verdicts restent séparés ;
- chaque article produit exactement un verdict justifié ;
- les cas incertains, conflictuels ou incomplets sont transférés à l'humain ;
- le LLM retourne une décision structurée dont l'ancrage de la preuve est contrôlé ;
- les accords et désaccords entre les deux versions sont visibles ;
- A et B restent exécutables indépendamment, tandis que C consomme leurs deux
  sorties sans les recalculer ;
- l'interface montre explicitement la transmission TD03 → TD04 ;
- l'étudiant sait expliquer comment l'instantané réel a été obtenu et proposer
  l'export automatique du `SearchState` comme amélioration de projet.
