# Projeto Daily Message

## Descrição:

Este projeto tem como objetivo enviar uma mensagem motivacional para a equipe de desenvolvimento diariamente, utilizando a API do Gemini para gerar o conteúdo. A mensagem é enviada através de um prompt específico, configurando o Gemini para gerar um texto motivacional relacionado ao trabalho em equipe e à importância da daily.

## Funcionalidades:

Geração de Mensagens: Utiliza a API do Gemini para criar mensagens motivacionais personalizadas.
Envio: A mensagem é enviada para um canal de comunicação da equipe (definir qual canal será utilizado).
Agendamento: O script é executado diariamente em um horário pré-definido através de um cronjob dentro de um ambiente Kubernetes.

## Tecnologias Utilizadas:

- Python: Linguagem de programação principal para a implementação do script.
- Gemini API: API utilizada para gerar o texto motivacional.
- Kubernetes: Plataforma de orquestração de containers para agendamento da tarefa.
- Docker/Podman: Ferramentas para containerização da aplicação.

## Estrutura do Projeto:

- app.py: Arquivo principal contendo o código Python para a geração e envio da mensagem.
- Dockerfile: Arquivo para construção da imagem Docker.
- daily-message-job.yaml: Arquivo de configuração para o job no Kubernetes.

## Como Executar:

### Criar uma imagem

**Podman:**

```bash
podman build -f Dockerfile -t daily-gemini:0.1 .
```

**Docker:**

```bash
docker build -f Dockerfile -t daily-gemini:0.1 .
```

### Executando Container com imagem

**Podman:**

```bash
podman run --rm -it -e GEMINI_KEY='informesuachave' -e GOOGLE_CHAT_URL='informeaurldogoogle' -e PATH_SYSTEMINSTRUCTION='/files/system-instruction.txt' -e PATH_CONTENT='/files/content.txt' localhost/daily-gemini:0.1 python -u app.py
```

**Docker:**

```bash
docker run --rm -it -e GEMINI_KEY='informesuachave' -e GOOGLE_CHAT_URL='informeaurldogoogle' -e PATH_SYSTEMINSTRUCTION='/files/system-instruction.txt' -e PATH_CONTENT='/files/content.txt' daily-gemini:0.1 python -u app.py
```

### Kubernetes

Aplicar o manifest do job: ```kubectl apply -f daily-message-job.yaml```
