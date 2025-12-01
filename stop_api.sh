#!/bin/bash

# Script para parar a API Hospshop

echo "🛑 Parando API Hospshop..."

if [ -f api.pid ]; then
    PID=$(cat api.pid)
    if ps -p $PID > /dev/null; then
        kill $PID
        echo "✅ API parada (PID: $PID)"
        rm api.pid
    else
        echo "⚠️  Processo não encontrado (PID: $PID)"
        rm api.pid
    fi
else
    echo "⚠️  Arquivo api.pid não encontrado"
    echo "   Tentando parar pela porta 5000..."
    
    PID=$(lsof -ti:5000)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ API parada (PID: $PID)"
    else
        echo "   Nenhum processo encontrado na porta 5000"
    fi
fi
