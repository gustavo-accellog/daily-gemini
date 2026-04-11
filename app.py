## Primeiro exemplo de como mandar um comando em texto para o Google Gemini e printar a resposta
## pip install -U -q google.generativeai

import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo
import requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

DIAS_SEMANA = {
    0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira",
    3: "Quinta-feira",  4: "Sexta-feira", 5: "Sábado", 6: "Domingo",
}

GOOGLE_API_KEY=os.getenv("GEMINI_KEY")
API_URL_BASE=os.getenv("GOOGLE_CHAT_URL")
MODEL_NAME=os.getenv("MODEL_NAME", "gemini-2.5-flash")
# MODEL_NAME='gemini-2.0-pro-exp-02-05'
TEMPERATURA = 1.0
TOP_P = 0.95
TOP_K = 64
MAX_OUTPUT_TOKENS = 8192

def formatar_contexto_data(hoje: datetime) -> str:
    dia = DIAS_SEMANA[hoje.weekday()]
    return f"{dia}, {hoje.strftime('%d/%m/%Y')} às {hoje.strftime('%H:%M')} (horário de Brasília)"


def carregar_data_especial(hoje: datetime) -> dict | None:
    path = os.getenv("PATH_SPECIAL_DATES", "./files/special-dates.json")
    try:
        with open(path, 'r') as f:
            dados = json.load(f)
    except FileNotFoundError:
        return None
    for entrada in dados.get("special_dates", []):
        if entrada["type"] == "annual":
            if entrada["month"] == hoje.month and entrada["day"] == hoje.day:
                return entrada
        elif entrada["type"] == "once":
            if entrada.get("year") == hoje.year and entrada["month"] == hoje.month and entrada["day"] == hoje.day:
                return entrada
    return None


def mensagem_daily(hoje: datetime):
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

    data_especial = carregar_data_especial(hoje)
    hint_especial = ""
    if data_especial:
        nome = data_especial["name"]
        hint = data_especial.get("message_hint", "")
        hint_especial = f" Hoje também é {nome}. {hint}"

    content = content.replace("{{DATE_CONTEXT}}", formatar_contexto_data(hoje))
    content = content.replace("{{SPECIAL_DATE}}", hint_especial)

    llm = ChatGoogleGenerativeAI(
        api_key=GOOGLE_API_KEY,
        model=MODEL_NAME,
        temperature=TEMPERATURA,
        top_p=TOP_P,
        top_k=TOP_K,
        max_output_tokens=MAX_OUTPUT_TOKENS,
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
    hoje = datetime.now(tz=ZoneInfo("America/Sao_Paulo"))
    message = mensagem_daily(hoje)
    message = message.replace('```html', '').replace('```', '')
    send_googlechat(message, hoje)

if __name__ == '__main__':
    main()