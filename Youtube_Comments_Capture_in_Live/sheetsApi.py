from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os.path
from datetime import datetime

class SheetsAPI():
    def __init__(self):

        self.creds = None
        self.SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

        # Se não houver credenciais (válidas) disponíveis, permita que o usuário faça login.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Salve as credenciais para a próxima execução
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        try:
            self.service = build("sheets", "v4", credentials=self.creds)
            self.sheet = self.service.spreadsheets()
        except HttpError as err:
            print(err)



    def add_Log_Planilha(self, comments):
        # Obtém o número da última linha ocupada na planilha
        last_row_range = self.sheet.values().get(
            spreadsheetId="código_da_sua_planilha",
            range="página_da_sua_planilha!A:Z"
        ).execute().get("values", [])
        
        last_row = len(last_row_range) + 1 if last_row_range else 1

        # Constrói os dados para atualização em lote
        data = []
        for comment in comments:
            comment_id, comment_published_at, comment_text = comment
            data.append([comment_id, comment_published_at, comment_text])

        # Atualiza as linhas na planilha
        range_name = f"página_da_sua_planilha!A{last_row}"

        try:
            self.sheet.values().update(
                spreadsheetId="código_da_sua_planilha",
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={"values": data}
            ).execute()

            print(f"{len(comments)} logs adicionados com sucesso à planilha.")
        except HttpError as err:
            print(f"Erro ao adicionar logs à planilha: {err}")