# 🚀 Guia Rápido de Instalação - Sistema Hospshop

## ⚡ Instalação Rápida (5 minutos)

### Pré-requisitos

- Python 3.11 ou superior
- Node.js 22 ou superior
- Git

### Passo 1: Clonar Repositórios

```bash
# Backend
git clone https://github.com/lukasfc-star/hospshop-sistema-final.git
cd hospshop-sistema-final

# Frontend (em outro terminal)
git clone https://github.com/seu-usuario/dashboard_analise_concorrentes.git
cd dashboard_analise_concorrentes
```

### Passo 2: Configurar Backend

```bash
cd hospshop-sistema-final

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate no Windows

# Instalar dependências
pip install -r requirements.txt

# Iniciar API
chmod +x start_api.sh
./start_api.sh
```

✅ **API rodando em**: http://localhost:5000

### Passo 3: Configurar Frontend

```bash
cd dashboard_analise_concorrentes

# Instalar dependências
pnpm install

# Iniciar servidor
pnpm dev
```

✅ **Dashboard rodando em**: http://localhost:3000

### Passo 4: Acessar Sistema

1. Abrir navegador em http://localhost:3000
2. Fazer login com:
   - **Username**: `admin`
   - **Senha**: `admin123`

---

## 🔐 Credenciais Padrão

| Usuário | Username | Senha | Nível |
|---------|----------|-------|-------|
| Admin | admin | admin123 | Administrador |
| Operador | operador1 | senha123 | Operador |

**⚠️ IMPORTANTE**: Alterar senhas padrão em produção!

---

## 📋 Checklist Pós-Instalação

- [ ] API rodando na porta 5000
- [ ] Dashboard rodando na porta 3000
- [ ] Login funcionando
- [ ] Criar novo usuário no painel Admin
- [ ] Alterar senha do admin padrão
- [ ] Configurar variáveis de ambiente (.env)

---

## 🔧 Configuração Opcional

### Variáveis de Ambiente

Criar arquivo `.env` em `hospshop-sistema-final/`:

```env
# Email (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

# WhatsApp (opcional)
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_TOKEN=seu_token

# AWS S3 Backup (opcional)
AWS_ACCESS_KEY_ID=sua_chave
AWS_SECRET_ACCESS_KEY=sua_senha
AWS_BUCKET_NAME=hospshop-backups
AWS_REGION=us-east-1
```

---

## 🐛 Problemas Comuns

### Porta 5000 já em uso

```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Erro ao instalar dependências Python

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro ao instalar dependências Node

```bash
rm -rf node_modules package-lock.json
pnpm install
```

---

## 📞 Precisa de Ajuda?

- 📖 Documentação completa: `DOCUMENTACAO_COMPLETA.md`
- 🐛 Issues: https://github.com/lukasfc-star/hospshop-sistema-final/issues
- 📧 Email: suporte@hospshop.com

---

## ✅ Próximos Passos

Após instalação bem-sucedida:

1. **Explorar o Dashboard** - Navegue pelos 11 módulos
2. **Criar Usuários** - Acesse /admin e crie operadores
3. **Configurar Integrações** - Email, WhatsApp, Google Sheets
4. **Importar Dados** - Comece a capturar licitações
5. **Gerar Relatórios** - Teste o sistema de relatórios

---

**Sistema pronto para uso! 🎉**
