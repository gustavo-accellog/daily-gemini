## Primeiro exemplo de como mandar um comando em texto para o Google Gemini e printar a resposta
## pip install -U -q google.generativeai

import json
import os
from datetime import datetime
import google.generativeai as genai
import requests

GOOGLE_API_KEY=os.getenv("GEMINI_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model_name='gemini-1.5-flash'

## ler system instruction de um arquivo
path_systeminstruction = os.getenv("PATH_SYSTEMINSTRUCTION")    # "./caminho-arquivo/system-instruction.txt"
with open(path_systeminstruction, 'r') as system_file:
    system_instruction = system_file.read()
    system_file.close()

print(system_instruction)

## ler content
path_content = os.getenv("PATH_CONTENT")      # "./caminho-arquivo/content.txt"
hoje = datetime.now()
with open(path_content, 'r') as content_file:
    content = f"{content_file.read()}" % (hoje.strftime('%d/%m/%Y %H:%M'))
    content_file.close()

print(content)

model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
response = model.generate_content(content)

api_url_base = os.getenv("GOOGLE_CHAT_URL")
headers = {'Content-Type': 'application/json; charset=UTF-8'}

dados = {
    "cardsV2": [
        {
            "card": {
                "header": {
                    "title": f"Daily: %s" % (hoje.strftime('%d/%m/%Y')),
                    "subtitle": "Time Carga Pontual"
                },
                "sections": {
                    "widgets": [
                        {
                            "textParagraph": {
                                "text": response.text
                            }
                        }
                    ]
                }
            }
        }
    ]
}

datetimeFORMAT = '%Y-%m-%d %H:%M.%s'

try:
    resp = requests.post(api_url_base, headers=headers, data=json.dumps(dados))
except Exception as ex:
    print("%s ERROR sending message to Google Chat - Response %s"%(hoje.strftime(datetimeFORMAT), ex))