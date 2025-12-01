# 📚 Documentação Completa - Sistema Hospshop

## 🎯 Visão Geral

O **Sistema Hospshop** é uma plataforma completa de gestão de licitações e fornecimento hospitalar, desenvolvida para automatizar e otimizar todo o processo de participação em licitações públicas, desde a captura de editais até a entrega de produtos.

### Principais Funcionalidades

- ✅ **22 Módulos Integrados** - Cobertura completa do processo
- ✅ **Captura Automática** - Integração com plataforma Effecti
- ✅ **Análise de Concorrentes** - Dashboard de irregularidades
- ✅ **Sistema de Cotações** - Comparação automática de propostas
- ✅ **Gestão Financeira** - Controle completo de receitas e despesas
- ✅ **Logística Integrada** - Rastreamento de entregas
- ✅ **Autenticação JWT** - Segurança com 3 níveis de acesso
- ✅ **API REST** - 40+ endpoints documentados

---

## 📦 Arquitetura do Sistema

### Backend (Python + Flask)

```
hospshop-sistema-final/
├── api_hospshop.py              # API REST principal
├── auth.py                      # Sistema de autenticação
├── effecti_integration.py       # Captura de licitações
├── padronizacao.py              # Validação e filtros
├── notifications.py             # Notificações (email/WhatsApp)
├── google_sheets_integration.py # Integração planilhas
├── ocr_document_analysis.py     # Análise de PDFs
├── supplier_quotation_system.py # Sistema de cotações
├── email_templates.py           # Templates de email
├── whatsapp_automation.py       # Automação WhatsApp
├── proposal_assembly.py         # Montagem de propostas
├── contract_generation.py       # Geração de contratos
├── financial_control.py         # Controle financeiro
├── payment_tracking.py          # Rastreamento de pagamentos
├── logistics_management.py      # Gestão de logística
├── reporting_system.py          # Sistema de relatórios
├── sistema_backup_automatizado.py # Backup AWS S3
├── preparar_pacote_producao.py  # Deploy
├── start_api.sh                 # Script de inicialização
├── stop_api.sh                  # Script de parada
└── requirements.txt             # Dependências Python
```

### Frontend (React + TypeScript)

```
dashboard_analise_concorrentes/
└── client/
    └── src/
        ├── pages/              # Páginas do sistema
        │   ├── Login.tsx       # Autenticação
        │   ├── Dashboard.tsx   # Dashboard principal
        │   ├── Admin.tsx       # Painel de administração
        │   ├── Licitacoes.tsx  # Gestão de licitações
        │   ├── Cotacoes.tsx    # Sistema de cotações
        │   ├── Financeiro.tsx  # Controle financeiro
        │   ├── Logistica.tsx   # Logística
        │   ├── Relatorios.tsx  # Relatórios
        │   ├── Contratos.tsx   # Contratos
        │   ├── Pagamentos.tsx  # Pagamentos
        │   ├── Fornecedores.tsx # Fornecedores
        │   └── Notificacoes.tsx # Notificações
        ├── contexts/
        │   └── AuthContext.tsx # Contexto de autenticação
        ├── components/
        │   └── ProtectedRoute.tsx # Proteção de rotas
        └── services/
            └── hospshop-api.ts # Cliente da API
```

---

## 🔐 Sistema de Autenticação

### Níveis de Acesso

| Nível | Permissões | Cor |
|-------|-----------|-----|
| **Admin** | Acesso total, criar usuários, ver logs | 🔴 Vermelho |
| **Operador** | Criar e editar registros | 🔵 Azul |
| **Visualizador** | Apenas visualização | ⚪ Cinza |

### Credenciais Padrão

```
Admin:
  Username: admin
  Senha: admin123

Operador:
  Username: operador1
  Senha: senha123
```

### Endpoints de Autenticação

```http
POST /api/auth/login
Body: { "username": "admin", "senha": "admin123" }
Response: { "token": "jwt_token", "usuario": {...} }

POST /api/auth/logout
Headers: Authorization: Bearer {token}

GET /api/auth/me
Headers: Authorization: Bearer {token}

GET /api/auth/usuarios (admin only)
POST /api/auth/usuarios (admin only)
POST /api/auth/alterar-senha
GET /api/auth/logs (admin only)
```

---

## 📡 API REST - Endpoints

### Dashboard

```http
GET /api/dashboard/stats
Response: {
  "licitacoes_ativas": 24,
  "valor_total_contratos": 2850000,
  "economia_gerada": 425000,
  "taxa_sucesso": 62.5
}

GET /api/dashboard/activity
Response: [
  {
    "tipo": "licitacao",
    "descricao": "Nova licitação detectada",
    "tempo": "5 min atrás"
  }
]
```

### Licitações

```http
GET /api/licitacoes
Query: ?status=aberta&estado=SP&limit=50

POST /api/licitacoes/capturar
Body: {
  "estados": ["SP", "RJ"],
  "palavras_chave": ["equipamento", "hospitalar"]
}
```

### Cotações

```http
GET /api/cotacoes
POST /api/cotacoes
Body: {
  "numero_edital": "PE-2024-001",
  "descricao": "Equipamentos médicos",
  "itens": [
    { "descricao": "Bisturi", "quantidade": 100, "unidade": "un" }
  ],
  "prazo_resposta": "2024-12-31"
}

GET /api/cotacoes/{id}/comparar
Response: {
  "menor_preco": 73500,
  "maior_preco": 84000,
  "economia": 10500
}
```

### Financeiro

```http
POST /api/financeiro/receitas
Body: {
  "descricao": "Contrato Hospital XYZ",
  "valor": 113500,
  "categoria": "Contratos",
  "data": "2024-12-01"
}

POST /api/financeiro/despesas
GET /api/financeiro/saldo
GET /api/financeiro/relatorio?inicio=2024-12-01&fim=2024-12-31
```

### Pagamentos

```http
POST /api/pagamentos
Body: {
  "descricao": "Fornecedor ABC",
  "valor_total": 85000,
  "numero_parcelas": 3,
  "data_vencimento_primeira": "2024-12-15"
}

GET /api/pagamentos/parcelas/vencendo?dias=7
POST /api/pagamentos/parcelas/{id}/pagar
```

### Logística

```http
POST /api/logistica/pedidos
POST /api/logistica/pedidos/{id}/agendar
GET /api/logistica/pedidos/{id}/rastreamento
GET /api/logistica/entregas/pendentes
```

### Notificações

```http
POST /api/notificacoes/email
Body: {
  "destinatario": "cliente@email.com",
  "assunto": "Nova Licitação",
  "corpo": "Detectamos uma nova licitação..."
}

POST /api/notificacoes/whatsapp
Body: {
  "telefone": "+5511999999999",
  "tipo_template": "nova_licitacao",
  "dados": { "numero": "PE-2024-001" }
}
```

### Relatórios

```http
GET /api/relatorios/licitacoes?inicio=2024-12-01&fim=2024-12-31
GET /api/relatorios/executivo?inicio=2024-12-01&fim=2024-12-31
POST /api/relatorios/exportar/pdf
```

### OCR

```http
POST /api/ocr/analisar
Body: { "pdf_path": "/path/to/edital.pdf" }
Response: {
  "numero_edital": "PE-2024-001",
  "orgao": "Hospital Municipal",
  "objeto": "Equipamentos médicos",
  "valor_estimado": 150000,
  "data_abertura": "2024-12-15",
  "prazo_entrega": "30 dias"
}
```

---

## 🗄️ Banco de Dados

### Estrutura SQLite

O sistema utiliza múltiplos bancos SQLite para organização:

- `hospshop_auth.db` - Autenticação e usuários
- `hospshop_licitacoes.db` - Licitações
- `hospshop_cotacoes.db` - Cotações
- `hospshop_financeiro.db` - Financeiro
- `hospshop_pagamentos.db` - Pagamentos
- `hospshop_logistica.db` - Logística

### Principais Tabelas

**Usuários (hospshop_auth.db)**
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    senha_hash TEXT,
    nome_completo TEXT,
    nivel_acesso TEXT, -- admin, operador, visualizador
    ativo BOOLEAN,
    data_criacao TIMESTAMP,
    ultimo_login TIMESTAMP
);

CREATE TABLE sessoes (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER,
    token TEXT UNIQUE,
    ip_address TEXT,
    data_expiracao TIMESTAMP,
    ativo BOOLEAN
);

CREATE TABLE log_acessos (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER,
    acao TEXT,
    detalhes TEXT,
    ip_address TEXT,
    sucesso BOOLEAN,
    data_hora TIMESTAMP
);
```

---

## 🚀 Instalação e Configuração

### Requisitos

- Python 3.11+
- Node.js 22+
- pip3
- pnpm

### Instalação Backend

```bash
# 1. Clonar repositório
git clone https://github.com/lukasfc-star/hospshop-sistema-final.git
cd hospshop-sistema-final

# 2. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais

# 5. Iniciar API
./start_api.sh
# ou
python3 api_hospshop.py
```

### Instalação Frontend

```bash
# 1. Navegar para o diretório do dashboard
cd dashboard_analise_concorrentes

# 2. Instalar dependências
pnpm install

# 3. Iniciar servidor de desenvolvimento
pnpm dev

# 4. Acessar
http://localhost:3000
```

### Configuração de Variáveis de Ambiente

Criar arquivo `.env` na raiz do projeto backend:

```env
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

# WhatsApp Business API
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_TOKEN=seu_token

# Google Sheets
GOOGLE_SHEETS_CREDENTIALS_FILE=credentials.json

# AWS S3 (Backup)
AWS_ACCESS_KEY_ID=sua_chave
AWS_SECRET_ACCESS_KEY=sua_senha_secreta
AWS_BUCKET_NAME=hospshop-backups
AWS_REGION=us-east-1

# Effecti
EFFECTI_API_URL=https://effecti.com.br/api
EFFECTI_API_KEY=sua_chave

# JWT
JWT_SECRET=gerar_com_secrets.token_hex(32)
JWT_EXPIRATION_HOURS=24
```

---

## 📊 Módulos do Sistema

### 1. Effecti Integration
**Arquivo**: `effecti_integration.py`

Captura automática de licitações da plataforma Effecti.

```python
from effecti_integration import EffectiIntegration

effecti = EffectiIntegration()
licitacoes = effecti.buscar_licitacoes(
    estados=['SP', 'RJ'],
    palavras_chave=['equipamento', 'hospitalar']
)
```

### 2. Padronização de Captação
**Arquivo**: `padronizacao.py`

Sistema de validação e score de licitações.

```python
from padronizacao import PadronizacaoCaptacao

padronizacao = PadronizacaoCaptacao()
resultado = padronizacao.validar_licitacao(licitacao_data)
# Score: 0-100, Prioridade: BAIXA/MÉDIA/ALTA
```

### 3. Sistema de Notificações
**Arquivo**: `notifications.py`

Envio de emails e mensagens WhatsApp.

```python
from notifications import NotificationManager

notif = NotificationManager()
notif.enviar_email(
    destinatario='cliente@email.com',
    assunto='Nova Licitação',
    corpo='Detectamos uma nova licitação...'
)
```

### 4. Google Sheets Integration
**Arquivo**: `google_sheets_integration.py`

Sincronização bidirecional com planilhas.

```python
from google_sheets_integration import GoogleSheetsIntegration

sheets = GoogleSheetsIntegration()
sheets.sincronizar_licitacoes('1234567890abcdef')
```

### 5. OCR Document Analysis
**Arquivo**: `ocr_document_analysis.py`

Extração inteligente de dados de editais PDF.

```python
from ocr_document_analysis import OCRDocumentAnalyzer

ocr = OCRDocumentAnalyzer()
dados = ocr.analisar_edital('/path/to/edital.pdf')
# Extrai: número, órgão, objeto, valor, datas, requisitos
```

### 6. Supplier Quotation System
**Arquivo**: `supplier_quotation_system.py`

Sistema completo de cotações com comparação automática.

```python
from supplier_quotation_system import SupplierQuotationSystem

quotations = SupplierQuotationSystem()
solicitacao_id = quotations.criar_solicitacao_cotacao(
    numero_edital='PE-2024-001',
    descricao='Equipamentos médicos',
    itens=[...]
)
```

### 7-8. Email e WhatsApp Templates
**Arquivos**: `email_templates.py`, `whatsapp_automation.py`

10 templates prontos para cada canal.

### 9. Proposal Assembly
**Arquivo**: `proposal_assembly.py`

Geração automática de propostas em PDF.

### 10. Contract Generation
**Arquivo**: `contract_generation.py`

Geração de contratos com 3 templates (fornecimento, serviços, locação).

### 11. Financial Control
**Arquivo**: `financial_control.py`

Controle completo de receitas, despesas e fluxo de caixa.

### 12. Payment Tracking
**Arquivo**: `payment_tracking.py`

Rastreamento de parcelas com alertas de vencimento.

### 13. Logistics Management
**Arquivo**: `logistics_management.py`

Gestão de pedidos, agendamentos e rastreamento.

### 14. Reporting System
**Arquivo**: `reporting_system.py`

5 tipos de relatórios com exportação PDF/CSV.

---

## 🔧 Manutenção

### Backup Automático

O sistema possui backup automático para AWS S3:

```bash
python3 sistema_backup_automatizado.py
```

Configurar cron para execução diária:
```bash
0 2 * * * cd /path/to/hospshop && python3 sistema_backup_automatizado.py
```

### Logs

Logs da API em `api.log`:
```bash
tail -f api.log
```

### Atualização

```bash
# Backend
cd hospshop-sistema-final
git pull
pip install -r requirements.txt
./stop_api.sh
./start_api.sh

# Frontend
cd dashboard_analise_concorrentes
git pull
pnpm install
pnpm build
```

---

## 🐛 Troubleshooting

### API não inicia

```bash
# Verificar porta 5000
lsof -i :5000
kill -9 <PID>

# Verificar logs
tail -f api.log

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Erro de autenticação

```bash
# Verificar banco de dados
sqlite3 hospshop_auth.db
SELECT * FROM usuarios;

# Recriar usuário admin
python3 auth.py
```

### Frontend não conecta com API

```bash
# Verificar proxy no vite.config.ts
# Verificar CORS na API
# Verificar se API está rodando: curl http://localhost:5000/api/health
```

---

## 📞 Suporte

**Repositório**: https://github.com/lukasfc-star/hospshop-sistema-final

**Desenvolvido em**: 01/12/2025

**Versão**: 1.0.0

---

## 📝 Licença

Sistema proprietário desenvolvido para gestão hospitalar.

© 2024 Sistema Hospshop - Todos os direitos reservados.
