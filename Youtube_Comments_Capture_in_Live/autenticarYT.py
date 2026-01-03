from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import openpyxl
import time
import pytz
from datetime import datetime

from sheetsApi import SheetsAPI

class Api_Youtube():


    def __init__(self):


        # Defina as suas credenciais aqui
        API_KEY = "chave_da_sua_API"
        VIDEO_ID = input("Entre com o ID da Live: ")

        self.sheets_api = SheetsAPI()

        # Extrai o ID do vídeo da URL
        #VIDEO_ID = VIDEO_ID.split('=')[-1]
        
        # Cria uma instância do serviço da API do YouTube
        youtube = build('youtube', 'v3', developerKey=API_KEY)

        # Faz uma solicitação para obter o ID do chat da live associado ao vídeo
        response = youtube.videos().list(
            part='liveStreamingDetails',
            id=VIDEO_ID
        ).execute()

        # Extrai o ID do chat da live
        live_chat_id = response['items'][0]['liveStreamingDetails']['activeLiveChatId']

        # Carregar ou criar um arquivo Excel para armazenar os comentários
        try:
            workbook = openpyxl.load_workbook('youtube_comments.xlsx')
            print("\nArquivo encontrado, vamos registrar os comentários de sua Live!")
        except FileNotFoundError:
            workbook = openpyxl.Workbook()
            print("\nArquivo de registro criado, vamos registrar os comentários de sua Live!")

        # Selecionar a primeira planilha no arquivo (se não houver, criar uma)
        sheet = workbook.active
        if sheet.title != 'Comments':
            sheet.title = 'Comments'
            sheet.append(['Comment_ID', 'Published_At', 'Comment_Text'])

        # Definir uma lista para armazenar IDs de comentários já vistos
        seen_comments = []

        # Loop infinito para capturar novos comentários em tempo real
        while True:
            try:

                # Lista para armazenar os novos comentários
                new_comments = []

                # Usa o ID do live chat para capturar os comentários em tempo real
                response = youtube.liveChatMessages().list(
                    liveChatId=live_chat_id,
                    part='snippet',
                    maxResults=200
                ).execute()

                # Iterar sobre os comentários
                for item in response['items']:
                    try:
                        comment_id = item['snippet']['authorChannelId']
                        comment_text = item['snippet']['textMessageDetails']['messageText']
                        comment_published_at = item['snippet']['publishedAt']

                        # Verificar se o comentário é novo com base no texto e no horário
                        if (comment_text, comment_published_at) not in seen_comments:
                            # Adicionar o comentário à lista de comentários já vistos
                            seen_comments.append((comment_text, comment_published_at))

                            # Converte o horário para o fuso que conhecemos (Por padrão chega em formato ISO 8601)
                            utc_time = datetime.strptime(comment_published_at, "%Y-%m-%dT%H:%M:%S.%f%z")
                            local_timezone = pytz.timezone('America/Sao_Paulo')
                            local_time = utc_time.astimezone(local_timezone)
                            comment_date = local_time.strftime("%Y-%m-%d %H:%M:%S")

                            # Adicionar os detalhes do comentário à lista de novos comentários
                            new_comments.append((comment_id, comment_date, comment_text))

                            # Adicionar os detalhes do comentário ao arquivo Excel (Cópia "Física")
                            sheet.append([comment_id, comment_date, comment_text])

                    except KeyError:
                        # Se a chave 'textMessageDetails' estiver ausente, o item não é um comentário de texto
                        pass

                # Adicionar os novos comentários ao Google Sheets em lote (Cópia "Digital")
                self.sheets_api.add_Log_Planilha(new_comments)
                # Salvar o arquivo Excel após cada iteração para garantir que os dados não sejam perdidos em caso de falha
                workbook.save('youtube_comments.xlsx')

                # Aguardar alguns segundos antes de verificar novamente por novos comentários
                time.sleep(100)
            except:
                print("Ocorreu algum erro durante a tentativa de captação de comentários!")
                time.sleep(20)