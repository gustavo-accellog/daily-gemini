## Primeiro exemplo de como mandar um comando em texto para o Google Gemini e printar a resposta
## pip install -U -q google.generativeai

import json
import os
from datetime import datetime
from markdown import markdown
import google.generativeai as genai
import requests
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY=os.getenv("GEMINI_KEY")
MODEL_NAME='gemini-2.0-flash-exp'
CONFIGURACAO_MODELO = {
    'temperature': 2.0,
    'top_p': 0.,
    'top_k': 64,
    'max_output_tokens': 8192,
    'response_mime_type': 'text/plain'      # 'application/json'
}

API_URL_BASE = os.getenv("GOOGLE_CHAT_URL")

def mensagem_daily(hoje):
    ## ler system instruction de um arquivo
    path_systeminstruction = os.getenv("PATH_SYSTEMINSTRUCTION", "./caminho-arquivo/system-instruction.txt")
    with open(path_systeminstruction, 'r') as system_file:
        system_instruction = system_file.read()
        system_file.close()

    # print(system_instruction)

    ## ler content
    path_content = os.getenv("PATH_CONTENT", "./caminho-arquivo/content.txt")
    with open(path_content, 'r') as content_file:
        content = f"{content_file.read()}" % (hoje.strftime('%d/%m/%Y %H:%M'))
        content_file.close()

    # print(content)

    genai.configure(api_key=GOOGLE_API_KEY)
    llm = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_instruction,
        generation_config=CONFIGURACAO_MODELO,
    )
    response = llm.generate_content(content)

    return response.text

def send_googlechat(message, hoje):
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
                                    "text": message
                                }
                            }
                        ]
                    }
                }
            }
        ]
    }

    try:
        resp = requests.post(API_URL_BASE, headers=headers, data=json.dumps(dados))
        print(resp)
    except Exception as ex:
        print("%s ERROR sending message to Google Chat - Response %s"%(hoje.strftime('%Y-%m-%d %H:%M.%s'), ex))

def main():
    hoje = datetime.now()
    message = markdown(mensagem_daily(hoje))
    
    send_googlechat(message, hoje)

if __name__ == '__main__':
    main()