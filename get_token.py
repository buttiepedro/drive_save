"""
Corre este script UNA SOLA VEZ para obtener el refresh token de Google.

Prerequisitos:
  pip install google-auth-oauthlib

Pasos en Google Cloud Console:
  1. APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID
  2. Application type: Desktop app
  3. Descargar el JSON y renombrarlo a oauth_client.json en esta carpeta

Al terminar imprime las 3 variables para pegar en el .env del servidor.
"""

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/drive"]

flow = InstalledAppFlow.from_client_secrets_file("oauth_client.json", SCOPES)
creds = flow.run_local_server(port=0)

print("\n--- Pegá esto en tu .env ---")
print(f"GOOGLE_CLIENT_ID={creds.client_id}")
print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
