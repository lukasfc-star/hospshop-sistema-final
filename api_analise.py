#!/usr/bin/env python3
"""
API REST - Módulo de Análise de Concorrentes
Sistema Hospshop

Servidor Flask que fornece endpoints para o dashboard React
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps
import json

# Configurações
DB_PATH = os.path.join(os.path.dirname(__file__), 'analise_concorrentes.db')
app = Flask(__name__)

# Configurar CORS para permitir acesso do React
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # Em produção, especificar domínios permitidos
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def get_db_connection():
    """Cria conexão com o banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Retornar resultados como dicionários
    return conn

def dict_from_row(row):
    """Converte sqlite3.Row para dicionário"""
    return dict(zip(row.keys(), row))

def calcular_tempo_decorrido(data_str):
    """Calcula tempo decorrido desde uma data"""
    if not data_str:
        return "N/A"
    
    try:
        data = datetime.fromisoformat(data_str)
        agora = datetime.now()
        diff = agora - data
        
        if diff.days > 0:
            return f"{diff.days}d"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h"
        else:
            return f"{diff.seconds // 60}min"
    except:
        return "N/A"

# ============================================================================
# ENDPOINTS - MÉTRICAS
# ============================================================================

@app.route('/api/metricas', methods=['GET'])
def get_metricas():
    """Retorna métricas gerais do sistema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total de irregularidades
        cursor.execute("SELECT COUNT(*) as total FROM irregularidades")
        total_irregularidades = cursor.fetchone()['total']
        
        # Total de recursos gerados
        cursor.execute("SELECT COUNT(*) as total FROM recursos_juridicos")
        total_recursos = cursor.fetchone()['total']
        
        # Economia estimada total
        cursor.execute("SELECT COALESCE(SUM(economia_estimada), 0) as total FROM recursos_juridicos")
        economia_total = cursor.fetchone()['total']
        
        # Taxa de sucesso (recursos deferidos / recursos enviados)
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status IN ('deferido', 'parcialmente_deferido') THEN 1 END) as deferidos,
                COUNT(CASE WHEN status IN ('deferido', 'parcialmente_deferido', 'indeferido') THEN 1 END) as total
            FROM recursos_juridicos
        """)
        resultado = cursor.fetchone()
        taxa_sucesso = (resultado['deferidos'] / resultado['total'] * 100) if resultado['total'] > 0 else 0
        
        conn.close()
        
        return jsonify({
            'irregularidades_detectadas': total_irregularidades,
            'recursos_gerados': total_recursos,
            'economia_estimada': round(economia_total, 2),
            'taxa_sucesso': round(taxa_sucesso, 1)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - LICITAÇÕES
# ============================================================================

@app.route('/api/licitacoes', methods=['GET'])
def get_licitacoes():
    """Retorna lista de licitações"""
    try:
        status = request.args.get('status', 'em_analise')
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar licitações com contagem de concorrentes e irregularidades
        cursor.execute("""
            SELECT 
                l.*,
                COUNT(DISTINCT c.id) as total_concorrentes,
                COUNT(DISTINCT i.id) as total_irregularidades
            FROM licitacoes_analise l
            LEFT JOIN concorrentes c ON l.id = c.licitacao_id
            LEFT JOIN irregularidades i ON l.id = i.licitacao_id
            WHERE l.status = ?
            GROUP BY l.id
            ORDER BY l.data_abertura DESC
            LIMIT ?
        """, (status, limit))
        
        licitacoes_raw = cursor.fetchall()
        
        # Formatar resultados
        licitacoes = []
        for row in licitacoes_raw:
            lic = dict_from_row(row)
            
            # Calcular tempo de análise
            if lic['created_at']:
                lic['tempo_analise'] = calcular_tempo_decorrido(lic['created_at'])
            else:
                lic['tempo_analise'] = 'N/A'
            
            # Calcular tempo restante para recurso
            if lic['data_limite_recurso']:
                try:
                    limite = datetime.fromisoformat(lic['data_limite_recurso'])
                    agora = datetime.now()
                    diff = limite - agora
                    
                    if diff.total_seconds() > 0:
                        if diff.days > 0:
                            lic['tempo_restante'] = f"{diff.days}d {diff.seconds // 3600}h"
                        else:
                            lic['tempo_restante'] = f"{diff.seconds // 3600}h {(diff.seconds % 3600) // 60}min"
                    else:
                        lic['tempo_restante'] = 'Expirado'
                except:
                    lic['tempo_restante'] = 'N/A'
            else:
                lic['tempo_restante'] = 'N/A'
            
            licitacoes.append(lic)
        
        conn.close()
        
        return jsonify({
            'total': len(licitacoes),
            'licitacoes': licitacoes
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/licitacoes/<int:licitacao_id>', methods=['GET'])
def get_licitacao_detalhes(licitacao_id):
    """Retorna detalhes de uma licitação específica"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar licitação
        cursor.execute("SELECT * FROM licitacoes_analise WHERE id = ?", (licitacao_id,))
        licitacao = cursor.fetchone()
        
        if not licitacao:
            return jsonify({'error': 'Licitação não encontrada'}), 404
        
        lic = dict_from_row(licitacao)
        
        # Buscar concorrentes
        cursor.execute("""
            SELECT c.*, COUNT(i.id) as total_irregularidades
            FROM concorrentes c
            LEFT JOIN irregularidades i ON c.id = i.concorrente_id
            WHERE c.licitacao_id = ?
            GROUP BY c.id
            ORDER BY c.posicao
        """, (licitacao_id,))
        
        lic['concorrentes'] = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Buscar irregularidades
        cursor.execute("""
            SELECT i.*, c.nome_empresa
            FROM irregularidades i
            JOIN concorrentes c ON i.concorrente_id = c.id
            WHERE i.licitacao_id = ?
            ORDER BY i.detectado_em DESC
        """, (licitacao_id,))
        
        lic['irregularidades'] = [dict_from_row(row) for row in cursor.fetchall()]
        
        # Buscar recursos
        cursor.execute("""
            SELECT * FROM recursos_juridicos
            WHERE licitacao_id = ?
            ORDER BY gerado_em DESC
        """, (licitacao_id,))
        
        lic['recursos'] = [dict_from_row(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify(lic)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - IRREGULARIDADES
# ============================================================================

@app.route('/api/irregularidades', methods=['GET'])
def get_irregularidades():
    """Retorna lista de irregularidades"""
    try:
        limit = request.args.get('limit', 10, type=int)
        gravidade = request.args.get('gravidade', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query
        query = """
            SELECT 
                i.*,
                c.nome_empresa,
                l.numero_licitacao,
                l.orgao
            FROM irregularidades i
            JOIN concorrentes c ON i.concorrente_id = c.id
            JOIN licitacoes_analise l ON i.licitacao_id = l.id
        """
        
        params = []
        if gravidade:
            query += " WHERE i.gravidade = ?"
            params.append(gravidade)
        
        query += " ORDER BY i.detectado_em DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        irregularidades_raw = cursor.fetchall()
        
        # Formatar resultados
        irregularidades = []
        for row in irregularidades_raw:
            irreg = dict_from_row(row)
            irreg['tempo_decorrido'] = calcular_tempo_decorrido(irreg['detectado_em'])
            irregularidades.append(irreg)
        
        conn.close()
        
        return jsonify({
            'total': len(irregularidades),
            'irregularidades': irregularidades
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - RECURSOS JURÍDICOS
# ============================================================================

@app.route('/api/recursos', methods=['GET'])
def get_recursos():
    """Retorna lista de recursos jurídicos"""
    try:
        limit = request.args.get('limit', 10, type=int)
        status = request.args.get('status', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir query
        query = """
            SELECT 
                r.*,
                l.numero_licitacao,
                l.orgao
            FROM recursos_juridicos r
            JOIN licitacoes_analise l ON r.licitacao_id = l.id
        """
        
        params = []
        if status:
            query += " WHERE r.status = ?"
            params.append(status)
        
        query += " ORDER BY r.gerado_em DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        recursos_raw = cursor.fetchall()
        
        # Formatar resultados
        recursos = []
        for row in recursos_raw:
            rec = dict_from_row(row)
            rec['tempo_decorrido'] = calcular_tempo_decorrido(rec['gerado_em'])
            recursos.append(rec)
        
        conn.close()
        
        return jsonify({
            'total': len(recursos),
            'recursos': recursos
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - GRÁFICOS
# ============================================================================

@app.route('/api/graficos/irregularidades-por-tipo', methods=['GET'])
def get_grafico_irregularidades():
    """Retorna dados para gráfico de irregularidades por tipo"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                tipo,
                COUNT(*) as total
            FROM irregularidades
            GROUP BY tipo
            ORDER BY total DESC
        """)
        
        resultados = cursor.fetchall()
        conn.close()
        
        # Mapear tipos para labels legíveis
        labels_map = {
            'documento_vencido': 'Doc. Vencido',
            'especificacao_nao_conforme': 'Espec. Não Conforme',
            'certidao_irregular': 'Certidão Irregular',
            'exigencia_nao_cumprida': 'Exigência Não Cumprida',
            'divergencia_valores': 'Divergência Valores',
            'prazo_entrega_incompativel': 'Prazo Incompatível',
            'marca_nao_aprovada': 'Marca Não Aprovada',
            'documentacao_incompleta': 'Doc. Incompleta'
        }
        
        labels = [labels_map.get(row['tipo'], row['tipo']) for row in resultados]
        valores = [row['total'] for row in resultados]
        
        return jsonify({
            'labels': labels,
            'valores': valores
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/graficos/recursos-timeline', methods=['GET'])
def get_grafico_recursos_timeline():
    """Retorna dados para gráfico de timeline de recursos"""
    try:
        periodo_dias = request.args.get('periodo', 30, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Buscar recursos dos últimos N dias
        data_inicio = (datetime.now() - timedelta(days=periodo_dias)).isoformat()
        
        cursor.execute("""
            SELECT 
                DATE(gerado_em) as data,
                COUNT(*) as total_gerados,
                SUM(CASE WHEN status IN ('deferido', 'parcialmente_deferido') THEN 1 ELSE 0 END) as deferidos,
                SUM(CASE WHEN status = 'indeferido' THEN 1 ELSE 0 END) as indeferidos
            FROM recursos_juridicos
            WHERE gerado_em >= ?
            GROUP BY DATE(gerado_em)
            ORDER BY data
        """, (data_inicio,))
        
        resultados = cursor.fetchall()
        conn.close()
        
        # Formatar datas
        labels = []
        gerados = []
        deferidos = []
        indeferidos = []
        
        for row in resultados:
            try:
                data = datetime.fromisoformat(row['data'])
                labels.append(data.strftime('%d/%m'))
            except:
                labels.append(row['data'])
            
            gerados.append(row['total_gerados'])
            deferidos.append(row['deferidos'])
            indeferidos.append(row['indeferidos'])
        
        return jsonify({
            'labels': labels,
            'gerados': gerados,
            'deferidos': deferidos,
            'indeferidos': indeferidos
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - ANALISTAS
# ============================================================================

@app.route('/api/analistas', methods=['GET'])
def get_analistas():
    """Retorna lista de analistas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analistas
            WHERE ativo = 1
            ORDER BY nome
        """)
        
        analistas = [dict_from_row(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'total': len(analistas),
            'analistas': analistas
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - ALERTAS
# ============================================================================

@app.route('/api/alertas', methods=['GET'])
def get_alertas():
    """Retorna lista de alertas"""
    try:
        limit = request.args.get('limit', 10, type=int)
        enviado = request.args.get('enviado', None)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                a.*,
                l.numero_licitacao
            FROM alertas a
            LEFT JOIN licitacoes_analise l ON a.licitacao_id = l.id
        """
        
        params = []
        if enviado is not None:
            query += " WHERE a.enviado = ?"
            params.append(1 if enviado == 'true' else 0)
        
        query += " ORDER BY a.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        alertas_raw = cursor.fetchall()
        
        # Formatar resultados
        alertas = []
        for row in alertas_raw:
            alerta = dict_from_row(row)
            alerta['tempo_decorrido'] = calcular_tempo_decorrido(alerta['created_at'])
            
            # Parse JSON fields
            if alerta.get('canais'):
                try:
                    alerta['canais'] = json.loads(alerta['canais'])
                except:
                    pass
            
            if alerta.get('destinatarios'):
                try:
                    alerta['destinatarios'] = json.loads(alerta['destinatarios'])
                except:
                    pass
            
            alertas.append(alerta)
        
        conn.close()
        
        return jsonify({
            'total': len(alertas),
            'alertas': alertas
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - DASHBOARD
# ============================================================================

@app.route('/api/dashboard/resumo', methods=['GET'])
def get_dashboard_resumo():
    """Retorna resumo completo para o dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Métricas gerais
        cursor.execute("SELECT COUNT(*) as total FROM irregularidades")
        total_irregularidades = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM recursos_juridicos")
        total_recursos = cursor.fetchone()['total']
        
        cursor.execute("SELECT COALESCE(SUM(economia_estimada), 0) as total FROM recursos_juridicos")
        economia_total = cursor.fetchone()['total']
        
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status IN ('deferido', 'parcialmente_deferido') THEN 1 END) as deferidos,
                COUNT(CASE WHEN status IN ('deferido', 'parcialmente_deferido', 'indeferido') THEN 1 END) as total
            FROM recursos_juridicos
        """)
        resultado = cursor.fetchone()
        taxa_sucesso = (resultado['deferidos'] / resultado['total'] * 100) if resultado['total'] > 0 else 0
        
        # Licitações ativas
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM licitacoes_analise
            WHERE status = 'em_analise'
        """)
        licitacoes_ativas = cursor.fetchone()['total']
        
        # Alertas pendentes
        cursor.execute("""
            SELECT COUNT(*) as total
            FROM alertas
            WHERE enviado = 0
        """)
        alertas_pendentes = cursor.fetchone()['total']
        
        conn.close()
        
        return jsonify({
            'metricas': {
                'irregularidades_detectadas': total_irregularidades,
                'recursos_gerados': total_recursos,
                'economia_estimada': round(economia_total, 2),
                'taxa_sucesso': round(taxa_sucesso, 1)
            },
            'status': {
                'licitacoes_ativas': licitacoes_ativas,
                'alertas_pendentes': alertas_pendentes
            },
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ENDPOINTS - HEALTH CHECK
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    try:
        # Verificar conexão com banco
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Rota raiz"""
    return jsonify({
        'message': 'API do Módulo de Análise de Concorrentes - Sistema Hospshop',
        'version': '1.0.0',
        'endpoints': {
            'metricas': '/api/metricas',
            'licitacoes': '/api/licitacoes',
            'irregularidades': '/api/irregularidades',
            'recursos': '/api/recursos',
            'graficos': {
                'irregularidades': '/api/graficos/irregularidades-por-tipo',
                'recursos_timeline': '/api/graficos/recursos-timeline'
            },
            'analistas': '/api/analistas',
            'alertas': '/api/alertas',
            'dashboard': '/api/dashboard/resumo',
            'health': '/api/health'
        }
    })

# ============================================================================
# MAIN
# ============================================================================

def register_api_routes(main_app):
    """Registra as rotas da API no app principal"""
    print(f"\n🔧 Registrando rotas da API de Análise de Concorrentes...")
    print(f"📊 Total de rotas encontradas: {len(list(app.url_map.iter_rules()))}")
    
    rotas_registradas = 0
    # Registrar todas as rotas da API no app principal
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            try:
                main_app.add_url_rule(
                    rule.rule,
                    endpoint=f'analise_{rule.endpoint}',
                    view_func=app.view_functions[rule.endpoint],
                    methods=rule.methods
                )
                print(f"  ✅ {rule.rule} -> {rule.endpoint}")
                rotas_registradas += 1
            except Exception as e:
                print(f"  ❌ Erro ao registrar {rule.rule}: {e}")
    
    print(f"\n✅ Total de rotas registradas: {rotas_registradas}\n")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 API do Módulo de Análise de Concorrentes")
    print("   Sistema Hospshop")
    print("=" * 60)
    print(f"📁 Banco de dados: {DB_PATH}")
    print("🌐 Servidor iniciando...")
    print("=" * 60)
    
    # Verificar se banco existe
    if not os.path.exists(DB_PATH):
        print("❌ ERRO: Banco de dados não encontrado!")
        print("💡 Execute primeiro: python3 init_database.py")
        exit(1)
    
    # Iniciar servidor
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
