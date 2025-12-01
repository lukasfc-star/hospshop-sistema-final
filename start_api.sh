#!/bin/bash

# Script de inicialização da API Hospshop
# Este script inicia a API Flask em background

echo "🚀 Iniciando API Hospshop..."

# Verificar se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado. Criando..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Verificar se a API já está rodando
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  API já está rodando na porta 5000"
    echo "   Para reiniciar, execute: ./stop_api.sh && ./start_api.sh"
    exit 1
fi

# Iniciar API em background
echo "📡 Iniciando servidor Flask na porta 5000..."
nohup python3 api_hospshop.py > api.log 2>&1 &
API_PID=$!

# Salvar PID para poder parar depois
echo $API_PID > api.pid

# Aguardar API iniciar
sleep 2

# Verificar se API está respondendo
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ API iniciada com sucesso!"
    echo "   URL: http://localhost:5000"
    echo "   PID: $API_PID"
    echo "   Log: tail -f api.log"
else
    echo "❌ Erro ao iniciar API. Verifique o log:"
    tail -20 api.log
    exit 1
fi
