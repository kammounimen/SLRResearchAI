from dataclasses import dataclass
from time import perf_counter

from langchain_core.messages import HumanMessage, SystemMessage

#   Afin de réussir ce TD et de bien assimiler les concepts introduits, il est recommandé d’étudier le module "langchain_core.messages", notamment les classes SystemMessage, HumanMessage et AIMessage, ainsi que la méthode invoke(), qui constitue le mécanisme principal d’invocation des LLM.

@dataclass
class FreeTextQuestions:
    text: str
    provider: str
    latency_seconds: float
    system_prompt: str
    user_prompt: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    finish_reason: str | None = None


def build_system_prompt() -> str:
    """TODO 1.1 — Compléter les règles stables du modèle."""
    return (
        "Tu es un assistant méthodologique spécialisé dans les revues "
        "systématiques de la littérature (SLR). "
        "Tu dois strictement te limiter au périmètre du sujet fourni par "
        "l'utilisateur, sans t'écarter vers d'autres domaines. "
        "Tu ne dois jamais inventer de faits, de références bibliographiques "
        "ou de résultats d'études qui n'existent pas. "
        "Tu dois toujours répondre en français."
    )


def build_user_prompt(topic: str) -> str:
    """TODO 1.2 — Construire un prompt zero-shot en cinq rubriques."""
    clean_topic = topic.strip()
    if not clean_topic:
        raise ValueError("Sujet vide")
    return f"""[OBJECTIF]
Générer des questions de recherche (RQ) pertinentes, focalisées et directement exploitables pour une revue systématique de la littérature portant sur le sujet donné.

[CONTEXTE]
Ces questions serviront de base pour définir la stratégie de recherche bibliographique et les critères d'inclusion/exclusion d'une SLR.

[ENTRÉE]
Sujet de la revue : {clean_topic}

[CONTRAINTES]
Propose entre 3 et 5 questions de recherche, ouvertes et distinctes les unes des autres. N'utilise aucun format JSON. N'invente aucune référence ni aucun résultat. Réponds uniquement en français.

[SORTIE ATTENDUE]
Une liste de questions numérotées au format RQ1., RQ2., etc., rédigées en texte libre, sans commentaire additionnel."""


def build_zero_shot_prompt(topic: str) -> str:
    """Compatibilité avec le TD2 : renvoie le User Prompt du TD1."""
    return build_user_prompt(topic)


def build_zero_shot_messages(topic: str) -> list[SystemMessage | HumanMessage]:
    """TODO 1.3 — Construire [SystemMessage, HumanMessage]."""
    return [
        SystemMessage(content=build_system_prompt()),
        HumanMessage(content=build_user_prompt(topic)),
    ]
    

def _observable_metadata(response) -> tuple[int | None, int | None, str | None]:
    usage = getattr(response, "usage_metadata", None) or {}
    metadata = getattr(response, "response_metadata", None) or {}
    return (
        usage.get("input_tokens"),
        usage.get("output_tokens"),
        metadata.get("finish_reason") or metadata.get("done_reason"),
    )


def generate_questions(model, topic: str, provider: str = "demo") -> FreeTextQuestions:
    """TODO 1.4 — Effectuer exactement un appel et conserver le texte libre."""
    messages = build_zero_shot_messages(topic)
    started = perf_counter()

    response = model.invoke(messages)

    latency = perf_counter() - started
    text = str(response.content).strip()
    input_tokens, output_tokens, finish_reason = _observable_metadata(response)

    return FreeTextQuestions(
        text=text,
        provider=provider,
        latency_seconds=latency,
        system_prompt=str(messages[0].content),
        user_prompt=str(messages[1].content),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        finish_reason=finish_reason,
    )
