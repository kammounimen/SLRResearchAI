# TD03Bis — Du workflow outillé à l'agent ReAct contrôlé

## 1. Position du TD dans le projet

Le TD02 contrôlait une **donnée produite par le LLM** : des questions de
recherche devaient respecter un contrat avant de devenir exploitables.

Le TD03Bis contrôle maintenant une **décision d'action** : le système peut proposer
d'appeler un outil, mais cette proposition doit être validée, autorisée,
exécutée et transformée en observation.

```text
TD02                                    TD03Bis
texte LLM                                 objectif + état
   ↓                                          ↓
ResearchQuestion validée                 AgentAction proposée
   ↓                                          ↓
requêtes scientifiques                  validation Pydantic
                                              ↓
                                         registre d'outils
                                              ↓
                                      exécution ou refus
                                              ↓
                                         Observation
```

Le TD03Bis charge réellement `artifacts/search_plan.json` avec
`load_search_plan()`. Pour éviter de refaire le TD02 pendant cette séance, le
fichier distribué contient des requêtes préremplies et porte
`origin="pedagogical_seed"`. Il respecte néanmoins le même contrat Pydantic que
l'artefact exportable par le TD02. Le TD03Bis ne reconstruit jamais les
requêtes. La procédure facultative de continuité complète est détaillée dans
`CONTINUITE_REELLE_TD02.md`.

## 2. Question centrale

Où se trouve la décision concernant le prochain outil ?

### Version A — Workflow outillé contrôlé

```python
for tool_name, query in queries.items():
    # Le programme impose l'ordre des outils.
```

La logique Python connaît à l'avance toutes les étapes.

### Version B — SearchAgent ReAct contrôlé

```text
décider → valider → autoriser → agir → observer → mettre l'état à jour
   ↑                                                               |
   └───────────────────────────────────────────────────────────────┘
```

Le décideur choisit l'action suivante à partir de l'objectif, de l'état et des
observations précédentes. Le programme conserve toutefois la frontière de
contrôle : le LLM ne lance jamais directement un outil.

## 3. Objectifs pédagogiques

À la fin du TD, vous devez savoir :

1. distinguer workflow outillé et agent ReAct ;
2. représenter une décision avec un contrat Pydantic `AgentAction` ;
3. appliquer une liste blanche d'outils avec un registre ;
4. transformer succès, résultat vide, erreur et refus en `Observation` ;
5. distinguer état du système et contexte exposé au LLM ;
6. conserver une trace action–observation ;
7. écrire une baseline déterministe ;
8. demander au LLM de proposer une action sans lui donner l'exécution ;
9. borner une boucle ReAct par `max_steps`, `finish` et une règle d'arrêt ;
10. expliquer comment une observation modifie une décision ultérieure.

## 4. Organisation des fichiers

Vous complétez uniquement :

```text
slrresearch/contracts.py    # TODO 1
slrresearch/tools.py        # TODO 2
slrresearch/real_tools.py   # TODO 3
slrresearch/runtime.py      # TODO 4 et TODO 5
slrresearch/workflow.py     # TODO 6
slrresearch/policies.py     # TODO 7
slrresearch/react_agent.py  # TODO 8, exercice difficile
```

Les fichiers suivants sont fournis :

- `slrresearch/research_questions.py` : acquis complet du TD01, conservé sans
  nouveau travail demandé ;
- `slrresearch/search_plan.py` : acquis complet du TD02, conservé sans nouveau
  travail demandé ;
- `artifacts/search_plan.json` : artefact réellement lu, prérempli pour ce TD ;
- `slrresearch/handoff.py` : contrat et validation du handoff TD02 → TD03Bis ;
- `slrresearch/demo.py` : outils locaux et politique reproductible ;
- `slrresearch/config.py` : sélection Groq/Ollama ;
- `main.py` : comparaison en terminal ;
- `streamlit_app.py` : comparaison visuelle ;
- `data/papers.json` : petit catalogue pédagogique ;
- `tests/test_td03.py` : contrat exécutable des TODO.

## 5. Installation et premier diagnostic

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m pytest --collect-only -q
```

Les tests échouent au départ à cause des `NotImplementedError`. Ne commencez
pas par l'interface : avancez TODO par TODO avec les tests ciblés.

---

# Partie A — Définir la frontière de contrôle

## TODO 1 — Valider le contrat `AgentAction`

**Fichier :** `slrresearch/contracts.py`  
**Fonction :** `AgentAction.validate_action_arguments()`

Le modèle possède quatre champs :

```python
action: Literal["search", "finish"]
tool: str | None
query: str | None
limit: int | None
```

Les types seuls ne suffisent pas. Par exemple, `tool` est optionnel pour que
`finish` puisse l'omettre, mais il devient obligatoire lorsque
`action="search"`. Le TODO contrôle donc la **cohérence entre les champs**.

Le décorateur `@model_validator(mode="after")` indique que Pydantic a déjà
contrôlé les types. Vous travaillez sur l'objet `self`, vous pouvez consulter
ses quatre attributs et vous devez retourner `self` si tout est cohérent.

Vous modifiez uniquement :

```text
slrresearch/contracts.py
└── AgentAction.validate_action_arguments()
```

### Règles

| Action | `tool` | `query` | `limit` |
|---|---|---|---|
| `search` | obligatoire | chaîne non vide | obligatoire, entre 1 et 20 |
| `finish` | doit être `None` | doit être `None` | doit être `None` |

### Étape 1.1 — Retirer l'exception provisoire

Repérez exactement :

```python
@model_validator(mode="after")
def validate_action_arguments(self):
    """TODO 1 - Appliquer les règles conditionnelles search/finish."""
    # search exige tool, query non vide et limit.
    # finish interdit ces trois arguments.
    raise NotImplementedError
```

Supprimez uniquement `raise NotImplementedError`, puis écrivez les contrôles à
sa place.

### Étape 1.2 — Valider une action `search`

Une recherche complète ressemble à ceci :

```python
AgentAction(
    action="search",
    tool="openalex",
    query="LLM AND systematic review",
    limit=5,
)
```

Commencez par `if self.action == "search":`, puis appliquez trois contrôles :

1. `if not self.tool` refuse un outil absent ou vide ;
2. `if not self.query or not self.query.strip()` refuse une requête absente,
   vide ou composée uniquement d'espaces ;
3. `if self.limit is None` refuse une limite absente.

La contrainte `1 <= limit <= 20` est déjà appliquée par `Field`.

### Étape 1.3 — Valider une action `finish`

Une demande d'arrêt correcte est `AgentAction(action="finish")`. Dans la
branche `else`, levez une `ValueError` si **au moins un** argument est présent :

```python
else:
    if (
        self.tool is not None
        ___ self.query is not None
        ___ self.limit is not None
    ):
        raise ValueError(
            "finish ne doit contenir aucun argument d'outil"
        )
```

Remplacez les blancs par l'opérateur logique correspondant à « au moins un ».
`and` serait incorrect, car un seul argument présent doit déjà être refusé.

### Étape 1.4 — Retourner le modèle

Ajoutez `return self` après les deux branches, aligné avec le premier `if`.

### Travail demandé, en résumé

Dans le validateur `mode="after"` :

1. remplacer `NotImplementedError` par les deux branches ;
2. lever `ValueError` pour chaque combinaison incohérente ;
3. utiliser `.strip()` pour les espaces ;
4. terminer par `return self`.

### Squelette

```python
if self.action == "search":
    if not self.tool:
        raise ValueError("...")
    if not self.query or not self.query.________():
        raise ValueError("...")
    if self.limit is None:
        raise ValueError("...")
else:
    if (
        self.tool is not None
        ___ self.query is not None
        ___ self.limit is not None
    ):
        raise ValueError("...")

return self
```

Remplacez les blancs grâce aux explications précédentes. Le contrôle de
`limit` est déjà donné entièrement. Ces actions doivent
réussir :

```python
AgentAction(action="search", tool="openalex", query="LLM AND SLR", limit=5)
AgentAction(action="finish")
```

Celles-ci doivent échouer :

```python
AgentAction(action="search", tool=None, query="LLM", limit=5)
AgentAction(action="search", tool="openalex", query="   ", limit=5)
AgentAction(action="search", tool="openalex", query="LLM", limit=None)
AgentAction(action="finish", tool="openalex")
AgentAction(action="finish", query="LLM")
AgentAction(action="finish", limit=5)
```

Ne lancez aucun outil ici. L'autorisation et l'exécution appartiennent aux
TODO 2 et 3.

```bash
python -m pytest -v -k "todo_1"
```

Résultat attendu : deux tests `PASSED`. Si `NotImplementedError` apparaît
encore, la mauvaise ligne a été modifiée. Si `finish` accepte un seul argument,
vérifiez l'opérateur logique utilisé.

---

## TODO 2 — Autoriser un outil avec `ToolRegistry`

**Fichier :** `slrresearch/tools.py`  
**Méthode :** `ToolRegistry.authorize()`

Le registre est construit par :

```python
self._tools = {tool.name: tool for tool in tools}
```

Il constitue une liste blanche. Un nom proposé par le LLM n'est jamais utilisé
directement pour importer une fonction ou exécuter une commande.

### Travail demandé

1. refuser `None` ;
2. refuser un nom absent de `self._tools` ;
3. lever `ToolNotAllowedError` dans les deux cas ;
4. sinon retourner `self._tools[tool_name]`.

### Hint

```python
if tool_name is None or tool_name not in self._tools:
    raise ______________________(f"Outil non autorisé : {tool_name}")

return ______________________
```

```bash
python -m pytest -v -k "todo_2"
```

### Question intermédiaire

Pourquoi valider `tool: str` avec Pydantic ne suffit-il pas pour autoriser
l'outil ?

---

## TODO 3 — Configurer et enregistrer de vrais outils scientifiques

**Fichier :** `slrresearch/real_tools.py`  
**Fonctions :** `semantic_scholar_search()` et `build_real_registry()`

Le mode local sert aux tests reproductibles. Ce TODO ajoute les véritables API
OpenAlex, Crossref et Semantic Scholar. OpenAlex et Crossref sont fournis comme
exemples dans `tools.py` ; vous complétez Semantic Scholar et le registre.

### TODO 3.1 — Compléter l'appel HTTP

Dans l'appel `httpx.get`, utilisez :

1. `SEMANTIC_SCHOLAR_URL` comme URL ;
2. `query` pour le paramètre `query` ;
3. `limit` pour le paramètre `limit`.

Le code fourni normalise ensuite `paperId`, `title`, `abstract`, DOI, URL et
accès ouvert dans le format commun.

### TODO 3.2 — Construire le registre réel

Complétez :

```python
return ToolRegistry(
    [
        SearchTool("openalex", __________________),
        SearchTool("crossref", __________________),
        SearchTool("semantic_scholar", __________________),
    ]
)
```

Utilisez `openalex_search`, `crossref_search` et `semantic_scholar_search`, sans
parenthèses.

```bash
python -m pytest -v -k "todo_3"
```

Les tests simulent HTTP. Après leur réussite, sélectionnez **API scientifiques
réelles** dans Streamlit. Les erreurs réseau et HTTP 429 sont normales dans un
système externe et seront converties en observations au TODO 4.

---

# Partie B — Agir et observer

## TODO 4 — Exécuter une action autorisée

**Fichier :** `slrresearch/runtime.py`  
**Fonction :** `execute_authorized_action()`

Cette fonction représente la frontière d'exécution. Elle reçoit une action
déjà structurée, mais elle doit encore demander l'autorisation au registre.

Elle ne doit pas laisser une erreur `httpx` interrompre la boucle. Toute issue
devient une `Observation`.

Le corps est presque entièrement fourni. L'étudiant écrit seulement les deux
lignes centrales des slides : autoriser puis exécuter.

```python
tool = registry.________________(action.tool)
raw_papers = tool.________________(action.query or "", action.limit or 1)
```

### Comprendre le contrat de la fonction

```text
AgentAction → autorisation → SearchTool → tool.search → Observation
```

La fonction doit toujours retourner une observation et contenir deux blocs
`try` : autorisation, puis appel externe.

### Cas à traiter

| Situation | `Observation.status` |
|---|---|
| outil refusé | `unauthorized` |
| au moins un article | `success` |
| liste vide | `empty` |
| HTTP 429 | `rate_limited` |
| autre erreur HTTP | `http_error` |
| erreur réseau | `network_error` |

### Code fourni — chronométrer

```python
started = perf_counter()
```

### Ligne à compléter 4.1 — autoriser

```python
try:
    tool = registry.authorize(action.tool)
except ToolNotAllowedError as exc:
    return Observation(
        tool=action.tool,
        status="unauthorized",
        latency_seconds=perf_counter() - started,
        error=str(exc),
    )
```

### Ligne à compléter 4.2 — appeler, puis normalisation fournie

```python
try:
    raw_papers = tool.search(action.query or "", action.limit or 1)
    papers = [
        PaperRecord(source=tool.name, **raw_paper)
        for raw_paper in raw_papers
    ]
```

### Code fourni — retourner succès ou liste vide

```python
return Observation(
    tool=tool.name,
    status="success" if papers else "empty",
    count=len(papers),
    latency_seconds=perf_counter() - started,
    papers=papers,
)
```

### Code fourni — traiter les statuts HTTP

```python
except httpx.HTTPStatusError as exc:
    status_code = exc.response.status_code
    return Observation(
        tool=tool.name,
        status="rate_limited" if status_code == 429 else "http_error",
        latency_seconds=perf_counter() - started,
        error=f"HTTP {status_code}",
    )
```

### Code fourni — traiter le réseau

```python
except httpx.HTTPError as exc:
    return Observation(
        tool=tool.name,
        status="network_error",
        latency_seconds=perf_counter() - started,
        error=str(exc),
    )
```

Placez `HTTPStatusError` avant `HTTPError`. `tool` doit être défini par
l'autorisation et `raw_paper` dans la compréhension de liste.

### Tests progressifs

```bash
python -m pytest -v -k "todo_4_execution_distingue"
python -m pytest -v -k "todo_4_execution_transforme_http_429"
python -m pytest -v -k "todo_4"
```

---

## TODO 5 — Mettre à jour `SearchState`

**Fichier :** `slrresearch/runtime.py`  
**Fonction :** `update_state()`

Une observation n'est utile à ReAct que si elle modifie un état persistant.

### Champs à mettre à jour

```text
step              +1 à chaque observation
actions_executed  action valide, si elle existe
observations      observation reçue
trace             couple action–observation numéroté
errors            message si observation.error existe
papers            articles uniques accumulés
```

### Déduplication

La déduplication, les erreurs, `step` et `actions_executed` sont fournis.

### Travail étudiant — deux noms de champs

```python
state.________________.append(observation)
state.________________.append(
    TraceEvent(step=state.step, action=action_dump, observation=observation)
)
```

Retrouvez les deux noms dans `SearchState`.

```bash
python -m pytest -v -k "todo_5"
```

### Point d'exécution A

À ce stade, vous avez le cadre sécurisé, mais aucune politique de parcours.
Vérifiez :

```bash
python -m pytest -v -k "todo_1 or todo_2 or todo_3 or todo_4 or todo_5"
```

---

# Partie C — Construire la baseline déterministe

## TODO 6 — Implémenter le workflow outillé

**Fichier :** `slrresearch/workflow.py`  
**Fonction :** `run_tool_workflow()`

Ici, le programme choisit les actions. Pour chaque entrée de `queries`, il
construit une action `search`, exécute l'outil puis met l'état à jour.

### Étapes

1. créer `SearchState(objective=objective, queries=queries)` ;
2. parcourir `queries.items()` ;
3. créer `AgentAction(action="search", ...)` ;
4. appeler `execute_authorized_action()` ;
5. appeler `update_state()` ;
6. après la boucle, positionner `finished=True` ;
7. positionner `stop_reason="workflow_complete"` ;
8. retourner l'état.

### Squelette

```python
state = SearchState(objective=objective, queries=queries)

for tool_name, query in queries.________():
    action = AgentAction(
        action="search",
        tool=________,
        query=________,
        limit=limit,
    )
    observation = ______________________________
    ______________________________

state.finished = ________
state.stop_reason = "________________"
return state
```

Le workflow doit continuer après un HTTP 429 puisque l'erreur est devenue une
observation.

```bash
python -m pytest -v -k "todo_6"
python main.py
```

Dans la Version A, vérifiez que les trois outils sont visités dans l'ordre des
requêtes, même si le premier échoue.

---

# Partie D — Demander une décision sans céder l'exécution

## TODO 7 — Construire la politique de décision LLM

Le prompt complet est fourni. L'étudiant écrit seulement l'appel LLM et
l'extraction de la décision.

### Code fourni — construire le prompt de décision

**Fichier :** `slrresearch/policies.py`  
**Fonction :** `build_decision_prompt()`

Le prompt ne doit pas recevoir automatiquement tout l'objet `SearchState`.
`state_for_decision()` produit une projection contenant seulement les éléments
utiles : objectif, requêtes, nombre d'articles, outils déjà appelés, dernière
observation et numéro d'étape.

Le prompt fourni inclut :

- l'objectif ;
- la projection JSON de l'état ;
- la liste des outils autorisés ;
- un exemple JSON `search` ;
- un exemple JSON `finish` ;
- la règle d'adaptation après une erreur ou un résultat vide ;
- l'interdiction d'exécuter directement un outil ;
- l'interdiction d'ajouter du Markdown ou une explication.

Il utilise :

```python
json.dumps(state_for_decision(state), ensure_ascii=False, indent=2)
json.dumps(allowed_tools, ensure_ascii=False)
```

### Travail étudiant — deux lignes

**Classe :** `LLMDecisionPolicy`  
**Méthode :** `__call__()`

Cette méthode doit :

1. construire le prompt ;
2. appeler `self.model.invoke(prompt)` exactement une fois ;
3. récupérer `response.content` ;
4. appeler `extract_json_object()` ;
5. retourner le dictionnaire, sans appeler d'outil.

```python
response = self.model.________________(
    build_decision_prompt(state, allowed_tools)
)
return ______________________________(str(response.content))
```

Complétez avec `invoke` et la fonction d'extraction définie juste au-dessus.

Ces deux lignes matérialisent `action = llm_decide(state, tools)` présenté dans
les slides. `LLMDecisionPolicy` propose l'action mais ne l'exécute pas.

La validation `AgentAction` sera effectuée par le runtime, pas par la politique.

```bash
python -m pytest -v -k "todo_7"
```

---

# Partie E — Exercice de synthèse difficile

## TODO 8 — Implémenter la boucle ReAct contrôlée

**Fichier :** `slrresearch/react_agent.py`  
**Fonction :** `run_react_agent()`

Ce dernier TODO est volontairement beaucoup plus difficile. Il mobilise tous
les contrats précédents. Aucun bloc complet prêt à copier n'est fourni.

### Invariants obligatoires

Votre boucle doit garantir simultanément que :

1. le décideur reçoit l'état courant et `registry.names` ;
2. toute proposition passe par `AgentAction.model_validate()` ;
3. une action invalide devient une observation `invalid_action` ;
4. `finish` arrête sans appeler d'outil ;
5. `search` passe toujours par `execute_authorized_action()` ;
6. toute observation passe par `update_state()` ;
7. atteindre `target_papers` arrête immédiatement ;
8. l'absence de `finish` ne permet jamais de dépasser `max_steps` ;
9. une erreur 429, un outil interdit ou une action invalide n'arrête pas
   automatiquement la boucle ;
10. `stop_reason` indique exactement la cause de l'arrêt.

### Valeurs de `stop_reason`

| Cause | Valeur |
|---|---|
| le décideur propose `finish` | `agent_finish` |
| assez d'articles uniques | `target_reached` |
| budget d'étapes épuisé | `max_steps` |

### TODO 8.1 — Initialiser l'état

Créez un `SearchState` avec l'objectif et les requêtes. Ne stockez pas l'état
dans une variable globale.

### TODO 8.2 — Borner la boucle

Utilisez une boucle qui ne peut exécuter que `max_steps` tours. Une boucle
`while True` est interdite.

### TODO 8.3 — Décider puis valider

À chaque tour :

```text
raw_action = decide(état courant, outils autorisés)
                    ↓
AgentAction.model_validate(raw_action)
```

Capturez seulement les erreurs de validation attendues. Construisez alors :

```python
Observation(
    status="invalid_action",
    error=str(exc),
    raw_action=...,
)
```

Appelez `update_state()` avec `action=None`, puis passez au tour suivant.

### TODO 8.4 — Traiter `finish`

Une action `finish` est valide mais n'est pas une action d'outil :

- ajoutez-la à `actions_executed` ;
- incrémentez `step` ;
- positionnez `finished=True` ;
- choisissez la bonne raison d'arrêt ;
- retournez immédiatement l'état ;
- n'appelez ni le registre ni `update_state()` puisqu'il n'existe aucune
  observation d'outil.

### TODO 8.5 — Exécuter et observer

Pour une action `search` :

1. appelez `execute_authorized_action(action, registry)` ;
2. appelez `update_state(state, action, observation)` ;
3. testez ensuite `len(state.papers) >= target_papers` ;
4. si vrai, terminez avec la raison correspondante.

### TODO 8.6 — Fermer la boucle

Si la boucle se termine sans `finish` et sans atteindre la cible :

- positionnez `finished=True` ;
- utilisez la raison indiquant l'épuisement du budget ;
- retournez l'état.

### Pseudocode global

```text
créer state

pour au maximum max_steps tours :
    demander raw_action

    essayer de construire AgentAction
    si validation impossible :
        créer observation invalid_action
        mettre state à jour
        continuer

    si action == finish :
        enregistrer l'arrêt
        retourner state

    observation = contrôler et exécuter search
    mettre state à jour

    si cible atteinte :
        enregistrer l'arrêt
        retourner state

enregistrer max_steps
retourner state
```

### Tests progressifs du TODO difficile

```bash
python -m pytest -v -k "todo_8_finish"
python -m pytest -v -k "todo_8_observation_429"
python -m pytest -v -k "todo_8_action_invalide"
python -m pytest -v -k "todo_8_outil_interdit"
python -m pytest -v -k "todo_8_target_reached"
python -m pytest -v -k "todo_8_max_steps"
```

Puis :

```bash
python -m pytest -v -k "todo_8"
```

### Scénario clé

Le test adaptatif impose cette trajectoire :

```text
1. search(openalex)
2. Observation(status="rate_limited")
3. search(crossref)
4. Observation(status="success")
5. finish
```

Le workflow A appelle simplement toutes les sources. L'agent B reçoit
l'observation 429 avant que la politique ne propose l'action suivante.

### Pourquoi la politique reproductible et le LLM peuvent-ils s'arrêter différemment ?

Les deux modes de la Version B utilisent exactement la même boucle ReAct, le
même état et les mêmes outils. **Seule la politique qui propose la prochaine
action change.**

| Mode | Choix de l'action suivante | Condition d'arrêt observée dans ce TD |
|---|---|---|
| Version A — workflow | ordre fixé dans le code | toutes les sources sont appelées |
| Version B — politique reproductible | règles Python de `build_demo_policy()` | succès d'OpenAlex, ou tentative de Crossref après l'échec d'OpenAlex |
| Version B — LLM réel | interprétation du prompt à partir de l'état | le LLM peut estimer qu'une autre source reste utile avant `finish` |

Dans le scénario HTTP 429, la politique reproductible suit volontairement :

```text
OpenAlex (429) → Crossref (succès) → finish
```

Elle n'appelle donc pas Semantic Scholar. Le LLM réel peut, lui, proposer
Semantic Scholar après Crossref, car le prompt lui demande de terminer quand
il dispose d'« assez d'articles ». Ce critère est ambigu : le LLM peut juger
qu'une seule source réussie ne donne pas encore une couverture suffisante.

Cette différence ne prouve pas que le LLM possède une meilleure stratégie. La
boucle ReAct exécute la politique qu'elle reçoit. Dans une véritable SLR, une
condition aussi importante doit être mesurable et reproductible. Une politique
hybride pourrait, par exemple, n'autoriser `finish` que si :

- au moins deux sources ont répondu avec succès ;
- ou toutes les sources autorisées ont été essayées ;
- tandis que `max_steps` conserve son rôle de garde-fou ultime.

Le LLM peut alors proposer l'ordre des outils, mais le programme garde le
contrôle de la couverture minimale.

---

## 6. Validation finale

```bash
python -m pytest -v
python main.py
python -m streamlit run streamlit_app.py
```

Résultat attendu :

```text
23 passed
```

Dans Streamlit :

1. gardez le scénario `OpenAlex répond HTTP 429` ;
2. exécutez la Version A ;
3. exécutez la Version B en politique reproductible ;
4. comparez les traces ;
5. vérifiez qui choisit l'action suivante ;
6. seulement ensuite, essayez le mode LLM réel configuré dans `.env`.

## 7. Questions d'interprétation

1. Où la décision de l'outil est-elle prise dans la Version A ?
2. Où est-elle prise dans la Version B ?
3. Pourquoi `AgentAction` ne doit-elle pas exécuter elle-même l'outil ?
4. Pourquoi Pydantic ne remplace-t-il pas `ToolRegistry` ?
5. Quelle différence existe entre une erreur et une observation d'erreur ?
6. Pourquoi un résultat vide doit-il être conservé dans l'état ?
7. Pourquoi l'état complet n'est-il pas automatiquement envoyé au LLM ?
8. Comment un HTTP 429 peut-il modifier la prochaine décision ?
9. Pourquoi `finish` ne produit-il pas une observation d'outil ?
10. Que protège `max_steps` ?
11. Quelle différence existe entre `target_reached` et `agent_finish` ?
12. Pourquoi les tests utilisent-ils `ScriptedPolicy` plutôt qu'un vrai LLM ?
13. La politique reproductible est-elle réellement intelligente ?
14. À partir de quel moment peut-on raisonnablement parler d'agent dans ce TD ?
15. Pourquoi ReAct contrôlé ne signifie-t-il pas autonomie illimitée ?
16. Le LLM appelle Semantic Scholar alors que la politique reproductible peut
    s'arrêter après Crossref. Cette différence prouve-t-elle que le LLM possède
    une meilleure stratégie ? Proposez une condition d'arrêt hybride,
    mesurable et reproductible.
17. Pourquoi les tests des outils réels remplacent-ils `httpx.get`, alors que
    la validation finale dans Streamlit doit appeler les véritables API ?

## 8. Critères de réussite

- les 23 tests passent, dont 3 vérifient le handoff JSON, 2 la présence des
  acquis TD01–TD02 et 2 la configuration des outils réels ;
- les requêtes du TD02 ne sont pas recopiées dans l'agent ;
- le contrat distingue strictement `search` et `finish` ;
- seuls les outils du registre sont exécutables ;
- toute issue externe devient une observation structurée ;
- l'état conserve actions, observations, erreurs et articles uniques ;
- la Version A montre une décision prédéfinie ;
- la Version B montre une décision répétée à partir de l'état ;
- la boucle respecte les trois conditions d'arrêt ;
- l'interface rend la comparaison visible ;
- l'étudiant peut expliquer chaque ligne du TODO 8.
