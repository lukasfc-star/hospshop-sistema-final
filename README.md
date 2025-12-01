# 🏥 Sistema Hospshop

**Plataforma Completa de Gestão de Licitações e Fornecimento Hospitalar**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6.svg)](https://www.typescriptlang.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## 📋 Sobre o Projeto

O **Sistema Hospshop** é uma solução completa e integrada para automatizar e otimizar todo o processo de participação em licitações públicas hospitalares, desde a captura automática de editais até a entrega final de produtos.

### 🎯 Principais Funcionalidades

- ✅ **22 Módulos Integrados** - Cobertura completa do processo de licitações
- ✅ **Captura Automática** - Integração com plataforma Effecti
- ✅ **Análise de Concorrentes** - Dashboard de irregularidades e vantagens competitivas
- ✅ **Sistema de Cotações** - Comparação automática de propostas de fornecedores
- ✅ **Gestão Financeira** - Controle completo de receitas, despesas e fluxo de caixa
- ✅ **Logística Integrada** - Rastreamento de entregas em tempo real
- ✅ **Autenticação JWT** - Segurança com 3 níveis de acesso (admin, operador, visualizador)
- ✅ **API REST** - 40+ endpoints documentados

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 22+
- Git

### Instalação em 3 Passos

```bash
# 1. Clone o repositório
git clone https://github.com/lukasfc-star/hospshop-sistema-final.git
cd hospshop-sistema-final

# 2. Inicie o backend
./start_api.sh

# 3. Inicie o frontend (em outro terminal)
cd ../dashboard_analise_concorrentes
pnpm install && pnpm dev
```

### Acesso

- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000
- **Credenciais**: `admin` / `admin123`

📖 **[Guia Completo de Instalação](GUIA_INSTALACAO.md)**

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| **[Documentação Completa](DOCUMENTACAO_COMPLETA.md)** | Arquitetura, API, banco de dados e troubleshooting |
| **[Guia de Instalação](GUIA_INSTALACAO.md)** | Instalação rápida em 5 minutos |
| **[Manual do Usuário](MANUAL_USUARIO.md)** | Guia completo para usuários finais |
| **[Script de Deploy](deploy.sh)** | Deploy automatizado com Docker |

---

## 📊 Módulos do Sistema (22/22 Completos)

| # | Módulo | Descrição | Status |
|---|--------|-----------|--------|
| 1 | **Effecti Integration** | Captura automática de licitações | ✅ |
| 2 | **Análise de Concorrentes** | Dashboard de irregularidades | ✅ |
| 3 | **Padronização** | Validação e score de licitações | ✅ |
| 4 | **Notificações** | Email e WhatsApp | ✅ |
| 5 | **Google Sheets** | Sincronização de planilhas | ✅ |
| 6 | **OCR** | Análise de documentos PDF | ✅ |
| 7 | **Cotações** | Sistema de cotações | ✅ |
| 8 | **Email Templates** | 10 templates prontos | ✅ |
| 9 | **WhatsApp** | Automação de mensagens | ✅ |
| 10 | **Propostas** | Montagem de propostas | ✅ |
| 11 | **Contratos** | Geração de contratos | ✅ |
| 12 | **Financeiro** | Controle financeiro | ✅ |
| 13 | **Pagamentos** | Rastreamento de parcelas | ✅ |
| 14 | **Logística** | Gestão de entregas | ✅ |
| 15 | **Relatórios** | 5 tipos de relatórios | ✅ |
| 16 | **Backup** | Backup automático AWS S3 | ✅ |
| 17 | **Autenticação** | Sistema JWT completo | ✅ |
| 18 | **CRUD Fornecedores** | Gestão de fornecedores | ✅ |
| 19 | **CRUD Licitações** | Gestão de licitações | ✅ |
| 20 | **CRUD Plataformas** | Gestão de plataformas | ✅ |
| 21 | **Dashboard Principal** | Interface unificada | ✅ |
| 22 | **Painel Admin** | Administração do sistema | ✅ |

---

## 🔐 Autenticação e Segurança

### Níveis de Acesso

| Nível | Permissões | Badge |
|-------|-----------|-------|
| **Admin** | Acesso total, criar usuários, ver logs | 🔴 |
| **Operador** | Criar e editar registros | 🔵 |
| **Visualizador** | Apenas visualização | ⚪ |

### Recursos de Segurança

- ✅ Autenticação JWT com tokens de 24h
- ✅ Hash SHA-256 para senhas
- ✅ Sessões rastreadas por IP
- ✅ Log completo de acessos
- ✅ Proteção de rotas sensíveis
- ✅ Níveis hierárquicos de acesso

---

## 📡 API REST (40+ Endpoints)

### Principais Endpoints

```http
# Autenticação
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/me

# Dashboard
GET    /api/dashboard/stats
GET    /api/dashboard/activity

# Licitações
GET    /api/licitacoes
POST   /api/licitacoes/capturar

# Cotações
GET    /api/cotacoes
POST   /api/cotacoes
GET    /api/cotacoes/{id}/comparar

# Financeiro
POST   /api/financeiro/receitas
POST   /api/financeiro/despesas
GET    /api/financeiro/saldo

# Logística
POST   /api/logistica/pedidos
GET    /api/logistica/entregas/pendentes

# Relatórios
GET    /api/relatorios/executivo
POST   /api/relatorios/exportar/pdf
```

📖 **[Documentação Completa da API](DOCUMENTACAO_COMPLETA.md)**

---

## 🚀 Deploy em Produção

### Deploy Automatizado com Docker

```bash
# Executar script de deploy
chmod +x deploy.sh
sudo ./deploy.sh
```

O script automaticamente:
- ✅ Instala Docker e Docker Compose
- ✅ Cria Dockerfiles para backend e frontend
- ✅ Configura Nginx com proxy reverso
- ✅ Configura SSL com Let's Encrypt
- ✅ Configura firewall
- ✅ Cria systemd service

---

## 📞 Suporte

- **Email**: suporte@hospshop.com
- **Issues**: [GitHub Issues](https://github.com/lukasfc-star/hospshop-sistema-final/issues)
- **Repositório**: https://github.com/lukasfc-star/hospshop-sistema-final

---

## 📝 Licença

Sistema proprietário desenvolvido para gestão hospitalar.

© 2024 Sistema Hospshop - Todos os direitos reservados.

---

## 👥 Equipe

- **Desenvolvedor Principal**: Lucas FC
- **Desenvolvido em**: 01/12/2025
- **Versão**: 1.0.0

---

**⭐ Sistema 100% Completo - 22 Módulos Funcionais!**
