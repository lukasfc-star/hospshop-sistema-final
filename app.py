import os
import psycopg2
from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hospshop-secret-key-2024')

# Configuração do banco de dados
DATABASE_URL = os.environ.get('URL_DO_BANCO_DE_DADOS')

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        app.logger.error(f"Erro na conexão com banco: {e}")
        return None

def init_db():
    """Inicializa o banco de dados com as tabelas necessárias"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        # Criar tabela de usuários
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de fornecedores
        cur.execute('''
            CREATE TABLE IF NOT EXISTS fornecedores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                cnpj VARCHAR(18),
                categoria VARCHAR(100),
                cidade VARCHAR(100),
                estado VARCHAR(2),
                telefone VARCHAR(20),
                email VARCHAR(100),
                responsavel VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de licitações
        cur.execute('''
            CREATE TABLE IF NOT EXISTS licitacoes (
                id SERIAL PRIMARY KEY,
                numero VARCHAR(50) NOT NULL,
                orgao VARCHAR(255) NOT NULL,
                objeto TEXT NOT NULL,
                modalidade VARCHAR(50),
                valor DECIMAL(15,2),
                data_abertura DATE,
                status VARCHAR(20) DEFAULT 'ABERTA',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Criar tabela de plataformas
        cur.execute('''
            CREATE TABLE IF NOT EXISTS plataformas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                url VARCHAR(255),
                login VARCHAR(100),
                descricao TEXT,
                status VARCHAR(20) DEFAULT 'ATIVO',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inserir usuário admin padrão
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cur.fetchone()[0] == 0:
            admin_hash = generate_password_hash('admin123')
            cur.execute(
                "INSERT INTO usuarios (username, password_hash, email) VALUES (%s, %s, %s)",
                ('admin', admin_hash, 'admin@hospshop.com')
            )
        
        # Inserir dados de exemplo
        cur.execute("SELECT COUNT(*) FROM fornecedores")
        if cur.fetchone()[0] == 0:
            fornecedores_exemplo = [
                ('MEDICALTECH EQUIPAMENTOS LTDA', '12.345.678/0001-90', 'EQUIPAMENTOS', 'São Paulo', 'SP', '(11) 3456-7890', 'contato@medicaltech.com', 'João Silva'),
                ('HOSPITECH SOLUÇÕES MÉDICAS', '23.456.789/0001-01', 'EQUIPAMENTOS', 'São Paulo', 'SP', '(11) 2345-6789', 'vendas@hospitech.com', 'Maria Santos'),
                ('BIOMEDICAL EQUIPAMENTOS', '34.567.890/0001-12', 'EQUIPAMENTOS', 'Goiânia', 'GO', '(62) 3456-7890', 'comercial@biomedical.com', 'Carlos Oliveira'),
                ('PHARMA DISTRIBUIDORA', '45.678.901/0001-23', 'MEDICAMENTOS', 'Rio de Janeiro', 'RJ', '(21) 3456-7890', 'pedidos@pharma.com', 'Ana Costa'),
                ('MEDICAL SUPPLIES LTDA', '56.789.012/0001-34', 'MATERIAIS', 'Brasília', 'DF', '(61) 3456-7890', 'suprimentos@medical.com', 'Pedro Lima')
            ]
            
            for fornecedor in fornecedores_exemplo:
                cur.execute(
                    "INSERT INTO fornecedores (nome, cnpj, categoria, cidade, estado, telefone, email, responsavel) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    fornecedor
                )
        
        cur.execute("SELECT COUNT(*) FROM licitacoes")
        if cur.fetchone()[0] == 0:
            licitacoes_exemplo = [
                ('PE 001/2025', 'Hospital Municipal de São Paulo', 'Aquisição de equipamentos médicos', 'Pregão Eletrônico', 250000.00, '2025-01-15', 'ABERTA'),
                ('CC 002/2025', 'Secretaria de Saúde do Estado', 'Fornecimento de materiais médico-hospitalares', 'Concorrência', 500000.00, '2025-01-20', 'ABERTA'),
                ('TP 003/2025', 'Hospital das Clínicas', 'Manutenção de equipamentos médicos', 'Tomada de Preços', 150000.00, '2025-01-25', 'ABERTA')
            ]
            
            for licitacao in licitacoes_exemplo:
                cur.execute(
                    "INSERT INTO licitacoes (numero, orgao, objeto, modalidade, valor, data_abertura, status) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    licitacao
                )
        
        cur.execute("SELECT COUNT(*) FROM plataformas")
        if cur.fetchone()[0] == 0:
            plataformas_exemplo = [
                ('Comprasnet (Compras Públicas)', 'https://www.comprasnet.gov.br', 'imagemhosp', 'Portal oficial do Governo Federal'),
                ('BLL (Bolsa de Licitações)', 'https://www.bll.org.br', '', 'Bolsa de Licitações e Leilões do Brasil'),
                ('Licitação-E (Banco do Brasil)', 'https://www.licitacoes-e.com.br', 'JF648886', 'Plataforma de licitações eletrônicas do BB'),
                ('BNC (Bolsa Nacional de Compras)', 'https://www.bnc.org.br', '', 'Bolsa Nacional de Compras'),
                ('Licitanet', 'https://www.licitanet.com.br', '01943800170', 'Portal de licitações Licitanet'),
                ('Publinexo', 'https://www.publinexo.com.br', 'adm@imagemhospitalar', 'Plataforma Publinexo de licitações'),
                ('Compras GO', 'https://www.comprasgovernamentais.gov.br', '', 'Portal de Compras Governamentais'),
                ('SlicX', 'https://www.slicx.com.br', 'Hopshop', 'Plataforma SlicX de licitações')
            ]
            
            for plataforma in plataformas_exemplo:
                cur.execute(
                    "INSERT INTO plataformas (nome, url, login, descricao) VALUES (%s, %s, %s, %s)",
                    plataforma
                )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        app.logger.error(f"Erro ao inicializar banco: {e}")
        if conn:
            conn.close()
        return False

# Template HTML principal
login_html = '''
{% extends "base.html" %}
{% block content %}
...

'''

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            return "Erro de conexão com banco de dados", 500
        
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, password_hash FROM usuarios WHERE username = %s", (username,))
            user = cur.fetchone()
            
            if user and check_password_hash(user[1], password):
                session['user_id'] = user[0]
                session['username'] = username
                return redirect(url_for('dashboard'))
            else:
                error = "Usuário ou senha inválidos"
                
        except Exception as e:
            error = f"Erro no login: {e}"
        finally:
            cur.close()
            conn.close()
    
    login_html = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hospshop - Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: #333;
        }
        .login-form {
            max-width: 400px; margin: 100px auto;
            background: rgba(255, 255, 255, 0.95);
            padding: 40px; border-radius: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; color: #2c3e50; }
        .form-group input {
            width: 100%; padding: 12px; border: 2px solid #ddd;
            border-radius: 8px; font-size: 16px;
        }
        .btn-primary {
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white; padding: 12px 30px; border: none;
            border-radius: 25px; cursor: pointer; font-size: 16px; width: 100%;
        }
    </style>
</head>
<body>
    <div class="login-form">
        <h2 style="text-align: center; color: #2c3e50; margin-bottom: 30px;">🏥 Hospshop Login</h2>
        {% if error %}
        <div style="background: #e74c3c; color: white; padding: 10px; border-radius: 5px; margin-bottom: 20px; text-align: center;">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <div class="form-group">
                <label for="username">Usuário:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="form-group">
                <label for="password">Senha:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit" class="btn-primary">Entrar</button>
        </form>
        <div style="text-align: center; margin-top: 20px; color: #7f8c8d;">
            <small>Usuário: admin | Senha: admin123</small>
        </div>
    </div>
</body>
</html>
    '''
    
    return render_template_string(login_html, error=locals().get('error'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão com banco de dados", 500
    
    try:
        cur = conn.cursor()
        
        # Contar estatísticas
        cur.execute("SELECT COUNT(*) FROM fornecedores")
        total_fornecedores = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM licitacoes")
        total_licitacoes = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM plataformas")
        total_plataformas = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM licitacoes WHERE status = 'ABERTA'")
        licitacoes_abertas = cur.fetchone()[0]
        
    except Exception as e:
        return f"Erro ao carregar dashboard: {e}", 500
    finally:
        cur.close()
        conn.close()
    
    dashboard_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="container">
        <div class="header">
            <h1>🏥 Sistema Hospshop</h1>
            <p style="text-align: center; color: #7f8c8d; font-size: 1.2em;">
                Gestão Inteligente de Licitações Hospitalares
            </p>
            <div class="nav">
                <a href="{{ url_for('fornecedores') }}" class="nav-btn">👥 Fornecedores</a>
                <a href="{{ url_for('licitacoes') }}" class="nav-btn">📋 Licitações</a>
                <a href="{{ url_for('plataformas') }}" class="nav-btn">🌐 Plataformas</a>
                <a href="{{ url_for('logout') }}" class="logout-btn">🚪 Sair</a>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">📊 Dashboard</h2>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{{ total_fornecedores }}</h3>
                    <p>Fornecedores</p>
                </div>
                <div class="stat-card">
                    <h3>{{ total_licitacoes }}</h3>
                    <p>Licitações</p>
                </div>
                <div class="stat-card">
                    <h3>{{ total_plataformas }}</h3>
                    <p>Plataformas</p>
                </div>
                <div class="stat-card">
                    <h3>{{ licitacoes_abertas }}</h3>
                    <p>Licitações Abertas</p>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: #7f8c8d; font-size: 1.1em;">
                    Bem-vindo ao sistema, <strong>{{ session.username }}</strong>! 
                    Selecione uma opção no menu acima para começar.
                </p>
            </div>
        </div>
    </div>
    {% endblock %}
    '''
    
    return render_template_string(HTML_TEMPLATE + dashboard_html, 
                                total_fornecedores=total_fornecedores,
                                total_licitacoes=total_licitacoes,
                                total_plataformas=total_plataformas,
                                licitacoes_abertas=licitacoes_abertas,
                                session=session)

@app.route('/fornecedores')
def fornecedores():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão com banco de dados", 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM fornecedores ORDER BY nome")
        fornecedores_data = cur.fetchall()
        
    except Exception as e:
        return f"Erro ao carregar fornecedores: {e}", 500
    finally:
        cur.close()
        conn.close()
    
    fornecedores_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="container">
        <div class="header">
            <h1>👥 Fornecedores</h1>
            <div class="nav">
                <a href="{{ url_for('dashboard') }}" class="nav-btn">🏠 Dashboard</a>
                <a href="{{ url_for('licitacoes') }}" class="nav-btn">📋 Licitações</a>
                <a href="{{ url_for('plataformas') }}" class="nav-btn">🌐 Plataformas</a>
                <a href="{{ url_for('logout') }}" class="logout-btn">🚪 Sair</a>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">Lista de Fornecedores</h2>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>CNPJ</th>
                        <th>Categoria</th>
                        <th>Localização</th>
                        <th>Telefone</th>
                        <th>Responsável</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fornecedor in fornecedores_data %}
                    <tr>
                        <td><strong>{{ fornecedor[1] }}</strong></td>
                        <td>{{ fornecedor[2] }}</td>
                        <td>{{ fornecedor[3] }}</td>
                        <td>{{ fornecedor[4] }}/{{ fornecedor[5] }}</td>
                        <td>{{ fornecedor[6] }}</td>
                        <td>{{ fornecedor[8] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    '''
    
    return render_template_string(HTML_TEMPLATE + fornecedores_html, 
                                fornecedores_data=fornecedores_data)

@app.route('/licitacoes')
def licitacoes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão com banco de dados", 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM licitacoes ORDER BY data_abertura DESC")
        licitacoes_data = cur.fetchall()
        
    except Exception as e:
        return f"Erro ao carregar licitações: {e}", 500
    finally:
        cur.close()
        conn.close()
    
    licitacoes_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="container">
        <div class="header">
            <h1>📋 Licitações</h1>
            <div class="nav">
                <a href="{{ url_for('dashboard') }}" class="nav-btn">🏠 Dashboard</a>
                <a href="{{ url_for('fornecedores') }}" class="nav-btn">👥 Fornecedores</a>
                <a href="{{ url_for('plataformas') }}" class="nav-btn">🌐 Plataformas</a>
                <a href="{{ url_for('logout') }}" class="logout-btn">🚪 Sair</a>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">Lista de Licitações</h2>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Número</th>
                        <th>Órgão</th>
                        <th>Objeto</th>
                        <th>Modalidade</th>
                        <th>Valor</th>
                        <th>Data Abertura</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for licitacao in licitacoes_data %}
                    <tr>
                        <td><strong>{{ licitacao[1] }}</strong></td>
                        <td>{{ licitacao[2] }}</td>
                        <td>{{ licitacao[3] }}</td>
                        <td>{{ licitacao[4] }}</td>
                        <td>R$ {{ "{:,.2f}".format(licitacao[5]) if licitacao[5] else "N/A" }}</td>
                        <td>{{ licitacao[6].strftime('%d/%m/%Y') if licitacao[6] else "N/A" }}</td>
                        <td><span class="status-badge status-aberta">{{ licitacao[7] }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    '''
    
    return render_template_string(HTML_TEMPLATE + licitacoes_html, 
                                licitacoes_data=licitacoes_data)

@app.route('/plataformas')
def plataformas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        return "Erro de conexão com banco de dados", 500
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM plataformas ORDER BY nome")
        plataformas_data = cur.fetchall()
        
    except Exception as e:
        return f"Erro ao carregar plataformas: {e}", 500
    finally:
        cur.close()
        conn.close()
    
    plataformas_html = '''
    {% extends "base.html" %}
    {% block content %}
    <div class="container">
        <div class="header">
            <h1>🌐 Plataformas</h1>
            <div class="nav">
                <a href="{{ url_for('dashboard') }}" class="nav-btn">🏠 Dashboard</a>
                <a href="{{ url_for('fornecedores') }}" class="nav-btn">👥 Fornecedores</a>
                <a href="{{ url_for('licitacoes') }}" class="nav-btn">📋 Licitações</a>
                <a href="{{ url_for('logout') }}" class="logout-btn">🚪 Sair</a>
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">Plataformas de Licitação</h2>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>URL</th>
                        <th>Login</th>
                        <th>Descrição</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for plataforma in plataformas_data %}
                    <tr>
                        <td><strong>{{ plataforma[1] }}</strong></td>
                        <td>
                            {% if plataforma[2] %}
                            <a href="{{ plataforma[2] }}" target="_blank" style="color: #3498db;">{{ plataforma[2] }}</a>
                            {% else %}
                            N/A
                            {% endif %}
                        </td>
                        <td>{{ plataforma[3] if plataforma[3] else "N/A" }}</td>
                        <td>{{ plataforma[4] }}</td>
                        <td><span class="status-badge status-ativo">{{ plataforma[5] }}</span></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endblock %}
    '''
    
    return render_template_string(HTML_TEMPLATE + plataformas_html, 
                                plataformas_data=plataformas_data)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "hospshop"})

if __name__ == '__main__':
    # Inicializar banco de dados
    if init_db():
        app.logger.info("Banco de dados inicializado com sucesso")
    else:
        app.logger.error("Erro ao inicializar banco de dados")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
