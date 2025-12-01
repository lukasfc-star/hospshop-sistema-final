"""
API REST do Sistema Hospshop
Integração entre backend Python e dashboard React

Desenvolvido em 01/12/2025
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging
from datetime import datetime
from functools import wraps
from auth import AuthSystem

# Importar todos os módulos
from effecti_integration import EffectiIntegration
from padronizacao import PadronizacaoCaptacao
from notifications import NotificationManager
from google_sheets_integration import GoogleSheetsIntegration
from ocr_document_analysis import OCRDocumentAnalyzer
from supplier_quotation_system import SupplierQuotationSystem
from email_templates import EmailTemplateSystem
from whatsapp_automation import WhatsAppAutomation
from proposal_assembly import ProposalAssembly
from contract_generation import ContractGeneration
from financial_control import FinancialControl
from payment_tracking import PaymentTracking
from logistics_management import LogisticsManagement
from reporting_system import ReportingSystem

# Configuração
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilitar CORS para o dashboard

# Inicializar sistema de autenticação
auth_system = AuthSystem()

# Decorator para proteger rotas
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        payload = auth_system.verificar_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido ou expirado'}), 401
        
        request.usuario = payload
        return f(*args, **kwargs)
    return decorated_function

# Decorator para verificar nível de acesso
def require_role(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'usuario'):
                return jsonify({'error': 'Não autenticado'}), 401
            
            if request.usuario['nivel_acesso'] not in roles:
                return jsonify({'error': 'Permissão negada'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Inicializar módulos
effecti = EffectiIntegration()
padronizacao = PadronizacaoCaptacao()
notifications = NotificationManager()
sheets = GoogleSheetsIntegration()
ocr = OCRDocumentAnalyzer()
quotations = SupplierQuotationSystem()
email_templates = EmailTemplateSystem()
whatsapp = WhatsAppAutomation()
proposals = ProposalAssembly()
contracts = ContractGeneration()
financial = FinancialControl()
payments = PaymentTracking()
logistics = LogisticsManagement()
reports = ReportingSystem()


# ==================== ENDPOINTS DE AUTENTICAÇÃO ====================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login de usuário"""
    try:
        data = request.json
        username = data.get('username')
        senha = data.get('senha')
        
        if not username or not senha:
            return jsonify({'error': 'Username e senha são obrigatórios'}), 400
        
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        resultado = auth_system.login(username, senha, ip_address, user_agent)
        return jsonify(resultado)
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Erro ao fazer login: {e}")
        return jsonify({'error': f'Erro ao fazer login: {str(e)}'}), 500

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    """Logout de usuário"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        auth_system.logout(token)
        return jsonify({'message': 'Logout realizado com sucesso'})
    except Exception as e:
        return jsonify({'error': f'Erro ao fazer logout: {str(e)}'}), 500

@app.route('/api/auth/me', methods=['GET'])
@require_auth
def me():
    """Retorna informações do usuário logado"""
    return jsonify(request.usuario)

@app.route('/api/auth/usuarios', methods=['GET'])
@require_auth
@require_role(['admin'])
def listar_usuarios():
    """Lista todos os usuários (apenas admin)"""
    try:
        usuarios = auth_system.listar_usuarios()
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({'error': f'Erro ao listar usuários: {str(e)}'}), 500

@app.route('/api/auth/usuarios', methods=['POST'])
@require_auth
@require_role(['admin'])
def criar_usuario():
    """Cria novo usuário (apenas admin)"""
    try:
        data = request.json
        usuario = auth_system.criar_usuario(
            username=data['username'],
            email=data['email'],
            senha=data['senha'],
            nome_completo=data['nome_completo'],
            nivel_acesso=data.get('nivel_acesso', 'operador'),
            criado_por=request.usuario['usuario_id']
        )
        return jsonify(usuario), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário: {str(e)}'}), 500

@app.route('/api/auth/alterar-senha', methods=['POST'])
@require_auth
def alterar_senha():
    """Altera senha do usuário logado"""
    try:
        data = request.json
        auth_system.alterar_senha(
            usuario_id=request.usuario['usuario_id'],
            senha_antiga=data['senha_antiga'],
            senha_nova=data['senha_nova']
        )
        return jsonify({'message': 'Senha alterada com sucesso'})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro ao alterar senha: {str(e)}'}), 500

@app.route('/api/auth/logs', methods=['GET'])
@require_auth
@require_role(['admin'])
def obter_logs():
    """Obtém logs de acesso (apenas admin)"""
    try:
        limite = request.args.get('limite', 100, type=int)
        logs = auth_system.obter_logs(limite=limite)
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': f'Erro ao obter logs: {str(e)}'}), 500

# ==================== ENDPOINTS DE DASHBOARD ====================

@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    """Retorna estatísticas para o dashboard principal"""
    try:
        # Obter estatísticas de cada módulo
        financial_stats = financial.obter_estatisticas()
        payment_stats = payments.obter_estatisticas()
        logistics_stats = logistics.obter_estatisticas()
        
        stats = {
            'licitacoes_ativas': 24,  # TODO: Implementar contagem real
            'propostas_enviadas': quotations.obter_estatisticas().get('total_solicitacoes', 0),
            'contratos_ativos': 8,  # TODO: Implementar contagem real
            'entregas_pendentes': len(logistics.listar_entregas_pendentes()),
            'valor_total_contratos': 2850000,  # TODO: Calcular real
            'economia_gerada': 425000,  # TODO: Calcular real
            'taxa_sucesso': 62.5,  # TODO: Calcular real
            'fornecedores_ativos': 45,  # TODO: Contar real
            'saldo_atual': financial_stats.get('saldo_atual', 0),
            'total_a_receber': financial_stats.get('total_a_receber', 0),
            'total_a_pagar': financial_stats.get('total_a_pagar', 0),
            'parcelas_pendentes': payment_stats.get('parcelas_pendentes', 0)
        }
        
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/activity', methods=['GET'])
def get_recent_activity():
    """Retorna atividade recente do sistema"""
    try:
        # TODO: Implementar log de atividades real
        activity = [
            {
                'id': 1,
                'tipo': 'licitacao',
                'descricao': 'Nova licitação detectada - PE-2024-001',
                'tempo': '5 min atrás',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return jsonify(activity), 200
    except Exception as e:
        logger.error(f"Erro ao obter atividades: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE LICITAÇÕES ====================

@app.route('/api/licitacoes', methods=['GET'])
def get_licitacoes():
    """Lista licitações"""
    try:
        # Parâmetros de filtro
        status = request.args.get('status')
        estado = request.args.get('estado')
        limit = int(request.args.get('limit', 50))
        
        # TODO: Implementar busca no banco
        licitacoes = []
        
        return jsonify({'licitacoes': licitacoes, 'total': len(licitacoes)}), 200
    except Exception as e:
        logger.error(f"Erro ao listar licitações: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/licitacoes/capturar', methods=['POST'])
def capturar_licitacoes():
    """Captura licitações do Effecti"""
    try:
        data = request.json
        estados = data.get('estados', [])
        palavras_chave = data.get('palavras_chave', [])
        
        # Capturar licitações
        licitacoes = effecti.buscar_licitacoes(estados, palavras_chave)
        
        return jsonify({
            'sucesso': True,
            'total_capturadas': len(licitacoes),
            'licitacoes': licitacoes
        }), 200
    except Exception as e:
        logger.error(f"Erro ao capturar licitações: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE COTAÇÕES ====================

@app.route('/api/cotacoes', methods=['GET'])
def get_cotacoes():
    """Lista solicitações de cotação"""
    try:
        # TODO: Implementar listagem real
        cotacoes = []
        return jsonify({'cotacoes': cotacoes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cotacoes', methods=['POST'])
def criar_cotacao():
    """Cria nova solicitação de cotação"""
    try:
        data = request.json
        
        solicitacao_id = quotations.criar_solicitacao_cotacao(
            numero_edital=data['numero_edital'],
            descricao=data['descricao'],
            itens=data['itens'],
            prazo_resposta=data.get('prazo_resposta', '2024-12-31')
        )
        
        return jsonify({
            'sucesso': True,
            'solicitacao_id': solicitacao_id
        }), 201
    except Exception as e:
        logger.error(f"Erro ao criar cotação: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cotacoes/<int:solicitacao_id>/comparar', methods=['GET'])
def comparar_propostas(solicitacao_id):
    """Compara propostas de uma solicitação"""
    try:
        comparacao = quotations.comparar_propostas(solicitacao_id)
        return jsonify(comparacao), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE CONTRATOS ====================

@app.route('/api/contratos', methods=['POST'])
def gerar_contrato():
    """Gera novo contrato"""
    try:
        data = request.json
        tipo = data.get('tipo', 'fornecimento')
        
        pdf_path = contracts.gerar_contrato(tipo, data)
        
        return jsonify({
            'sucesso': True,
            'pdf_path': pdf_path
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS FINANCEIROS ====================

@app.route('/api/financeiro/receitas', methods=['POST'])
def registrar_receita():
    """Registra nova receita"""
    try:
        data = request.json
        receita_id = financial.registrar_receita(data)
        
        return jsonify({
            'sucesso': True,
            'receita_id': receita_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/financeiro/despesas', methods=['POST'])
def registrar_despesa():
    """Registra nova despesa"""
    try:
        data = request.json
        despesa_id = financial.registrar_despesa(data)
        
        return jsonify({
            'sucesso': True,
            'despesa_id': despesa_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/financeiro/saldo', methods=['GET'])
def get_saldo():
    """Retorna saldo atual"""
    try:
        saldo = financial.obter_saldo_atual()
        return jsonify({'saldo': saldo}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/financeiro/relatorio', methods=['GET'])
def get_relatorio_financeiro():
    """Gera relatório financeiro"""
    try:
        inicio = request.args.get('inicio', '2024-12-01')
        fim = request.args.get('fim', '2024-12-31')
        
        relatorio = financial.relatorio_periodo(inicio, fim)
        return jsonify(relatorio), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE PAGAMENTOS ====================

@app.route('/api/pagamentos', methods=['POST'])
def criar_pagamento():
    """Cria novo pagamento"""
    try:
        data = request.json
        pagamento_id = payments.criar_pagamento(data)
        
        return jsonify({
            'sucesso': True,
            'pagamento_id': pagamento_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pagamentos/parcelas/vencendo', methods=['GET'])
def get_parcelas_vencendo():
    """Lista parcelas vencendo"""
    try:
        dias = int(request.args.get('dias', 7))
        parcelas = payments.listar_parcelas_vencendo(dias)
        
        return jsonify({'parcelas': parcelas}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/pagamentos/parcelas/<int:parcela_id>/pagar', methods=['POST'])
def pagar_parcela(parcela_id):
    """Registra pagamento de parcela"""
    try:
        data = request.json
        sucesso = payments.registrar_pagamento_parcela(parcela_id, data)
        
        return jsonify({'sucesso': sucesso}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE LOGÍSTICA ====================

@app.route('/api/logistica/pedidos', methods=['POST'])
def criar_pedido():
    """Cria novo pedido de entrega"""
    try:
        data = request.json
        pedido_id = logistics.criar_pedido(data)
        
        return jsonify({
            'sucesso': True,
            'pedido_id': pedido_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logistica/pedidos/<int:pedido_id>/agendar', methods=['POST'])
def agendar_entrega(pedido_id):
    """Agenda entrega"""
    try:
        data = request.json
        agendamento_id = logistics.agendar_entrega(pedido_id, data)
        
        return jsonify({
            'sucesso': True,
            'agendamento_id': agendamento_id
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logistica/pedidos/<int:pedido_id>/rastreamento', methods=['GET'])
def get_rastreamento(pedido_id):
    """Retorna rastreamento do pedido"""
    try:
        rastreamento = logistics.obter_rastreamento(pedido_id)
        return jsonify({'rastreamento': rastreamento}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/logistica/entregas/pendentes', methods=['GET'])
def get_entregas_pendentes():
    """Lista entregas pendentes"""
    try:
        pendentes = logistics.listar_entregas_pendentes()
        return jsonify({'entregas': pendentes}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE NOTIFICAÇÕES ====================

@app.route('/api/notificacoes/email', methods=['POST'])
def enviar_email():
    """Envia email"""
    try:
        data = request.json
        resultado = notifications.enviar_email(
            data['destinatario'],
            data['assunto'],
            data['corpo']
        )
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/notificacoes/whatsapp', methods=['POST'])
def enviar_whatsapp():
    """Envia mensagem WhatsApp"""
    try:
        data = request.json
        resultado = whatsapp.enviar_mensagem(
            data['telefone'],
            data['tipo_template'],
            data['dados']
        )
        
        return jsonify(resultado), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE RELATÓRIOS ====================

@app.route('/api/relatorios/licitacoes', methods=['GET'])
def relatorio_licitacoes():
    """Gera relatório de licitações"""
    try:
        inicio = request.args.get('inicio', '2024-12-01')
        fim = request.args.get('fim', '2024-12-31')
        
        relatorio = reports.relatorio_licitacoes(inicio, fim)
        return jsonify(relatorio), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/relatorios/executivo', methods=['GET'])
def relatorio_executivo():
    """Gera relatório executivo"""
    try:
        inicio = request.args.get('inicio', '2024-12-01')
        fim = request.args.get('fim', '2024-12-31')
        
        relatorio = reports.relatorio_executivo(inicio, fim)
        return jsonify(relatorio), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/relatorios/exportar/pdf', methods=['POST'])
def exportar_pdf():
    """Exporta relatório em PDF"""
    try:
        data = request.json
        pdf_path = reports.gerar_pdf_relatorio(data['relatorio'], data['titulo'])
        
        return jsonify({
            'sucesso': True,
            'pdf_path': pdf_path
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINTS DE OCR ====================

@app.route('/api/ocr/analisar', methods=['POST'])
def analisar_documento():
    """Analisa documento PDF com OCR"""
    try:
        data = request.json
        pdf_path = data['pdf_path']
        
        analise = ocr.analisar_edital(pdf_path)
        return jsonify(analise), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== ENDPOINT DE HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check da API"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'modules': {
            'effecti': True,
            'padronizacao': True,
            'notifications': True,
            'sheets': True,
            'ocr': True,
            'quotations': True,
            'email': True,
            'whatsapp': True,
            'proposals': True,
            'contracts': True,
            'financial': True,
            'payments': True,
            'logistics': True,
            'reports': True
        }
    }), 200


if __name__ == '__main__':
    logger.info("🚀 Iniciando API Hospshop...")
    logger.info("📡 Servidor rodando em http://localhost:5000")
    logger.info("📚 Documentação: http://localhost:5000/api/health")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
