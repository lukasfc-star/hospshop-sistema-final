"""
Sistema de Mensagens Automatizadas WhatsApp
Integração com WhatsApp Business API para notificações

Desenvolvido em 01/12/2025
"""

import os
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppAutomation:
    """
    Sistema de automação de mensagens WhatsApp
    Integração com WhatsApp Business API
    """
    
    def __init__(self):
        self.api_key = os.getenv('WHATSAPP_API_KEY', '')
        self.api_url = os.getenv('WHATSAPP_API_URL', 'https://api.whatsapp.com/send')
        self.phone_id = os.getenv('WHATSAPP_PHONE_ID', '')
        self.templates = {}
        self._load_templates()
        self.modo_simulacao = not self.api_key
        
        if self.modo_simulacao:
            logger.warning("⚠️ WhatsApp API não configurada - Modo simulação ativado")
        else:
            logger.info("✅ WhatsApp API inicializada")
    
    def _load_templates(self):
        """Carrega templates de mensagens WhatsApp"""
        self.templates = {
            'nova_licitacao': self._template_nova_licitacao(),
            'prazo_proximo': self._template_prazo_proximo(),
            'solicitacao_cotacao': self._template_solicitacao_cotacao(),
            'proposta_recebida': self._template_proposta_recebida(),
            'proposta_vencedora': self._template_proposta_vencedora(),
            'proposta_nao_selecionada': self._template_proposta_nao_selecionada(),
            'pagamento_vencimento': self._template_pagamento_vencimento(),
            'entrega_agendada': self._template_entrega_agendada(),
            'confirmacao_entrega': self._template_confirmacao_entrega(),
            'lembrete_documentos': self._template_lembrete_documentos(),
        }
        logger.info(f"✅ {len(self.templates)} templates WhatsApp carregados")
    
    def _template_nova_licitacao(self) -> str:
        """Template para nova licitação"""
        return """🔔 *Nova Licitação Detectada*

📋 *Edital:* {{numero_edital}}
🏛️ *Órgão:* {{orgao}}
💰 *Valor:* R$ {{valor_estimado}}
📅 *Abertura:* {{data_abertura}}

🔗 Acesse: {{link_sistema}}

_Sistema Hospshop - Gestão de Licitações_"""
    
    def _template_prazo_proximo(self) -> str:
        """Template para alerta de prazo"""
        return """⚠️ *ALERTA DE PRAZO*

⏰ Faltam apenas *{{dias_restantes}} dias* para o prazo!

📋 *Edital:* {{numero_edital}}
🏛️ *Órgão:* {{orgao}}
📅 *Abertura:* {{data_abertura}}

🚨 *Ação necessária:* Verifique se a proposta foi enviada!

🔗 {{link_sistema}}

_Sistema Hospshop_"""
    
    def _template_solicitacao_cotacao(self) -> str:
        """Template para solicitação de cotação"""
        return """📨 *Solicitação de Cotação*

Prezado(a) Fornecedor,

Solicitamos cotação para:

📋 *Solicitação:* {{numero_solicitacao}}
📄 *Edital:* {{numero_edital}}
📝 *Descrição:* {{descricao}}
⏰ *Prazo:* {{prazo_resposta}}

🔗 Enviar proposta: {{link_resposta}}

_Sistema Hospshop_"""
    
    def _template_proposta_recebida(self) -> str:
        """Template para confirmação de proposta"""
        return """✅ *Proposta Recebida*

Sua proposta foi recebida com sucesso!

📋 *Proposta:* {{numero_proposta}}
💰 *Valor:* R$ {{valor_total}}
📅 *Recebida em:* {{data_recebimento}}

Aguarde a análise. Você será notificado do resultado em breve.

_Sistema Hospshop_"""
    
    def _template_proposta_vencedora(self) -> str:
        """Template para proposta vencedora"""
        return """🎉 *PARABÉNS! Proposta Vencedora*

Sua proposta foi selecionada! 🏆

📋 *Proposta:* {{numero_proposta}}
💰 *Valor:* R$ {{valor_total}}
✅ *Critério:* {{criterio}}

*Próximos passos:*
1️⃣ Aguarde contato para contrato
2️⃣ Prepare documentação
3️⃣ Organize logística

🔗 {{link_contrato}}

_Sistema Hospshop_"""
    
    def _template_proposta_nao_selecionada(self) -> str:
        """Template para proposta não selecionada"""
        return """📋 *Resultado da Cotação*

Agradecemos sua participação!

Infelizmente sua proposta não foi selecionada neste processo.

📋 *Proposta:* {{numero_proposta}}
📝 *Motivo:* {{motivo}}

Valorizamos sua parceria e esperamos contar com você em futuras oportunidades.

_Sistema Hospshop_"""
    
    def _template_pagamento_vencimento(self) -> str:
        """Template para alerta de pagamento"""
        return """💳 *Alerta de Pagamento*

⚠️ Pagamento próximo ao vencimento!

📋 *Pagamento:* {{numero_pagamento}}
👤 *Fornecedor:* {{fornecedor}}
💰 *Valor:* R$ {{valor}}
📅 *Vencimento:* {{data_vencimento}}
⏰ *Faltam:* {{dias_restantes}} dias

🔗 Processar: {{link_pagamento}}

_Sistema Hospshop_"""
    
    def _template_entrega_agendada(self) -> str:
        """Template para confirmação de entrega"""
        return """📦 *Entrega Agendada*

Confirmamos o agendamento da entrega:

📋 *Pedido:* {{numero_pedido}}
👤 *Fornecedor:* {{fornecedor}}
📅 *Data:* {{data_entrega}}
🕐 *Horário:* {{horario}}
📍 *Local:* {{local_entrega}}

Por favor, esteja disponível para receber.

_Sistema Hospshop_"""
    
    def _template_confirmacao_entrega(self) -> str:
        """Template para confirmação de entrega realizada"""
        return """✅ *Entrega Confirmada*

A entrega foi confirmada com sucesso!

📋 *Pedido:* {{numero_pedido}}
📅 *Data:* {{data_entrega}}
👤 *Recebido por:* {{recebedor}}

{{observacoes}}

Obrigado!

_Sistema Hospshop_"""
    
    def _template_lembrete_documentos(self) -> str:
        """Template para lembrete de documentos"""
        return """📄 *Lembrete de Documentos*

Documentos pendentes para:

📋 *Edital:* {{numero_edital}}

*Documentos necessários:*
{{lista_documentos}}

⏰ *Prazo:* {{prazo}}

🔗 Enviar: {{link_upload}}

_Sistema Hospshop_"""
    
    def enviar_mensagem(self, 
                       telefone: str, 
                       tipo_template: str, 
                       dados: Dict) -> Dict:
        """
        Envia mensagem WhatsApp
        
        Args:
            telefone: Número do telefone (formato: +5511999999999)
            tipo_template: Tipo do template
            dados: Dados para substituição no template
            
        Returns:
            Dicionário com resultado do envio
        """
        if tipo_template not in self.templates:
            logger.error(f"❌ Template '{tipo_template}' não encontrado")
            return {'sucesso': False, 'erro': 'Template não encontrado'}
        
        # Obter template
        template = self.templates[tipo_template]
        
        # Substituir variáveis
        mensagem = template
        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            mensagem = mensagem.replace(placeholder, str(valor))
        
        # Limpar telefone
        telefone_limpo = ''.join(filter(str.isdigit, telefone))
        if not telefone_limpo.startswith('55'):
            telefone_limpo = '55' + telefone_limpo
        
        if self.modo_simulacao:
            return self._simular_envio(telefone_limpo, mensagem, tipo_template)
        
        # Enviar via API
        return self._enviar_api(telefone_limpo, mensagem, tipo_template)
    
    def _enviar_api(self, telefone: str, mensagem: str, tipo: str) -> Dict:
        """Envia mensagem via WhatsApp Business API"""
        try:
            import requests
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'messaging_product': 'whatsapp',
                'to': telefone,
                'type': 'text',
                'text': {
                    'body': mensagem
                }
            }
            
            response = requests.post(
                f"{self.api_url}/{self.phone_id}/messages",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Mensagem enviada para {telefone}")
                return {
                    'sucesso': True,
                    'telefone': telefone,
                    'tipo': tipo,
                    'timestamp': datetime.now().isoformat(),
                    'message_id': response.json().get('messages', [{}])[0].get('id')
                }
            else:
                logger.error(f"❌ Erro ao enviar: {response.status_code}")
                return {
                    'sucesso': False,
                    'erro': f"HTTP {response.status_code}",
                    'detalhes': response.text
                }
        
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem: {e}")
            return {'sucesso': False, 'erro': str(e)}
    
    def _simular_envio(self, telefone: str, mensagem: str, tipo: str) -> Dict:
        """Simula envio de mensagem"""
        logger.info(f"📱 Simulando envio para {telefone}")
        logger.info(f"📝 Tipo: {tipo}")
        logger.info(f"💬 Mensagem ({len(mensagem)} caracteres)")
        
        return {
            'sucesso': True,
            'telefone': telefone,
            'tipo': tipo,
            'mensagem': mensagem,
            'timestamp': datetime.now().isoformat(),
            'simulado': True
        }
    
    def enviar_em_lote(self, 
                      destinatarios: List[Dict]) -> Dict:
        """
        Envia mensagens em lote
        
        Args:
            destinatarios: Lista de dicionários com telefone, tipo e dados
            
        Returns:
            Estatísticas do envio em lote
        """
        logger.info(f"📨 Enviando {len(destinatarios)} mensagens em lote...")
        
        resultados = {
            'total': len(destinatarios),
            'sucesso': 0,
            'falha': 0,
            'detalhes': []
        }
        
        for dest in destinatarios:
            resultado = self.enviar_mensagem(
                dest['telefone'],
                dest['tipo'],
                dest['dados']
            )
            
            if resultado['sucesso']:
                resultados['sucesso'] += 1
            else:
                resultados['falha'] += 1
            
            resultados['detalhes'].append(resultado)
        
        logger.info(f"✅ Lote concluído: {resultados['sucesso']} enviadas, {resultados['falha']} falhas")
        return resultados
    
    def listar_templates(self) -> List[str]:
        """Lista templates disponíveis"""
        return list(self.templates.keys())
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas de uso"""
        return {
            'templates_disponiveis': len(self.templates),
            'api_configurada': not self.modo_simulacao,
            'modo': 'producao' if not self.modo_simulacao else 'simulacao'
        }


def testar_whatsapp():
    """Função de teste do sistema WhatsApp"""
    print("\n" + "="*60)
    print("🧪 TESTE DE AUTOMAÇÃO WHATSAPP")
    print("="*60 + "\n")
    
    whatsapp = WhatsAppAutomation()
    
    # Teste 1: Listar templates
    print("1️⃣ Templates Disponíveis:")
    for template in whatsapp.listar_templates():
        print(f"   • {template}")
    print()
    
    # Teste 2: Enviar mensagem de nova licitação
    print("2️⃣ Enviando mensagem de nova licitação...")
    dados = {
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal',
        'valor_estimado': '250.000,00',
        'data_abertura': '20/12/2024',
        'link_sistema': 'https://hospshop.com/licitacoes/PE-2024-TEST-001'
    }
    
    resultado = whatsapp.enviar_mensagem(
        '+5511999999999',
        'nova_licitacao',
        dados
    )
    
    print(f"   Telefone: {resultado['telefone']}")
    print(f"   Status: {'✅ Enviada' if resultado['sucesso'] else '❌ Falhou'}")
    print(f"   Tamanho: {len(resultado.get('mensagem', ''))} caracteres\n")
    
    # Teste 3: Enviar alerta de prazo
    print("3️⃣ Enviando alerta de prazo...")
    dados_prazo = {
        'dias_restantes': '3',
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal',
        'data_abertura': '15/12/2024',
        'link_sistema': 'https://hospshop.com'
    }
    
    resultado_prazo = whatsapp.enviar_mensagem(
        '11999999999',
        'prazo_proximo',
        dados_prazo
    )
    print(f"   Status: {'✅ Enviada' if resultado_prazo['sucesso'] else '❌ Falhou'}\n")
    
    # Teste 4: Envio em lote
    print("4️⃣ Testando envio em lote...")
    destinatarios = [
        {
            'telefone': '+5511988888888',
            'tipo': 'proposta_vencedora',
            'dados': {
                'numero_proposta': 'PROP-001',
                'valor_total': '73.500,00',
                'criterio': 'Menor Preço',
                'link_contrato': 'https://hospshop.com/contratos/CONT-001'
            }
        },
        {
            'telefone': '+5511977777777',
            'tipo': 'proposta_recebida',
            'dados': {
                'numero_proposta': 'PROP-002',
                'valor_total': '78.500,00',
                'data_recebimento': '01/12/2024'
            }
        },
        {
            'telefone': '+5511966666666',
            'tipo': 'entrega_agendada',
            'dados': {
                'numero_pedido': 'PED-001',
                'fornecedor': 'Fornecedor A',
                'data_entrega': '15/12/2024',
                'horario': '14:00',
                'local_entrega': 'Hospital Municipal - Recepção'
            }
        }
    ]
    
    resultado_lote = whatsapp.enviar_em_lote(destinatarios)
    print(f"   Total: {resultado_lote['total']}")
    print(f"   Sucesso: {resultado_lote['sucesso']}")
    print(f"   Falhas: {resultado_lote['falha']}\n")
    
    # Teste 5: Estatísticas
    print("5️⃣ Estatísticas do sistema...")
    stats = whatsapp.obter_estatisticas()
    print(f"   Templates: {stats['templates_disponiveis']}")
    print(f"   API Configurada: {'✅ SIM' if stats['api_configurada'] else '❌ NÃO'}")
    print(f"   Modo: {stats['modo'].upper()}\n")
    
    # Salvar exemplo de mensagem
    print("6️⃣ Salvando exemplo de mensagem...")
    with open('/tmp/whatsapp_exemplo.txt', 'w', encoding='utf-8') as f:
        f.write(resultado.get('mensagem', ''))
    print(f"   ✅ Salvo em: /tmp/whatsapp_exemplo.txt\n")
    
    print("="*60)
    print("✅ SISTEMA WHATSAPP FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Criar conta WhatsApp Business API")
    print("   2. Obter API_KEY e PHONE_ID")
    print("   3. Configurar variáveis de ambiente")
    print("   4. Testar com números reais\n")


if __name__ == '__main__':
    testar_whatsapp()
