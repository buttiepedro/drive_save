import io
import logging
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

logger = logging.getLogger(__name__)


def _get_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
    )
    creds.refresh(Request())
    return build("drive", "v3", credentials=creds)


def find_or_create_folder(parent_id: str, name: str) -> str:
    service = _get_service()
    escaped = name.replace("'", "\\'")
    query = (
        f"mimeType='application/vnd.google-apps.folder'"
        f" and name='{escaped}'"
        f" and '{parent_id}' in parents"
        f" and trashed=false"
    )
    result = service.files().list(q=query, fields="files(id)").execute()
    files = result.get("files", [])
    if files:
        logger.debug("Carpeta existente | nombre=%s | id=%s", name, files[0]["id"])
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    logger.info("Carpeta creada en Drive | nombre=%s | id=%s", name, folder["id"])
    return folder["id"]


def upload_file(folder_id: str, filename: str, content: bytes, mimetype: str) -> str:
    service = _get_service()
    metadata = {"name": filename, "parents": [folder_id]}
    media = MediaIoBaseUpload(io.BytesIO(content), mimetype=mimetype, resumable=False)
    file = (
        service.files()
        .create(body=metadata, media_body=media, fields="id")
        .execute()
    )
    return file["id"]
