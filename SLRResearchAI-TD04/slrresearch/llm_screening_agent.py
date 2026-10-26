from typing import Literal
import re
import unicodedata

from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field, field_validator

from slrresearch.artifacts import PaperRecord
from slrresearch.screening_agent import ScreeningDecision


class LLMScreeningDecision(BaseModel):
    paper_id: str
    decision: Literal["include", "exclude", "uncertain"]
    confidence: float = Field(ge=0, le=1)
    reasons: list[str] = Field(min_length=1)
    evidence: str = Field(
        description=(
            "Courte preuve copiée du titre ou du résumé ; son ancrage lexical "
            "sera contrôlé localement"
        )
    )
    needs_human_review: bool

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, value):
        """Accepte 0..1 ou un pourcentage 0..100, puis stocke 0..1."""
        number = float(value)
        if 1 < number <= 100:
            return number / 100
        return number


class ComparisonResult(BaseModel):
    paper_id: str
    deterministic_decision: Literal["include", "exclude", "uncertain"]
    llm_decision: Literal["include", "exclude", "uncertain"]
    agreement: bool
    needs_human_review: bool
    escalation_reason: str


def normalize_for_matching(text: str) -> str:
    """Code fourni — neutralise les variations sans modifier le sens lexical."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    normalized = re.sub(r"[^\w%]+", " ", normalized, flags=re.UNICODE)
    return " ".join(normalized.split())


def build_screening_messages(
    paper: PaperRecord,
    topic: str,
    inclusion_terms: set[str],
    exclusion_terms: set[str],
) -> list:
    """TODO 7 — Construire le contexte et les instructions du LLM."""
    # Le SystemMessage doit définir le rôle, les trois décisions autorisées,
    # l'interdiction d'inventer, une confiance entre 0 et 1 et l'obligation
    # de citer le texte fourni.
    system_prompt = "..."

    # Le HumanMessage doit contenir le sujet, les critères, l'identifiant,
    # le titre et le résumé du papier.
    user_prompt = "..."
    return [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]


def invoke_structured_screening(
    model,
    paper: PaperRecord,
    topic: str,
    inclusion_terms: set[str],
    exclusion_terms: set[str],
) -> LLMScreeningDecision:
    """TODO 8 — Effectuer exactement un appel LLM structuré."""
    # La construction des messages et la restitution de l'identifiant sont fournies.
    messages = build_screening_messages(
        paper, topic, inclusion_terms, exclusion_terms
    )

    # TODO 8 — Le schéma est fourni ; compléter uniquement la méthode d'appel.
    structured_model = model.with_structured_output(LLMScreeningDecision)
    decision = structured_model.________(messages)

    # L'identifiant technique appartient à l'application, pas au LLM.
    return decision.model_copy(update={"paper_id": paper.id})


def validate_grounding(paper: PaperRecord, decision: LLMScreeningDecision) -> None:
    """TODO 9 — Contrôler l'ancrage de la preuve dans le titre et le résumé."""
    # La normalisation technique est fournie : compléter seulement la règle.
    source_text = normalize_for_matching(f"{paper.title} {paper.abstract}")
    evidence = decision.evidence.strip()
    normalized_evidence = normalize_for_matching(evidence)

    # TODO 9a — True seulement si la preuve est vide ET le verdict uncertain.
    valid_empty_evidence = None
    # TODO 9b — True seulement si une preuve non vide apparaît dans la source.
    evidence_found = None

    if not (valid_empty_evidence or evidence_found):
        raise ValueError("Preuve LLM absente du titre et du résumé")


def screen_with_llm(
    model,
    paper: PaperRecord,
    topic: str,
    inclusion_terms: set[str],
    exclusion_terms: set[str],
) -> LLMScreeningDecision:
    """Code fourni — enchaîne l'appel du TODO 8 et le contrôle du TODO 9."""
    decision = invoke_structured_screening(
        model, paper, topic, inclusion_terms, exclusion_terms
    )
    try:
        validate_grounding(paper, decision)
    except ValueError as exc:
        decision = decision.model_copy(
            update={
                "decision": "uncertain",
                "confidence": 0.0,
                "reasons": [*decision.reasons, f"Contrôle local : {exc}"],
                "evidence": "",
                "needs_human_review": True,
            }
        )
    return decision


def compare_decisions(
    deterministic: ScreeningDecision,
    llm: LLMScreeningDecision,
) -> ComparisonResult:
    """TODO 10 — Détecter accord, désaccord et besoin d'arbitrage."""
    # La comparaison, les raisons et le résultat sont fournis.
    agreement = deterministic.decision == llm.decision
    # TODO 10a — Lire needs_human_review dans la décision déterministe.
    deterministic_requests_human = None
    # TODO 10b — Lire needs_human_review dans la décision du LLM.
    llm_requests_human = None
    needs_human_review = (
        deterministic_requests_human
        or llm_requests_human
        or not agreement
    )
    if not agreement:
        reason = "Désaccord entre la règle déterministe et l'analyse sémantique"
    elif deterministic.needs_human_review or llm.needs_human_review:
        reason = "Au moins un agent demande une validation humaine"
    else:
        reason = "Accord exploitable automatiquement"
    return ComparisonResult(
        paper_id=deterministic.paper_id,
        deterministic_decision=deterministic.decision,
        llm_decision=llm.decision,
        agreement=agreement,
        needs_human_review=needs_human_review,
        escalation_reason=reason,
    )
