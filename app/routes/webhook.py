import os

from fastapi import APIRouter, Form, HTTPException, UploadFile

from app.services.drive import find_or_create_folder, upload_file

router = APIRouter()


@router.post(os.environ.get("WEBHOOK_PATH", "/webhook/upload"))
async def receive_image(
    sender_id: str = Form(...),
    image: UploadFile = Form(...),
):
    drive_folder_id = os.environ.get("DRIVE_FOLDER_ID")
    if not drive_folder_id:
        raise HTTPException(status_code=500, detail="DRIVE_FOLDER_ID no configurado")

    try:
        subfolder_id = find_or_create_folder(drive_folder_id, sender_id)
        content = await image.read()
        file_id = upload_file(
            subfolder_id,
            image.filename or "image",
            content,
            image.content_type or "application/octet-stream",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"status": "ok", "file_id": file_id}
