"""
Sistema de Templates de Email Automatizados
Templates HTML profissionais para diferentes eventos do sistema

Desenvolvido em 01/12/2025
"""

import logging
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailTemplateSystem:
    """
    Sistema de templates de email com variáveis dinâmicas
    """
    
    def __init__(self):
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carrega todos os templates disponíveis"""
        self.templates = {
            'nova_licitacao': self._template_nova_licitacao(),
            'prazo_proximo': self._template_prazo_proximo(),
            'solicitacao_cotacao': self._template_solicitacao_cotacao(),
            'proposta_recebida': self._template_proposta_recebida(),
            'proposta_vencedora': self._template_proposta_vencedora(),
            'proposta_nao_selecionada': self._template_proposta_nao_selecionada(),
            'contrato_gerado': self._template_contrato_gerado(),
            'pagamento_vencimento': self._template_pagamento_vencimento(),
            'entrega_agendada': self._template_entrega_agendada(),
            'irregularidade_detectada': self._template_irregularidade_detectada(),
        }
        logger.info(f"✅ {len(self.templates)} templates carregados")
    
    def _base_template(self, titulo: str, conteudo: str, cor_header: str = '#2563eb') -> str:
        """Template base HTML para todos os emails"""
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .header {{
            background: {cor_header};
            color: white;
            padding: 30px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .content {{
            padding: 30px 20px;
        }}
        .field {{
            margin: 15px 0;
            padding: 12px;
            background: #f9fafb;
            border-left: 3px solid {cor_header};
            border-radius: 4px;
        }}
        .field-label {{
            font-weight: 600;
            color: #374151;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .field-value {{
            color: #1f2937;
            margin-top: 4px;
            font-size: 15px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background: {cor_header};
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            margin: 20px 0;
        }}
        .button:hover {{
            opacity: 0.9;
        }}
        .footer {{
            background: #f9fafb;
            padding: 20px;
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            border-top: 1px solid #e5e7eb;
        }}
        .alert {{
            background: #fef2f2;
            border-left: 3px solid #dc2626;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .success {{
            background: #f0fdf4;
            border-left: 3px solid #16a34a;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 Hospshop</h1>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">{titulo}</p>
        </div>
        <div class="content">
            {conteudo}
        </div>
        <div class="footer">
            <p><strong>Sistema Hospshop</strong> - Gestão de Licitações</p>
            <p>Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p style="margin-top: 10px; font-size: 11px;">
                Este é um email automático. Por favor, não responda.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    def _template_nova_licitacao(self) -> str:
        """Template para notificação de nova licitação"""
        conteudo = """
            <h2 style="color: #1f2937; margin-top: 0;">Nova Licitação Detectada</h2>
            <p>Uma nova licitação foi capturada automaticamente pelo sistema e está aguardando sua análise.</p>
            
            <div class="field">
                <div class="field-label">Número do Edital</div>
                <div class="field-value">{{numero_edital}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Órgão</div>
                <div class="field-value">{{orgao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Objeto</div>
                <div class="field-value">{{objeto}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor Estimado</div>
                <div class="field-value">R$ {{valor_estimado}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Data de Abertura</div>
                <div class="field-value">{{data_abertura}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Modalidade</div>
                <div class="field-value">{{modalidade}}</div>
            </div>
            
            <a href="{{link_sistema}}" class="button">Acessar Sistema</a>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                💡 <strong>Dica:</strong> Acesse o sistema para iniciar o processo de cotação e análise de viabilidade.
            </p>
        """
        return self._base_template("Nova Licitação Detectada", conteudo)
    
    def _template_prazo_proximo(self) -> str:
        """Template para alerta de prazo próximo"""
        conteudo = """
            <div class="alert">
                <h2 style="color: #dc2626; margin-top: 0;">⚠️ Alerta de Prazo</h2>
                <p style="font-size: 16px; font-weight: 600;">
                    Faltam apenas <strong>{{dias_restantes}} dias</strong> para o prazo!
                </p>
            </div>
            
            <p>A licitação abaixo está próxima do prazo de abertura. Verifique se todas as providências foram tomadas.</p>
            
            <div class="field">
                <div class="field-label">Número do Edital</div>
                <div class="field-value">{{numero_edital}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Órgão</div>
                <div class="field-value">{{orgao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Data de Abertura</div>
                <div class="field-value">{{data_abertura}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor</div>
                <div class="field-value">R$ {{valor_estimado}}</div>
            </div>
            
            <a href="{{link_sistema}}" class="button">Verificar Status</a>
            
            <p style="color: #dc2626; font-weight: 600; margin-top: 20px;">
                ⏰ Ação necessária: Certifique-se de que a proposta foi enviada e todos os documentos estão em ordem.
            </p>
        """
        return self._base_template("Alerta de Prazo Próximo", conteudo, '#dc2626')
    
    def _template_solicitacao_cotacao(self) -> str:
        """Template para solicitação de cotação a fornecedor"""
        conteudo = """
            <h2 style="color: #1f2937; margin-top: 0;">Solicitação de Cotação</h2>
            <p>Prezado(a) Fornecedor,</p>
            <p>Solicitamos cotação para os itens abaixo, referente ao processo licitatório:</p>
            
            <div class="field">
                <div class="field-label">Número da Solicitação</div>
                <div class="field-value">{{numero_solicitacao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Edital Relacionado</div>
                <div class="field-value">{{numero_edital}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Descrição</div>
                <div class="field-value">{{descricao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Prazo para Resposta</div>
                <div class="field-value">{{prazo_resposta}}</div>
            </div>
            
            <h3 style="color: #374151; margin-top: 25px;">Itens Solicitados:</h3>
            {{itens_lista}}
            
            <a href="{{link_resposta}}" class="button">Enviar Proposta</a>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                Por favor, envie sua proposta dentro do prazo estabelecido. Propostas enviadas após o prazo não serão consideradas.
            </p>
        """
        return self._base_template("Solicitação de Cotação", conteudo, '#059669')
    
    def _template_proposta_recebida(self) -> str:
        """Template para confirmação de proposta recebida"""
        conteudo = """
            <div class="success">
                <h2 style="color: #16a34a; margin-top: 0;">✅ Proposta Recebida</h2>
                <p>Sua proposta foi recebida com sucesso e está em análise.</p>
            </div>
            
            <div class="field">
                <div class="field-label">Número da Proposta</div>
                <div class="field-value">{{numero_proposta}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Solicitação</div>
                <div class="field-value">{{numero_solicitacao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor Total</div>
                <div class="field-value">R$ {{valor_total}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Data de Recebimento</div>
                <div class="field-value">{{data_recebimento}}</div>
            </div>
            
            <p style="margin-top: 20px;">
                Sua proposta será analisada junto com as demais recebidas. O resultado será comunicado em breve.
            </p>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                📧 Você receberá um email assim que a análise for concluída.
            </p>
        """
        return self._base_template("Proposta Recebida", conteudo, '#059669')
    
    def _template_proposta_vencedora(self) -> str:
        """Template para notificação de proposta vencedora"""
        conteudo = """
            <div class="success">
                <h2 style="color: #16a34a; margin-top: 0;">🎉 Parabéns! Sua Proposta Foi Selecionada</h2>
                <p style="font-size: 16px;">Sua proposta foi selecionada como vencedora!</p>
            </div>
            
            <div class="field">
                <div class="field-label">Número da Proposta</div>
                <div class="field-value">{{numero_proposta}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Solicitação</div>
                <div class="field-value">{{numero_solicitacao}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor Contratado</div>
                <div class="field-value">R$ {{valor_total}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Critério de Seleção</div>
                <div class="field-value">{{criterio}}</div>
            </div>
            
            <h3 style="color: #374151; margin-top: 25px;">Próximos Passos:</h3>
            <ol style="color: #4b5563; line-height: 1.8;">
                <li>Aguarde o contato para assinatura do contrato</li>
                <li>Prepare a documentação necessária</li>
                <li>Organize a logística de entrega</li>
            </ol>
            
            <a href="{{link_contrato}}" class="button">Visualizar Detalhes</a>
            
            <p style="color: #059669; font-weight: 600; margin-top: 20px;">
                ✨ Obrigado pela parceria!
            </p>
        """
        return self._base_template("Proposta Vencedora", conteudo, '#059669')
    
    def _template_proposta_nao_selecionada(self) -> str:
        """Template para notificação de proposta não selecionada"""
        conteudo = """
            <h2 style="color: #1f2937; margin-top: 0;">Resultado da Análise de Propostas</h2>
            <p>Agradecemos sua participação no processo de cotação.</p>
            
            <div class="field">
                <div class="field-label">Número da Proposta</div>
                <div class="field-value">{{numero_proposta}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Solicitação</div>
                <div class="field-value">{{numero_solicitacao}}</div>
            </div>
            
            <p style="margin-top: 20px;">
                Informamos que, após análise criteriosa de todas as propostas recebidas, 
                sua proposta não foi selecionada neste processo.
            </p>
            
            <div class="field">
                <div class="field-label">Motivo</div>
                <div class="field-value">{{motivo}}</div>
            </div>
            
            <p style="margin-top: 20px;">
                Valorizamos sua participação e esperamos contar com você em futuras oportunidades.
            </p>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                💼 Continue cadastrado em nosso sistema para receber novas solicitações de cotação.
            </p>
        """
        return self._base_template("Resultado da Cotação", conteudo, '#6b7280')
    
    def _template_contrato_gerado(self) -> str:
        """Template para notificação de contrato gerado"""
        conteudo = """
            <h2 style="color: #1f2937; margin-top: 0;">Contrato Gerado</h2>
            <p>O contrato referente à licitação foi gerado e está disponível para assinatura.</p>
            
            <div class="field">
                <div class="field-label">Número do Contrato</div>
                <div class="field-value">{{numero_contrato}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Edital</div>
                <div class="field-value">{{numero_edital}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Fornecedor</div>
                <div class="field-value">{{fornecedor}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor do Contrato</div>
                <div class="field-value">R$ {{valor_contrato}}</div>
            </div>
            
            <a href="{{link_contrato}}" class="button">Visualizar Contrato</a>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                📄 O contrato está disponível em formato PDF para download e assinatura digital.
            </p>
        """
        return self._base_template("Contrato Gerado", conteudo, '#7c3aed')
    
    def _template_pagamento_vencimento(self) -> str:
        """Template para alerta de pagamento próximo ao vencimento"""
        conteudo = """
            <div class="alert">
                <h2 style="color: #dc2626; margin-top: 0;">💳 Pagamento Próximo ao Vencimento</h2>
                <p>Um pagamento está próximo do vencimento e requer sua atenção.</p>
            </div>
            
            <div class="field">
                <div class="field-label">Número do Pagamento</div>
                <div class="field-value">{{numero_pagamento}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Fornecedor</div>
                <div class="field-value">{{fornecedor}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Valor</div>
                <div class="field-value">R$ {{valor}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Data de Vencimento</div>
                <div class="field-value">{{data_vencimento}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Dias Restantes</div>
                <div class="field-value">{{dias_restantes}} dias</div>
            </div>
            
            <a href="{{link_pagamento}}" class="button">Processar Pagamento</a>
            
            <p style="color: #dc2626; font-weight: 600; margin-top: 20px;">
                ⚠️ Evite multas e juros: Processe o pagamento antes do vencimento.
            </p>
        """
        return self._base_template("Alerta de Pagamento", conteudo, '#dc2626')
    
    def _template_entrega_agendada(self) -> str:
        """Template para confirmação de entrega agendada"""
        conteudo = """
            <h2 style="color: #1f2937; margin-top: 0;">📦 Entrega Agendada</h2>
            <p>A entrega dos produtos foi agendada com sucesso.</p>
            
            <div class="field">
                <div class="field-label">Número do Pedido</div>
                <div class="field-value">{{numero_pedido}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Fornecedor</div>
                <div class="field-value">{{fornecedor}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Data da Entrega</div>
                <div class="field-value">{{data_entrega}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Horário</div>
                <div class="field-value">{{horario}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Local de Entrega</div>
                <div class="field-value">{{local_entrega}}</div>
            </div>
            
            <p style="margin-top: 20px;">
                Por favor, certifique-se de que haverá alguém disponível para receber os produtos no horário agendado.
            </p>
            
            <p style="color: #6b7280; font-size: 13px; margin-top: 20px;">
                📞 Em caso de dúvidas ou necessidade de reagendamento, entre em contato com o fornecedor.
            </p>
        """
        return self._base_template("Entrega Agendada", conteudo, '#0891b2')
    
    def _template_irregularidade_detectada(self) -> str:
        """Template para alerta de irregularidade detectada"""
        conteudo = """
            <div class="alert">
                <h2 style="color: #dc2626; margin-top: 0;">🚨 Irregularidade Detectada</h2>
                <p>O sistema detectou uma possível irregularidade que requer análise.</p>
            </div>
            
            <div class="field">
                <div class="field-label">Tipo de Irregularidade</div>
                <div class="field-value">{{tipo}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Edital Relacionado</div>
                <div class="field-value">{{numero_edital}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Gravidade</div>
                <div class="field-value">{{gravidade}}</div>
            </div>
            
            <div class="field">
                <div class="field-label">Descrição</div>
                <div class="field-value">{{descricao}}</div>
            </div>
            
            <a href="{{link_analise}}" class="button">Analisar Irregularidade</a>
            
            <p style="color: #dc2626; font-weight: 600; margin-top: 20px;">
                ⚖️ Ação recomendada: Verifique se é necessário gerar recurso administrativo.
            </p>
        """
        return self._base_template("Irregularidade Detectada", conteudo, '#dc2626')
    
    def gerar_email(self, tipo: str, dados: Dict) -> Dict:
        """
        Gera email a partir de template e dados
        
        Args:
            tipo: Tipo do template
            dados: Dicionário com dados para substituição
            
        Returns:
            Dicionário com assunto e corpo HTML
        """
        if tipo not in self.templates:
            logger.error(f"❌ Template '{tipo}' não encontrado")
            return None
        
        template = self.templates[tipo]
        
        # Substituir variáveis
        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            template = template.replace(placeholder, str(valor))
        
        # Definir assunto baseado no tipo
        assuntos = {
            'nova_licitacao': f"🔔 Nova Licitação: {dados.get('numero_edital', 'N/A')}",
            'prazo_proximo': f"⚠️ URGENTE: Prazo em {dados.get('dias_restantes', 'X')} dias",
            'solicitacao_cotacao': f"Solicitação de Cotação: {dados.get('numero_solicitacao', 'N/A')}",
            'proposta_recebida': f"✅ Proposta Recebida: {dados.get('numero_proposta', 'N/A')}",
            'proposta_vencedora': f"🎉 Proposta Vencedora: {dados.get('numero_proposta', 'N/A')}",
            'proposta_nao_selecionada': f"Resultado da Cotação: {dados.get('numero_solicitacao', 'N/A')}",
            'contrato_gerado': f"📄 Contrato Gerado: {dados.get('numero_contrato', 'N/A')}",
            'pagamento_vencimento': f"💳 Pagamento Vence em {dados.get('dias_restantes', 'X')} dias",
            'entrega_agendada': f"📦 Entrega Agendada: {dados.get('data_entrega', 'N/A')}",
            'irregularidade_detectada': f"🚨 Irregularidade: {dados.get('tipo', 'N/A')}",
        }
        
        resultado = {
            'assunto': assuntos.get(tipo, 'Notificação do Sistema Hospshop'),
            'corpo_html': template,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Email '{tipo}' gerado")
        return resultado
    
    def listar_templates(self) -> list:
        """Lista todos os templates disponíveis"""
        return list(self.templates.keys())


def testar_templates():
    """Função de teste do sistema de templates"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE TEMPLATES DE EMAIL")
    print("="*60 + "\n")
    
    sistema = EmailTemplateSystem()
    
    # Teste 1: Listar templates
    print("1️⃣ Templates Disponíveis:")
    for template in sistema.listar_templates():
        print(f"   • {template}")
    print()
    
    # Teste 2: Gerar email de nova licitação
    print("2️⃣ Gerando email de nova licitação...")
    dados = {
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal de Testes',
        'objeto': 'Aquisição de equipamentos hospitalares',
        'valor_estimado': '250.000,00',
        'data_abertura': '20/12/2024',
        'modalidade': 'Pregão Eletrônico',
        'link_sistema': 'https://hospshop.com/licitacoes/PE-2024-TEST-001'
    }
    
    email = sistema.gerar_email('nova_licitacao', dados)
    print(f"   Assunto: {email['assunto']}")
    print(f"   Tamanho HTML: {len(email['corpo_html'])} caracteres")
    print(f"   ✅ Email gerado com sucesso\n")
    
    # Teste 3: Gerar email de prazo próximo
    print("3️⃣ Gerando email de prazo próximo...")
    dados_prazo = {
        'dias_restantes': '3',
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal',
        'data_abertura': '15/12/2024',
        'valor_estimado': '250.000,00',
        'link_sistema': 'https://hospshop.com/licitacoes/PE-2024-TEST-001'
    }
    
    email_prazo = sistema.gerar_email('prazo_proximo', dados_prazo)
    print(f"   Assunto: {email_prazo['assunto']}")
    print(f"   ✅ Email de alerta gerado\n")
    
    # Teste 4: Gerar email de proposta vencedora
    print("4️⃣ Gerando email de proposta vencedora...")
    dados_vencedora = {
        'numero_proposta': 'PROP-001',
        'numero_solicitacao': 'SOL-001',
        'valor_total': '73.500,00',
        'criterio': 'Menor Preço',
        'link_contrato': 'https://hospshop.com/contratos/CONT-001'
    }
    
    email_vencedora = sistema.gerar_email('proposta_vencedora', dados_vencedora)
    print(f"   Assunto: {email_vencedora['assunto']}")
    print(f"   ✅ Email de vitória gerado\n")
    
    # Salvar exemplo em arquivo
    print("5️⃣ Salvando exemplo de email...")
    with open('/tmp/email_exemplo.html', 'w', encoding='utf-8') as f:
        f.write(email['corpo_html'])
    print(f"   ✅ Salvo em: /tmp/email_exemplo.html\n")
    
    print("="*60)
    print("✅ SISTEMA DE TEMPLATES FUNCIONANDO")
    print("="*60 + "\n")
    
    print(f"📊 Estatísticas:")
    print(f"   • Total de Templates: {len(sistema.listar_templates())}")
    print(f"   • Emails Gerados: 3")
    print(f"   • Tamanho Médio: ~{(len(email['corpo_html']) + len(email_prazo['corpo_html']) + len(email_vencedora['corpo_html'])) // 3} caracteres\n")


if __name__ == '__main__':
    testar_templates()
