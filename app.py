#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Hospshop - Versão Railway
Gestão de Licitações e Fornecedores
"""

from flask import Flask, render_template_string, jsonify, request, session, redirect, url_for
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "hospshop_railway_secret_2025")

# Railway automaticamente fornece DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    """Estabelece conexão com o banco de dados PostgreSQL"""
    return psycopg2.connect(DATABASE_URL)

def init_db():
    """Inicializar banco de dados"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                nivel VARCHAR(50) DEFAULT 'consulta',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de fornecedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                cnpj VARCHAR(20),
                categoria VARCHAR(100),
                cidade VARCHAR(100),
                uf VARCHAR(2),
                telefone VARCHAR(20),
                email VARCHAR(100),
                responsavel VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de plataformas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plataformas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                url VARCHAR(255),
                login VARCHAR(100),
                senha VARCHAR(100),
                descricao TEXT,
                status VARCHAR(20) DEFAULT 'ativo',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de licitações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS licitacoes (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(50) NOT NULL,
                orgao VARCHAR(255),
                objeto TEXT,
                modalidade VARCHAR(100),
                valor_estimado NUMERIC(15, 2),
                data_abertura DATE,
                data_fechamento DATE,
                status VARCHAR(50) DEFAULT 'aberta',
                plataforma_origem VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de logs de atividade
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_atividade (
                id SERIAL PRIMARY KEY,
                usuario VARCHAR(80),
                acao VARCHAR(100),
                detalhes TEXT,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Inserir usuário admin se não existir
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (username, password, nivel) 
                VALUES (%s, %s, %s)
            """, ('admin', 'admin123', 'admin'))
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Banco de dados inicializado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def load_sample_data():
    """Carregar dados de exemplo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verificar se já existem dados
        cursor.execute('SELECT COUNT(*) FROM fornecedores')
        if cursor.fetchone()[0] == 0:
            # Inserir fornecedores de exemplo
            fornecedores = [
                ('MEDICALTECH EQUIPAMENTOS LTDA', '12.345.678/0001-90', 'EQUIPAMENTOS', 'São Paulo', 'SP', '(11) 3456-7890', 'contato@medicaltech.com.br', 'João Silva'),
                ('HOSPITECH SOLUÇÕES MÉDICAS', '23.456.789/0001-01', 'EQUIPAMENTOS', 'São Paulo', 'SP', '(11) 2345-6789', 'vendas@hospitech.com.br', 'Maria Santos'),
                ('BIOMEDICAL EQUIPAMENTOS', '34.567.890/0001-12', 'EQUIPAMENTOS', 'Goiânia', 'GO', '(62) 3456-7890', 'contato@biomedical.com.br', 'Carlos Lima'),
                ('PHARMA DISTRIBUIDORA', '45.678.901/0001-23', 'MEDICAMENTOS', 'Rio de Janeiro', 'RJ', '(21) 3456-7890', 'vendas@pharma.com.br', 'Ana Costa'),
                ('MEDICAL SUPPLIES LTDA', '56.789.012/0001-34', 'MATERIAIS', 'Brasília', 'DF', '(61) 3456-7890', 'contato@medicalsupplies.com.br', 'Pedro Oliveira')
            ]
            
            for fornecedor in fornecedores:
                cursor.execute("""
                    INSERT INTO fornecedores (nome, cnpj, categoria, cidade, uf, telefone, email, responsavel)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, fornecedor)
        
        # Verificar se já existem plataformas
        cursor.execute('SELECT COUNT(*) FROM plataformas')
        if cursor.fetchone()[0] == 0:
            plataformas = [
                ('Comprasnet (Compras Públicas)', 'https://www.comprasnet.gov.br', 'imagemhosp', 'HS32521210', 'Portal oficial de compras do Governo Federal'),
                ('BLL (Bolsa de Licitações)', 'https://www.bll.org.br', '', '', 'Bolsa de Licitações e Leilões do Brasil'),
                ('Licitação-E (Banco do Brasil)', 'https://www.licitacoes-e.com.br', 'JF648886', 'Lic74125', 'Plataforma de licitações eletrônicas do BB'),
                ('BNC (Bolsa Nacional de Compras)', 'https://www.bnc.org.br', '', '', 'Bolsa Nacional de Compras'),
                ('Licitanet', 'https://www.licitanet.com.br', '01943800170', 'HS32521210', 'Portal de licitações Licitanet'),
                ('Publinexo', 'https://www.publinexo.com.br', 'adm@imagemhospitalar', 'Licita4152@', 'Plataforma Publinexo de licitações'),
                ('Compras GO', 'https://www.comprasgovernamentais.gov.br', '', '', 'Portal de Compras Governamentais'),
                ('SlicX', 'https://www.slicx.com.br', 'Hopshop', 'HS32521210@$', 'Plataforma SlicX de licitações')
            ]
            
            for plataforma in plataformas:
                cursor.execute("""
                    INSERT INTO plataformas (nome, url, login, senha, descricao)
                    VALUES (%s, %s, %s, %s, %s)
                """, plataforma)
        
        # Verificar se já existem licitações
        cursor.execute('SELECT COUNT(*) FROM licitacoes')
        if cursor.fetchone()[0] == 0:
            licitacoes = [
                ('PE 001/2025', 'Hospital Municipal de São Paulo', 'Aquisição de equipamentos médicos hospitalares', 'Pregão Eletrônico', 250000.00, '2025-10-15', 'aberta', 'Comprasnet'),
                ('CC 002/2025', 'Secretaria de Saúde do Estado', 'Fornecimento de materiais médico-hospitalares', 'Concorrência', 500000.00, '2025-10-20', 'aberta', 'BLL'),
                ('TP 003/2025', 'Hospital das Clínicas', 'Manutenção de equipamentos médicos', 'Tomada de Preços', 150000.00, '2025-10-25', 'aberta', 'Licitanet')
            ]
            
            for licitacao in licitacoes:
                cursor.execute("""
                    INSERT INTO licitacoes (numero, orgao, objeto, modalidade, valor_estimado, data_abertura, status, plataforma_origem)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, licitacao)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Dados de exemplo carregados com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

# Template HTML principal
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospshop - Sistema de Licitações</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; }
        .navbar { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
        .card { border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
        .btn-primary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border: none; }
        .stats-card { border-left: 4px solid #667eea; }
        .badge-online { background-color: #28a745; }
    </style>
</head>
<body>
    {% if not session.username %}
    <!-- Login Form -->
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h3 class="text-center mb-4">
                            <i class="fas fa-hospital"></i> Hospshop
                            <small class="d-block text-muted">Sistema Online</small>
                        </h3>
                        <form method="POST" action="/login">
                            <div class="mb-3">
                                <label class="form-label">Usuário</label>
                                <input type="text" class="form-control" name="username" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Senha</label>
                                <input type="password" class="form-control" name="password" required>
                            </div>
                            <button type="submit" class="btn btn-primary w-100">Entrar</button>
                        </form>
                        <div class="mt-3 text-center">
                            <small>Teste: admin / admin123</small>
                            <br><span class="badge badge-online">🟢 Sistema Online</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <!-- Dashboard -->
    <nav class="navbar navbar-expand-lg navbar-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="#"><i class="fas fa-hospital"></i> Hospshop</a>
            <div class="navbar-nav ms-auto">
                <span class="navbar-text me-3">🟢 Online</span>
                <a class="nav-link" href="/logout">Sair ({{ session.username }})</a>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-2">
                <div class="card">
                    <div class="list-group list-group-flush">
                        <a href="#" class="list-group-item list-group-item-action active" onclick="showSection('dashboard')">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                        <a href="#" class="list-group-item list-group-item-action" onclick="showSection('fornecedores')">
                            <i class="fas fa-building"></i> Fornecedores
                        </a>
                        <a href="#" class="list-group-item list-group-item-action" onclick="showSection('licitacoes')">
                            <i class="fas fa-gavel"></i> Licitações
                        </a>
                        <a href="#" class="list-group-item list-group-item-action" onclick="showSection('plataformas')">
                            <i class="fas fa-globe"></i> Plataformas
                        </a>
                    </div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="col-md-10">
                <!-- Dashboard Section -->
                <div id="dashboard" class="content-section">
                    <h2>Dashboard <small class="text-muted">Sistema Online</small></h2>
                    <div class="row mb-4">
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h3 id="total-fornecedores">{{ stats.fornecedores }}</h3>
                                    <p>Fornecedores</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h3 id="total-licitacoes">{{ stats.licitacoes }}</h3>
                                    <p>Licitações</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h3 id="total-plataformas">{{ stats.plataformas }}</h3>
                                    <p>Plataformas</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="card stats-card">
                                <div class="card-body">
                                    <h3>{{ stats.licitacoes_abertas }}</h3>
                                    <p>Abertas</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Fornecedores Section -->
                <div id="fornecedores" class="content-section" style="display: none;">
                    <h2>Fornecedores</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Nome</th>
                                            <th>CNPJ</th>
                                            <th>Categoria</th>
                                            <th>Cidade/UF</th>
                                            <th>Telefone</th>
                                            <th>Responsável</th>
                                        </tr>
                                    </thead>
                                    <tbody id="fornecedores-list">
                                        <!-- Carregado via JavaScript -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Licitações Section -->
                <div id="licitacoes" class="content-section" style="display: none;">
                    <h2>Licitações</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Número</th>
                                            <th>Órgão</th>
                                            <th>Objeto</th>
                                            <th>Modalidade</th>
                                            <th>Valor</th>
                                            <th>Data Abertura</th>
                                            <th>Status</th>
                                            <th>Plataforma</th>
                                        </tr>
                                    </thead>
                                    <tbody id="licitacoes-list">
                                        <!-- Carregado via JavaScript -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Plataformas Section -->
                <div id="plataformas" class="content-section" style="display: none;">
                    <h2>Plataformas</h2>
                    <div class="card">
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Nome</th>
                                            <th>URL</th>
                                            <th>Login</th>
                                            <th>Descrição</th>
                                            <th>Status</th>
                                        </tr>
                                    </thead>
                                    <tbody id="plataformas-list">
                                        <!-- Carregado via JavaScript -->
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        function showSection(sectionName) {
            // Esconder todas as seções
            document.querySelectorAll('.content-section').forEach(section => {
                section.style.display = 'none';
            });
            
            // Mostrar seção selecionada
            document.getElementById(sectionName).style.display = 'block';
            
            // Atualizar navegação
            document.querySelectorAll('.list-group-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // Carregar dados da seção
            if (sectionName === 'fornecedores') {
                fetch('/api/fornecedores')
                    .then(response => response.json())
                    .then(data => {
                        let list = document.getElementById('fornecedores-list');
                        list.innerHTML = '';
                        data.forEach(item => {
                            list.innerHTML += `<tr><td>${item.nome}</td><td>${item.cnpj}</td><td>${item.categoria}</td><td>${item.cidade}/${item.uf}</td><td>${item.telefone}</td><td>${item.responsavel}</td></tr>`;
                        });
                    });
            } else if (sectionName === 'licitacoes') {
                fetch('/api/licitacoes')
                    .then(response => response.json())
                    .then(data => {
                        let list = document.getElementById('licitacoes-list');
                        list.innerHTML = '';
                        data.forEach(item => {
                            list.innerHTML += `<tr><td>${item.numero}</td><td>${item.orgao}</td><td>${item.objeto}</td><td>${item.modalidade}</td><td>R$ ${item.valor_estimado.toFixed(2)}</td><td>${item.data_abertura}</td><td><span class="badge bg-success">${item.status}</span></td><td>${item.plataforma_origem || 'N/A'}</td></tr>`;
                        });
                    });
            } else if (sectionName === 'plataformas') {
                fetch('/api/plataformas')
                    .then(response => response.json())
                    .then(data => {
                        let list = document.getElementById('plataformas-list');
                        list.innerHTML = '';
                        data.forEach(item => {
                            list.innerHTML += `<tr><td>${item.nome}</td><td><a href="${item.url}" target="_blank">${item.url}</a></td><td>${item.login}</td><td>${item.descricao}</td><td><span class="badge bg-success">Ativo</span></td></tr>`;
                        });
                    });
            }
        }

        // Carregar dashboard por padrão
        document.addEventListener('DOMContentLoaded', function() {
            showSection('dashboard');
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if 'username' not in session:
        return render_template_string(HTML_TEMPLATE)
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM fornecedores')
        total_fornecedores = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM licitacoes')
        total_licitacoes = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM plataformas')
        total_plataformas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM licitacoes WHERE status = 'aberta'")
        licitacoes_abertas = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        stats = {
            'fornecedores': total_fornecedores,
            'licitacoes': total_licitacoes,
            'plataformas': total_plataformas,
            'licitacoes_abertas': licitacoes_abertas
        }
        
        return render_template_string(HTML_TEMPLATE, stats=stats)
    except Exception as e:
        print(f"Erro no dashboard: {e}")
        return render_template_string(HTML_TEMPLATE, stats={'fornecedores': 0, 'licitacoes': 0, 'plataformas': 0, 'licitacoes_abertas': 0})

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT username, nivel FROM usuarios WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session['username'] = user[0]
            session['nivel'] = user[1]
            return redirect(url_for('index'))
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Erro no login: {e}")
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/fornecedores')
def api_fornecedores():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, cnpj, categoria, cidade, uf, telefone, email, responsavel FROM fornecedores ORDER BY nome')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        fornecedores = []
        for row in rows:
            fornecedores.append({
                'id': row[0],
                'nome': row[1],
                'cnpj': row[2],
                'categoria': row[3],
                'cidade': row[4],
                'uf': row[5],
                'telefone': row[6],
                'email': row[7],
                'responsavel': row[8]
            })
        
        return jsonify(fornecedores)
    except Exception as e:
        print(f"Erro na API fornecedores: {e}")
        return jsonify([])

@app.route('/api/licitacoes')
def api_licitacoes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, numero, orgao, objeto, modalidade, valor_estimado, data_abertura, status, plataforma_origem FROM licitacoes ORDER BY data_abertura DESC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        licitacoes = []
        for row in rows:
            licitacoes.append({
                'id': row[0],
                'numero': row[1],
                'orgao': row[2],
                'objeto': row[3],
                'modalidade': row[4],
                'valor_estimado': float(row[5]) if row[5] is not None else 0,
                'data_abertura': row[6].isoformat() if row[6] is not None else None,
                'status': row[7],
                'plataforma_origem': row[8]
            })
        
        return jsonify(licitacoes)
    except Exception as e:
        print(f"Erro na API licitações: {e}")
        return jsonify([])

@app.route('/api/plataformas')
def api_plataformas():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, url, login, senha, descricao FROM plataformas ORDER BY nome')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        plataformas = []
        for row in rows:
            plataformas.append({
                'id': row[0],
                'nome': row[1],
                'url': row[2],
                'login': row[3],
                'senha': '***' if row[4] else '',
                'descricao': row[5]
            })
        
        return jsonify(plataformas)
    except Exception as e:
        print(f"Erro na API plataformas: {e}")
        return jsonify([])

@app.route('/health')
def health():
    """Endpoint de saúde para monitoramento"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"})
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    if DATABASE_URL:
        print("🚀 Iniciando Sistema Hospshop no Railway...")
        init_db()
        load_sample_data()
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:
        print("❌ DATABASE_URL não encontrada. Verifique as configurações do Railway.")
        app.run(host='0.0.0.0', port=8080, debug=True)
