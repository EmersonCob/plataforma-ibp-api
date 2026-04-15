# Plataforma IBP Backend

API principal para clientes, contratos, assinatura publica, auditoria e documento final assinado.

## Escopo

Este projeto contem somente a aplicacao backend e suas regras de negocio.

## Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic
- Redis
- MinIO/S3 compativel para fotos, assinaturas e PDFs
- JWT
- ReportLab para PDF

## Como rodar

1. Crie e ative um ambiente virtual Python.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Instale as dependencias.

```bash
pip install -r requirements.txt
```

3. Copie o arquivo de ambiente e ajuste as variaveis.

```bash
copy .env.example .env
```

4. Inicie a API.

```bash
uvicorn app.main:app --reload
```

A documentacao interativa fica em `/docs`.

## Imagem Docker

O projeto possui um `Dockerfile` proprio para empacotar apenas a API.

```bash
docker build -t plataforma-ibp-backend .
docker run --env-file .env -p 8000:8000 plataforma-ibp-backend
```

O arquivo `deploy/nginx.conf` e um template de proxy para a API em `127.0.0.1:8000`. Ajuste o upstream conforme o ambiente onde o Nginx estiver rodando.

## Criacao automatica de tabelas

Nao ha comando manual de banco neste projeto.

Ao iniciar, a API executa `Base.metadata.create_all()` de forma centralizada em `app/db/init.py`, verifica se todas as tabelas mapeadas existem e interrompe o startup se a estrutura minima nao estiver disponivel.

As tabelas sao criadas no schema definido por `DATABASE_SCHEMA`, com valor padrao `plataforma_ibp`. Isso evita colisao com tabelas existentes no schema `public`, como `users` de outros sistemas.

Esse comportamento atende ao requisito atual de criacao dinamica do schema. Alteracoes futuras de modelo devem ser tratadas com cuidado, pois `create_all()` cria objetos ausentes, mas nao substitui uma estrategia formal de evolucao de schema para alteracoes destrutivas.

## Bootstrap inicial

O primeiro admin pode ser criado automaticamente no startup quando estas variaveis estiverem configuradas:

```env
INITIAL_ADMIN_NAME=Administrador
INITIAL_ADMIN_EMAIL=admin@clinica.local
INITIAL_ADMIN_PASSWORD=troque-esta-senha-antes-de-usar
```

A senha precisa ter pelo menos 12 caracteres. O valor da senha nunca e registrado em log.

O template padrao de contrato pode ser criado automaticamente com:

```env
BOOTSTRAP_DEFAULT_TEMPLATE=true
```

## Variaveis principais

```env
ENVIRONMENT=development
PROJECT_NAME=Plataforma IBP
API_V1_PREFIX=/api/v1
SECRET_KEY=troque-por-uma-chave-forte
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080
PUBLIC_SIGN_URL_BASE=https://ibp-web-qa.jbtechinnova.com/assinatura
BACKEND_CORS_ORIGINS=https://ibp-web-qa.jbtechinnova.com

DATABASE_URL=postgresql+psycopg2://postgres:configure-no-ambiente@postgres:5432/postgres
DATABASE_SCHEMA=plataforma_ibp
REDIS_URL=redis://:configure-no-ambiente@redis:6379/1

OBJECT_STORAGE_ENDPOINT=https://s3-infra-qa.jbtechinnova.com
OBJECT_STORAGE_API_ENDPOINT=https://s3-infra-qa.jbtechinnova.com
S3_ENDPOINT=s3-infra-qa.jbtechinnova.com
S3_SECURE=true
S3_BUCKET=plataforma-ibp
S3_ACCESS_KEY=configure-no-ambiente
S3_SECRET_KEY=configure-no-ambiente
S3_PRESIGNED_EXPIRES_SECONDS=900

MAX_UPLOAD_MB=8
LOGIN_RATE_LIMIT=8/minute
PUBLIC_RATE_LIMIT=30/minute
```

Para CORS, use somente origins, sem caminho e sem barra final. Exemplo correto: `https://ibp-web-qa.jbtechinnova.com`. Nao use `https://ibp-web-qa.jbtechinnova.com/assinatura`.

## S3/MinIO

O bucket esperado para documentos, fotos e assinaturas e `plataforma-ibp`.

Use o endpoint da API S3, nao o console/browser do MinIO. Para QA:

```env
OBJECT_STORAGE_ENDPOINT=https://s3-infra-qa.jbtechinnova.com
OBJECT_STORAGE_API_ENDPOINT=https://s3-infra-qa.jbtechinnova.com
S3_ENDPOINT=s3-infra-qa.jbtechinnova.com
S3_SECURE=true
S3_BUCKET=plataforma-ibp
```

O console/browser do MinIO e `https://minio-infra-qa.jbtechinnova.com`; ele nao deve ser usado como endpoint S3 da aplicacao.

As credenciais `S3_ACCESS_KEY` e `S3_SECRET_KEY` devem ficar no `.env` real ou no mecanismo de secrets do ambiente, nunca no `.env.example`.

## Stack QA

O arquivo `deploy/stack.yml` usa a rede externa `jbtechinnova` e estes servicos:

- `plataforma_ibp_api`
- `nginx_plataforma_ibp_api`

A API monta o arquivo de ambiente em:

```text
/root/base_dados/plataforma_ibp_api/.env:/app/.env:ro
```

O Nginx monta:

```text
/root/base_dados/plataforma_ibp_api/deploy/nginx.conf:/etc/nginx/nginx.conf:ro
```

O dominio publicado via Traefik e `ibp-api-qa.jbtechinnova.com`.

## Fluxo principal

1. Admin faz login com JWT.
2. Admin cadastra cliente.
3. Admin cria ou edita contrato.
4. Alteracao de conteudo gera nova versao.
5. Admin gera link publico unico.
6. Paciente acessa sem login, le o contrato, envia foto obrigatoria e assina.
7. O backend usa controle de concorrencia via Redis e transacao no PostgreSQL para impedir dupla assinatura.
8. O contrato e bloqueado como assinado.
9. O PDF final e gerado com conteudo assinado, nome, data/hora, foto, assinatura e metadados de evidencia.
10. Admin visualiza e imprime/exporta o documento final por URL assinada.

## Seguranca preservada

- Senhas com Argon2.
- JWT com expiracao.
- Rotas privadas protegidas por bearer token.
- Links publicos aleatorios e nao previsiveis.
- Expiracao de link.
- Bloqueio apos assinatura.
- Upload com validacao de MIME, tamanho e conteudo real de imagem.
- Rate limit em login e rotas publicas sensiveis via Redis.
- Lock de assinatura via Redis e `SELECT FOR UPDATE` no contrato.
- Auditoria de eventos criticos.
- Erros tratados sem expor detalhes internos.
- Documentos e imagens acessados por URLs assinadas.
- Contrato assinado e documento final tratados como imutaveis.

## Notificacoes futuras

Nao ha integracao real com provider de WhatsApp neste momento.

O backend mantem `NotificationGateway`, `BaseNotificationProvider` e `WhatsAppProviderInterface`. Hoje o provider interno apenas registra `NotificationEvent` com status `pending` e payload estruturado, deixando a troca futura para Evolution API, Meta Cloud API ou outro provider sem acoplar o core.

## Testes

```bash
pytest
```
