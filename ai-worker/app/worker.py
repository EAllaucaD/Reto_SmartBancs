import logging
import os

from datetime import datetime, timezone

from google import genai
from sqlalchemy import select

from app.models import AIRecommendation


logger = logging.getLogger(__name__)


MODEL_NAME = "gemini-3.6-flash"


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("No se encontró GEMINI_API_KEY")

    return genai.Client(api_key=api_key)


def build_prompt(ai_job: AIRecommendation) -> str:
    return f"""
Genera una recomendación financiera breve para un cliente bancario.

Datos:
- Account ID: {ai_job.account_id}

La recomendación debe ser general, prudente y orientada a buenos hábitos financieros.
Reglas:
- Utiliza el Account ID únicamente como referencia interna.
- No menciones, repitas ni muestres el Account ID en la respuesta.
- No inventes datos específicos del cliente.
- Responde únicamente con la recomendación.
- Máximo 3 oraciones
""".strip()


def process_one_job(db):
    ai_job = db.execute(
        select(AIRecommendation)
        .where(AIRecommendation.status == "PENDING")
        .order_by(AIRecommendation.created_at)
        .limit(1)
    ).scalar_one_or_none()

    if ai_job is None:
        return False

    logger.info(
        "AI job iniciado | job_id=%s | account_id=%s",
        ai_job.id,
        ai_job.account_id
    )

    try:
        client = get_gemini_client()

        logger.info(
            "Llamando a Gemini | job_id=%s | model=%s",
            ai_job.id,
            MODEL_NAME
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=build_prompt(ai_job)
        )

        recommendation = response.text

        if not recommendation:
            raise RuntimeError("Gemini no devolvió contenido")

        ai_job.recommendation = recommendation
        ai_job.status = "COMPLETED"
        ai_job.error_message = None
        ai_job.updated_at = datetime.now(timezone.utc)

        db.commit()

        logger.info(
            "AI job completado | job_id=%s | model=%s",
            ai_job.id,
            MODEL_NAME
        )

    except Exception as error:
        db.rollback()

        ai_job = db.get(AIRecommendation, ai_job.id)

        if ai_job is not None:
            ai_job.status = "FAILED"
            ai_job.error_message = str(error)
            ai_job.updated_at = datetime.now(timezone.utc)

            db.commit()

        logger.exception(
            "Error procesando AI job | job_id=%s",
            ai_job.id if ai_job is not None else "unknown"
        )

    return True

