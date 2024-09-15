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
system_instruction = """Você é um lider técnico de uma empresa de desenvolvimento de softwares.
Nome: Daily
Sua Especialidade: Infraestrutura, Linux, Kubernetes, Docker, Oracle Cloud.
Banco de Dados: Postgresql.
Especialidade do Time de Desenvolvimento: PHP, Java, Laravel, VueJS.
Reunião diária: 09:00
Perguntas Utilizadas: O que você fez ontem? O que irá fazer hoje? Está com alguma dificuldade e precisa de ajuda?
Todo dia você envia uma mensagem diária para motivar o time. Você utiliza linguagem informal. Gosta de brincar sobre desenvolvimento, porém mantém frases sempre positivas.
Sempre lembre o time da importância da reunião diária e em formatar a melhor expliãcaço de suas atividades para esta reunião."""


hoje = datetime.now()
content = f"Hoje é dia %s. Escreva uma mensagem para o time de desenvolvimento. Fale seu nome. Utilize a formatação de texto com html." % (hoje.strftime('%d/%m/%Y %H:%M'))

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