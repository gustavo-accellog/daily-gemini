## Primeiro exemplo de como mandar um comando em texto para o Google Gemini e printar a resposta
## pip install -U -q google.generativeai

import json
import os
from datetime import datetime
import requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY=os.getenv("GEMINI_KEY")
API_URL_BASE=os.getenv("GOOGLE_CHAT_URL")
# MODEL_NAME='gemini-2.0-flash'
MODEL_NAME='gemini-2.0-pro-exp-02-05'
CONFIGURACAO_MODELO = {
    'temperature': 2.0,
    'top_p': 0.95,
    'top_k': 64,
    'output_length': 8192,
    'response_mime_type': 'text/plain'      # 'application/json'
}

def mensagem_daily():
    ## ler system instruction de um arquivo
    path_systeminstruction = os.getenv("PATH_SYSTEMINSTRUCTION", "./caminho-arquivo/system-instruction.txt")
    with open(path_systeminstruction, 'r') as system_file:
        system_instruction = system_file.read()
        system_file.close()

    # print(system_instruction)

    ## ler content
    path_content = os.getenv("PATH_CONTENT", "./caminho-arquivo/content.txt")
    with open(path_content, 'r') as content_file:
        content = content_file.read()
        content_file.close()

    # print(content)

    llm = ChatGoogleGenerativeAI(
        api_key=GOOGLE_API_KEY,
        model=MODEL_NAME,
        model_kwargs=CONFIGURACAO_MODELO
    )


    template_mensagem = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                system_instruction
            ),
            (
                'user',
                [
                    {
                        'type': 'text',
                        'text': content,
                    }
                ]
            )
        ]
    )

    cadeia_mensagem = template_mensagem | llm | StrOutputParser()

    corpo_mensagem = cadeia_mensagem.invoke({})


    template_resposta = PromptTemplate(
        template="""
        Você é um especialista em gerar mensagens motivacionais em HTML para equipes de desenvolvimento.

        Crie uma mensagem inspiradora para a equipe, incluindo os seguintes elementos:

        * Título: {titulo}
        * Corpo: {corpo}

        A mensagem deve ser formatada em HTML, com as tags `<h1>`, `<p>` e `<strong>`.
        Gere apenas o HTML. Não gere explicações sobre o HTML.
         Gere **apenas** o código HTML, sem incluir as tags `<DOCTYPE html>`, `<html>`, `<head>`, `<body>`, `<ul>` e `<li>`.
        """,
        input_variables=['titulo', 'corpo']
    )

    cadeia_html = template_resposta | llm | StrOutputParser()

    resposta = cadeia_html.invoke({'titulo': 'Daily Carga Pontual', 'corpo': corpo_mensagem})
    # print(resposta)
    return resposta

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
    message = mensagem_daily()
    message = message.replace('```html', '').replace('```', '')
    send_googlechat(message, hoje)

if __name__ == '__main__':
    main()