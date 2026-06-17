import logging
import os

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.services.drive import find_or_create_folder, upload_file

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(os.environ.get("WEBHOOK_PATH", "/webhook/upload"))
async def receive_image(
    sender_id: str = Form(...),
    image: UploadFile = Form(...),
):
    drive_folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not drive_folder_id:
        raise HTTPException(status_code=500, detail="DRIVE_FOLDER_ID no configurado")

    filename = image.filename or "image"
    size_kb = None

    logger.info("Imagen recibida | sender_id=%s | archivo=%s | tipo=%s", sender_id, filename, image.content_type)

    try:
        subfolder_id = find_or_create_folder(drive_folder_id, sender_id)
        content = await image.read()
        size_kb = round(len(content) / 1024, 1)
        logger.info("Subiendo a Drive | sender_id=%s | archivo=%s | tamaño=%s KB", sender_id, filename, size_kb)
        file_id = upload_file(
            subfolder_id,
            filename,
            content,
            image.content_type or "application/octet-stream",
        )
    except Exception as exc:
        logger.error("Error al guardar | sender_id=%s | archivo=%s | error=%s", sender_id, filename, exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    logger.info("Guardado OK | sender_id=%s | archivo=%s | file_id=%s", sender_id, filename, file_id)
    return {"status": "ok", "file_id": file_id}
