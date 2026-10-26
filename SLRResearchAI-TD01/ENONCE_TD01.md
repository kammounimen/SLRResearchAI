# TD01 — Prompting et contrôle du décodage

## 1. Mission

À partir d'un sujet scientifique, effectuer **un seul appel LLM** et produire 3
à 5 questions de recherche en texte libre.

Objectifs : construire un prompt zero-shot, appeler Ollama ou Groq, comparer
greedy et sampling, puis étudier l'effet de la température.

## 2. Fichiers

- `slrresearch/research_questions.py` : TODO 1.1 à 1.4.
- `main.py` : TODO 2.1 et 2.2.
- `slrresearch/config.py` : lire seulement.
- `streamlit_app.py` et `tests/test_td01.py` : ne pas modifier.

## 3. Ollama ou Groq ?

- **Ollama** : local, confidentiel et utilisable hors-ligne après installation.
- **Groq** : distant et léger, mais Internet et clé API requis.

Choisissez dans `.env` : `LLM_PROVIDER=ollama` ou `LLM_PROVIDER=groq`.

## 4. Partie 1 — Construire le prompt et appeler le LLM

Fichier : `slrresearch/research_questions.py`.

### TODO 1.1 — System Prompt

Complétez le périmètre, le garde-fou et la langue :

```python
def build_system_prompt() -> str:
    return (
        "Tu es un expert en méthodologie de recherche académique, spécialisé dans la conduite de Revues Systématiques de la Littérature (SLR)."
        "Tu doit strictement te limiter au périmètre __________________. "
        "Tu ne dois jamais inventer ____________________. " 
        "Tu dois toujours répondre en ____________________."
    )
```

### TODO 1.2 — User Prompt

Complétez les cinq rubriques déjà présentes :

```python
return f"""[OBJECTIF]
___

[CONTEXTE]
___

[ENTRÉE]
Sujet de la revue : {clean}

[CONTRAINTES]
___

[SORTIE ATTENDUE]
___"""
```

Contrat : demander 3 à 5 questions ouvertes et distinctes, expliquer leur usage
futur, interdire le JSON et imposer la numérotation `RQ1.`, `RQ2.`, etc.

### TODO 1.3 — Construire les messages

# Cette partie nécessitel'étude du module "langchain_core.messages", notamment les classes SystemMessage, HumanMessage et AIMessage. 

```python
return [
    SystemMessage(content=___),
    HumanMessage(content=___),
]
```

Utilisez les deux fonctions précédentes. Les valeurs de `content` doivent être
des résultats d'appels de fonction.

### TODO 1.4 — Effectuer un appel unique
# ici vous avez besoin de regarder comment la méthode "invoke()" fonctionne. 


```python
response = model.___(messages)
text = str(response.___).strip()

return FreeTextQuestions(
    text=___,
    provider=___,
    latency_seconds=___,
    system_prompt=str(messages[0].content),
    user_prompt=str(messages[1].content),
    input_tokens=___,
    output_tokens=___,
    finish_reason=___,
)
```

Appelez le modèle une seule fois avec `model.invoke(messages)`. Récupérez le
texte dans `response.content`, convertissez-le en chaîne et nettoyez ses espaces
avec `.strip()`. Dans `FreeTextQuestions`, utilisez les variables déjà calculées
juste au-dessus. Retirez ensuite `raise NotImplementedError(...)`.

### Vérifier la partie 1

```bash
python -m pytest -v
python main.py
 python -m streamlit run streamlit_app.py
```

Résultat attendu après réalisation complète : `4 passed`.

À discuter :

1. Pourquoi le sujet appartient-il au User Prompt ?
2. Quel rôle joue chaque rubrique ?
3. Pourquoi ce prompt reste-t-il zero-shot ?
4. Que vérifie réellement le faux modèle des tests ?

## 5. Partie 2 — Observer le décodage

Fichier : `main.py`.

Les constantes sont utilisées ici :

```python
decoding = resolve_decoding(
    mode=DECODING_MODE,
    sampling_temperature=SAMPLING_TEMPERATURE,
    top_p=TOP_P,
    max_output_tokens=MAX_OUTPUT_TOKENS,
)
model = build_model(settings, decoding)
```

`resolve_decoding()` calcule les paramètres effectifs ; `build_model()` les
transmet à Ollama ou Groq.

### TODO 2.1 — Greedy contre sampling

Avec le même sujet, effectuez trois essais avec :

```python
DECODING_MODE = "greedy"
```

Puis trois essais avec :

```python
DECODING_MODE = "sampling"
```

Cette comparaison porte sur deux stratégies complètes de décodage : plusieurs
paramètres peuvent changer ensemble.

### TODO 2.2 — Effet de la température

Conservez obligatoirement :

```python
DECODING_MODE = "sampling"
TOP_P = 0.9
MAX_OUTPUT_TOKENS = 400
```

Effectuez trois essais avec :

```python
SAMPLING_TEMPERATURE = 0.2
```

Puis trois essais avec :

```python
SAMPLING_TEMPERATURE = 0.8
```

Ici, seule la température change : les différences peuvent donc lui être
attribuées plus raisonnablement.

Après chaque modification, relancez :

```bash
python -m streamlit run streamlit_app.py
```

L'interface affiche les paramètres provenant de `main.py` sans permettre de les
modifier.

| Expérience | Configuration | Essai | Nb RQ | Format correct ? | Variation |
|---|---|---:|---:|---|---|
| Stratégie | greedy | 1–3 | | | |
| Stratégie | sampling, T=0.8 | 1–3 | | | |
| Température | sampling, T=0.2 | 1–3 | | | |
| Température | sampling, T=0.8 | 1–3 | | | |

À discuter :

5. Quel mode produit les réponses les plus stables ?
6. Quel effet observez-vous entre les températures 0.2 et 0.8 ?
7. La température rend-elle le modèle plus intelligent ?
8. Pourquoi conserver le même sujet, le même modèle et le même top-p ?
9. Pourquoi la sortie libre devra-t-elle être validée au TD2 ?

## 6. Critères de réussite

- `4 passed` ;
- deux messages et un seul appel LLM ;
- trois essais greedy et trois essais sampling ;
- deux séries en sampling avec températures 0.2 et 0.8 ;
- paramètres visibles dans Streamlit ;
- observations interprétées pendant la discussion.
