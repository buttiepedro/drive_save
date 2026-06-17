import io
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

_SCOPES = ["https://www.googleapis.com/auth/drive"]


def _get_service():
    credentials_path = os.environ["GOOGLE_CREDENTIALS_PATH"]
    creds = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=_SCOPES
    )
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
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
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
