#!/bin/bash

###############################################################################
# Script de Deploy - Sistema Hospshop
# Automatiza deploy em produção com Docker, Nginx e SSL
###############################################################################

set -e  # Parar em caso de erro

echo "🚀 Iniciando Deploy do Sistema Hospshop..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variáveis
DOMAIN=${DOMAIN:-"hospshop.com.br"}
EMAIL=${EMAIL:-"admin@hospshop.com.br"}
BACKEND_PORT=${BACKEND_PORT:-5000}
FRONTEND_PORT=${FRONTEND_PORT:-3000}

###############################################################################
# 1. Verificar Requisitos
###############################################################################

echo "📋 Verificando requisitos..."

# Verificar se está rodando como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Este script deve ser executado como root${NC}"
   exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker não encontrado. Instalando...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker Compose não encontrado. Instalando...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo -e "${GREEN}✅ Requisitos verificados${NC}"
echo ""

###############################################################################
# 2. Criar Dockerfile para Backend
###############################################################################

echo "🐳 Criando Dockerfile para Backend..."

cat > Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-por \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python3", "api_hospshop.py"]
EOF

echo -e "${GREEN}✅ Dockerfile.backend criado${NC}"

###############################################################################
# 3. Criar Dockerfile para Frontend
###############################################################################

echo "🐳 Criando Dockerfile para Frontend..."

cat > Dockerfile.frontend << 'EOF'
FROM node:22-alpine AS builder

WORKDIR /app

# Copiar package.json
COPY package.json pnpm-lock.yaml ./

# Instalar pnpm
RUN npm install -g pnpm

# Instalar dependências
RUN pnpm install

# Copiar código
COPY . .

# Build
RUN pnpm build

# Imagem de produção
FROM nginx:alpine

# Copiar build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF

echo -e "${GREEN}✅ Dockerfile.frontend criado${NC}"

###############################################################################
# 4. Criar docker-compose.yml
###############################################################################

echo "🐳 Criando docker-compose.yml..."

cat > docker-compose.yml << EOF
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: hospshop-backend
    restart: unless-stopped
    ports:
      - "${BACKEND_PORT}:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - JWT_SECRET=\${JWT_SECRET}
      - SMTP_HOST=\${SMTP_HOST}
      - SMTP_PORT=\${SMTP_PORT}
      - SMTP_USER=\${SMTP_USER}
      - SMTP_PASSWORD=\${SMTP_PASSWORD}
    networks:
      - hospshop-network

  frontend:
    build:
      context: ../dashboard_analise_concorrentes
      dockerfile: ../hospshop-sistema-final/Dockerfile.frontend
    container_name: hospshop-frontend
    restart: unless-stopped
    ports:
      - "${FRONTEND_PORT}:80"
    depends_on:
      - backend
    networks:
      - hospshop-network

networks:
  hospshop-network:
    driver: bridge
EOF

echo -e "${GREEN}✅ docker-compose.yml criado${NC}"

###############################################################################
# 5. Criar configuração Nginx
###############################################################################

echo "🌐 Criando configuração Nginx..."

cat > nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy para API
    location /api {
        proxy_pass http://backend:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Cache de assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

echo -e "${GREEN}✅ nginx.conf criado${NC}"

###############################################################################
# 6. Criar arquivo .env de produção
###############################################################################

echo "🔐 Criando arquivo .env..."

if [ ! -f .env ]; then
    cat > .env << EOF
# JWT
JWT_SECRET=$(openssl rand -hex 32)

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

# WhatsApp
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_TOKEN=seu_token

# AWS S3
AWS_ACCESS_KEY_ID=sua_chave
AWS_SECRET_ACCESS_KEY=sua_senha
AWS_BUCKET_NAME=hospshop-backups
AWS_REGION=us-east-1

# Effecti
EFFECTI_API_URL=https://effecti.com.br/api
EFFECTI_API_KEY=sua_chave
EOF
    echo -e "${YELLOW}⚠️  Arquivo .env criado. EDITE com suas credenciais!${NC}"
else
    echo -e "${GREEN}✅ Arquivo .env já existe${NC}"
fi

###############################################################################
# 7. Criar diretórios necessários
###############################################################################

echo "📁 Criando diretórios..."

mkdir -p data logs backups

echo -e "${GREEN}✅ Diretórios criados${NC}"

###############################################################################
# 8. Build e Deploy
###############################################################################

echo ""
echo "🏗️  Iniciando build das imagens Docker..."
echo ""

docker-compose build

echo ""
echo "🚀 Iniciando containers..."
echo ""

docker-compose up -d

echo ""
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""

###############################################################################
# 9. Configurar SSL com Certbot (opcional)
###############################################################################

read -p "Deseja configurar SSL com Let's Encrypt? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "🔒 Configurando SSL..."
    
    # Instalar Certbot
    if ! command -v certbot &> /dev/null; then
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    fi
    
    # Obter certificado
    certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --no-eff-email
    
    # Renovação automática
    echo "0 0 * * * certbot renew --quiet" | crontab -
    
    echo -e "${GREEN}✅ SSL configurado${NC}"
fi

###############################################################################
# 10. Configurar Firewall
###############################################################################

echo ""
echo "🔥 Configurando firewall..."

if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
    echo -e "${GREEN}✅ Firewall configurado${NC}"
fi

###############################################################################
# 11. Criar systemd service (alternativa ao Docker)
###############################################################################

cat > /etc/systemd/system/hospshop-backend.service << EOF
[Unit]
Description=Hospshop Backend API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/start_api.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable hospshop-backend.service

echo -e "${GREEN}✅ Systemd service criado${NC}"

###############################################################################
# 12. Informações Finais
###############################################################################

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 DEPLOY CONCLUÍDO COM SUCESSO!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Status dos Containers:"
docker-compose ps
echo ""
echo "🌐 URLs de Acesso:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend:  http://localhost:$BACKEND_PORT"
echo "   API Docs: http://localhost:$BACKEND_PORT/api/health"
echo ""
echo "🔐 Credenciais Padrão:"
echo "   Username: admin"
echo "   Senha: admin123"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Edite o arquivo .env com suas credenciais"
echo "   2. Altere a senha padrão do admin"
echo "   3. Configure backup automático"
echo "   4. Monitore os logs: docker-compose logs -f"
echo ""
echo "📝 Comandos Úteis:"
echo "   Parar:     docker-compose down"
echo "   Reiniciar: docker-compose restart"
echo "   Logs:      docker-compose logs -f"
echo "   Status:    docker-compose ps"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
