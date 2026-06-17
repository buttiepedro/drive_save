import logging
import os
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Request

logger = logging.getLogger(__name__)

router = APIRouter()

_raw_path = os.environ.get("WEBHOOK_PATH", "/webhook/upload")
_webhook_path = urlparse(_raw_path).path or _raw_path
logger.info("Webhook registrado en: %s", _webhook_path)


@router.post(_webhook_path)
async def receive_image(request: Request):
    logger.info("--- Request recibida ---")
    logger.info("Headers: %s", dict(request.headers))

    try:
        form = await request.form()
        logger.info("Form fields: %s", list(form.keys()))
        for key, value in form.items():
            if hasattr(value, "filename"):
                logger.info("  [archivo] %s → filename=%s | content_type=%s", key, value.filename, value.content_type)
            else:
                logger.info("  [campo]   %s → %s", key, value)
    except Exception as exc:
        logger.error("No se pudo parsear el form: %s", exc)
        raise HTTPException(status_code=422, detail=f"No se pudo parsear el form: {exc}")

    raise HTTPException(status_code=200, detail="Request logueada — revisá los logs")
