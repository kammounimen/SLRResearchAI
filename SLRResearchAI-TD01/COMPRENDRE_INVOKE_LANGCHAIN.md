# Comprendre `invoke()` dans le TD01

## 1. Idée essentielle

Dans le TD01, nous n'avons pas programmé une nouvelle méthode `invoke()`.

L'instruction suivante appelle directement la méthode proposée par LangChain :

```python
response = model.invoke(messages)
```

Notre programme prépare l'entrée de cette méthode, déclenche l'appel, puis
exploite sa réponse.

---

## 2. D'où vient `invoke()` ?

LangChain définit une interface commune appelée `Runnable`. Elle représente un
composant que l'on peut exécuter sur une entrée pour obtenir une sortie.

Cette interface fournit notamment la méthode :

```python
invoke(input, config=None, **kwargs)
```

Les modèles `ChatGroq` et `ChatOllama` respectent cette interface. Ils peuvent
donc tous les deux être appelés avec la même syntaxe :

```python
response = model.invoke(messages)
```

La documentation générale peut être consultée dans le terminal :

```bash
python -m pydoc langchain_core.runnables.Runnable.invoke
```

---

## 3. Que représente `model` dans le TD ?

Dans `main.py`, le modèle est créé de cette manière :

```python
settings = Settings()
decoding = resolve_decoding(
    mode=DECODING_MODE,
    sampling_temperature=SAMPLING_TEMPERATURE,
    top_p=TOP_P,
    max_output_tokens=MAX_OUTPUT_TOKENS,
)
model = build_model(settings, decoding)
```

La fonction `build_model()` se trouve dans `slrresearch/config.py`. Elle examine
le fournisseur choisi dans `.env` :

```env
LLM_PROVIDER=groq
```

ou :

```env
LLM_PROVIDER=ollama
```

Elle construit ensuite l'objet correspondant :

```text
LLM_PROVIDER=groq
        ↓
    ChatGroq(...)

LLM_PROVIDER=ollama
        ↓
    ChatOllama(...)
```

La variable `model` contient donc un objet `ChatGroq` ou `ChatOllama`, et ces
deux objets possèdent la méthode LangChain `invoke()`.

---

## 4. Que transmettons-nous à `invoke()` ?

Le TD construit deux messages :

```python
messages = [
    SystemMessage(content=build_system_prompt()),
    HumanMessage(content=build_user_prompt(topic)),
]
```

Le `SystemMessage` contient les règles stables du modèle :

- son rôle ;
- son périmètre ;
- l'interdiction d'inventer ;
- la langue de réponse.

Le `HumanMessage` contient la demande variable :

- le sujet de la revue ;
- l'objectif ;
- le contexte ;
- les contraintes ;
- le format attendu.

Cette liste devient l'entrée de `invoke()` :

```python
response = model.invoke(messages)
```

---

## 5. Que fait LangChain pendant l'appel ?

LangChain adapte les mêmes messages au fournisseur sélectionné.

### Si Groq est sélectionné

```text
SystemMessage + HumanMessage
              ↓
      ChatGroq.invoke()
              ↓
         API Groq distante
              ↓
       AIMessage LangChain
```

### Si Ollama est sélectionné

```text
SystemMessage + HumanMessage
              ↓
     ChatOllama.invoke()
              ↓
      serveur Ollama local
              ↓
       AIMessage LangChain
```

Le code d'appel ne change donc pas lorsque l'on change de fournisseur :

```python
response = model.invoke(messages)
```

Seule la classe réelle contenue dans `model` change.

---

## 6. Que retourne `invoke()` ?

Pour un modèle de chat, `invoke()` retourne généralement un `AIMessage`
LangChain.

Le texte généré est disponible dans :

```python
response.content
```

Dans le TD, il est converti en chaîne et nettoyé :

```python
text = str(response.content).strip()
```

`.strip()` supprime les espaces et les sauts de ligne inutiles placés au début
ou à la fin de la réponse.

Certaines informations d'observation peuvent également être disponibles :

```python
response.usage_metadata
response.response_metadata
```

Elles peuvent contenir, selon le fournisseur :

- le nombre de tokens d'entrée ;
- le nombre de tokens de sortie ;
- la raison d'arrêt de la génération.

---

## 7. Quelle partie appartient à LangChain et quelle partie appartient au TD ?

### LangChain fournit

- `SystemMessage` et `HumanMessage` ;
- les classes `ChatGroq` et `ChatOllama` via leurs intégrations ;
- l'interface commune `Runnable` ;
- la méthode `invoke()` ;
- l'objet de réponse `AIMessage`.

### Notre TD réalise

- la lecture de `.env` ;
- le choix de Groq ou Ollama ;
- le réglage du décodage ;
- la construction des prompts ;
- la création des messages ;
- la mesure de la latence ;
- la récupération du texte et des métadonnées ;
- la conservation du résultat dans `FreeTextQuestions`.

La frontière apparaît dans ce code :

```python
# Notre code : préparer l'entrée
messages = build_zero_shot_messages(topic)
started = perf_counter()

# LangChain : exécuter le modèle
response = model.invoke(messages)

# Notre code : observer et conserver la sortie
latency = perf_counter() - started
text = str(response.content).strip()
```

---

## 8. Pourquoi cette abstraction est-elle utile ?

Sans interface commune, il faudrait écrire un appel différent pour chaque
fournisseur :

```python
if provider == "groq":
    response = appel_specifique_groq(...)
else:
    response = appel_specifique_ollama(...)
```

Avec LangChain, la construction du client dépend du fournisseur, mais son
utilisation reste uniforme :

```python
response = model.invoke(messages)
```

Cela facilite :

- le changement de fournisseur ;
- les tests avec un faux modèle ;
- la réutilisation du même code ;
- l'intégration future dans une chaîne ou un agent.

---

## 9. Pourquoi les tests utilisent-ils aussi `invoke()` ?

Le faux modèle du TD fournit la même opération minimale :

```python
class FakeModel:
    def invoke(self, messages):
        return SimpleNamespace(
            content="RQ1. Comment évaluer les LLM ?",
            usage_metadata={
                "input_tokens": 42,
                "output_tokens": 18,
            },
            response_metadata={"finish_reason": "stop"},
        )
```

Il ne contacte aucun vrai LLM. Il permet de vérifier que notre programme :

- prépare correctement les messages ;
- effectue exactement un appel ;
- récupère correctement la réponse ;
- conserve les métadonnées.

Le test évalue donc notre orchestration Python, pas la qualité scientifique
d'un modèle réel.

---

## 10. À retenir

> L'`invoke()` utilisé dans le TD est la méthode d'exécution standard de
> LangChain. Le TD ne la redéfinit pas : il construit son entrée et traite sa
> sortie.

Le flux complet est :

```text
.env
  ↓
Settings
  ↓
build_model()
  ↓
ChatGroq ou ChatOllama
  ↓
model.invoke(messages)
  ↓
AIMessage
  ↓
FreeTextQuestions
```

## Questions de compréhension

1. Pourquoi le même appel `model.invoke(messages)` fonctionne-t-il avec Groq
   et Ollama ?
2. Quelle partie du programme change lorsque l'on change de fournisseur ?
3. Quel est le rôle de `SystemMessage` et de `HumanMessage` ?
4. Où se trouve le texte produit par le modèle dans la réponse ?
5. Pourquoi le faux modèle peut-il tester notre code sans tester la qualité du
   LLM ?
