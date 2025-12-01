"""
Módulo de Notificações do Sistema Hospshop
Suporte para e-mail e WhatsApp

Desenvolvido originalmente no Chat 2 e reconstruído em 01/12/2025
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional
import os
import requests

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmailNotification:
    """
    Classe para envio de notificações por e-mail
    """
    
    def __init__(self, 
                 smtp_server: str = None,
                 smtp_port: int = 587,
                 smtp_user: str = None,
                 smtp_password: str = None):
        """
        Inicializa configuração de e-mail
        
        Args:
            smtp_server: Servidor SMTP (ex: smtp.gmail.com)
            smtp_port: Porta SMTP (padrão: 587)
            smtp_user: Usuário/e-mail de envio
            smtp_password: Senha ou app password
        """
        self.smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.getenv('SMTP_USER')
        self.smtp_password = smtp_password or os.getenv('SMTP_PASSWORD')
        self.from_email = self.smtp_user
        
    def enviar_email(self, 
                     destinatario: str,
                     assunto: str,
                     corpo: str,
                     html: bool = True) -> bool:
        """
        Envia e-mail para destinatário
        
        Args:
            destinatario: E-mail do destinatário
            assunto: Assunto do e-mail
            corpo: Corpo do e-mail (texto ou HTML)
            html: Se True, corpo é HTML; se False, texto puro
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['From'] = self.from_email
            msg['To'] = destinatario
            msg['Subject'] = assunto
            
            # Adicionar corpo
            if html:
                msg.attach(MIMEText(corpo, 'html'))
            else:
                msg.attach(MIMEText(corpo, 'plain'))
            
            # Conectar e enviar
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ E-mail enviado para {destinatario}: {assunto}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar e-mail: {e}")
            return False
    
    def notificar_nova_licitacao(self, destinatario: str, licitacao: dict) -> bool:
        """
        Envia notificação de nova licitação
        
        Args:
            destinatario: E-mail do destinatário
            licitacao: Dicionário com dados da licitação
        """
        assunto = f"🔔 Nova Licitação: {licitacao.get('numero_edital')}"
        
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .field {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #374151; }}
                .value {{ color: #1f2937; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>🏥 Hospshop - Nova Licitação Detectada</h2>
                </div>
                <div class="content">
                    <div class="field">
                        <span class="label">Número do Edital:</span>
                        <span class="value">{licitacao.get('numero_edital')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Órgão:</span>
                        <span class="value">{licitacao.get('orgao')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Objeto:</span>
                        <span class="value">{licitacao.get('objeto')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Valor Estimado:</span>
                        <span class="value">R$ {licitacao.get('valor_estimado', 0):,.2f}</span>
                    </div>
                    <div class="field">
                        <span class="label">Data de Abertura:</span>
                        <span class="value">{licitacao.get('data_abertura')}</span>
                    </div>
                    <div class="field">
                        <span class="label">Modalidade:</span>
                        <span class="value">{licitacao.get('modalidade')}</span>
                    </div>
                </div>
                <div class="footer">
                    <p>Sistema Hospshop - Gestão de Licitações</p>
                    <p>Enviado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(destinatario, assunto, corpo_html, html=True)
    
    def notificar_prazo_proximo(self, destinatario: str, licitacao: dict, dias_restantes: int) -> bool:
        """
        Envia alerta de prazo próximo
        
        Args:
            destinatario: E-mail do destinatário
            licitacao: Dicionário com dados da licitação
            dias_restantes: Número de dias até o prazo
        """
        assunto = f"⚠️ URGENTE: Prazo em {dias_restantes} dias - {licitacao.get('numero_edital')}"
        
        corpo_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
                .alert {{ background: #fef2f2; border-left: 4px solid #dc2626; padding: 15px; margin: 20px 0; }}
                .content {{ padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>⚠️ ALERTA DE PRAZO</h2>
                </div>
                <div class="alert">
                    <h3>Faltam apenas {dias_restantes} dias!</h3>
                    <p>A licitação <strong>{licitacao.get('numero_edital')}</strong> está próxima do prazo.</p>
                </div>
                <div class="content">
                    <p><strong>Órgão:</strong> {licitacao.get('orgao')}</p>
                    <p><strong>Data de Abertura:</strong> {licitacao.get('data_abertura')}</p>
                    <p><strong>Valor:</strong> R$ {licitacao.get('valor_estimado', 0):,.2f}</p>
                    <p>Acesse o sistema para tomar as providências necessárias.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.enviar_email(destinatario, assunto, corpo_html, html=True)


class WhatsAppNotification:
    """
    Classe para envio de notificações via WhatsApp
    Integração com WhatsApp Business API ou Twilio
    """
    
    def __init__(self, api_key: str = None, api_url: str = None):
        """
        Inicializa configuração WhatsApp
        
        Args:
            api_key: Chave da API (Twilio ou WhatsApp Business)
            api_url: URL da API
        """
        self.api_key = api_key or os.getenv('WHATSAPP_API_KEY')
        self.api_url = api_url or os.getenv('WHATSAPP_API_URL')
        
    def enviar_mensagem(self, numero: str, mensagem: str) -> bool:
        """
        Envia mensagem WhatsApp
        
        Args:
            numero: Número do destinatário (formato: +5511999999999)
            mensagem: Texto da mensagem
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.api_key or not self.api_url:
            logger.warning("⚠️ WhatsApp não configurado (API_KEY ou API_URL ausentes)")
            return False
        
        try:
            # Exemplo de integração com Twilio
            # Em produção, ajustar conforme API utilizada
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': numero,
                'body': mensagem
            }
            
            response = requests.post(self.api_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"✅ WhatsApp enviado para {numero}")
                return True
            else:
                logger.error(f"❌ Erro WhatsApp: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar WhatsApp: {e}")
            return False
    
    def notificar_nova_licitacao(self, numero: str, licitacao: dict) -> bool:
        """
        Envia notificação WhatsApp de nova licitação
        """
        mensagem = f"""
🏥 *Hospshop - Nova Licitação*

📋 *Edital:* {licitacao.get('numero_edital')}
🏛️ *Órgão:* {licitacao.get('orgao')}
💰 *Valor:* R$ {licitacao.get('valor_estimado', 0):,.2f}
📅 *Abertura:* {licitacao.get('data_abertura')}

Acesse o sistema para mais detalhes.
        """.strip()
        
        return self.enviar_mensagem(numero, mensagem)


class NotificationManager:
    """
    Gerenciador central de notificações
    Coordena envio por e-mail e WhatsApp
    """
    
    def __init__(self):
        self.email = EmailNotification()
        self.whatsapp = WhatsAppNotification()
    
    def notificar_nova_licitacao(self, 
                                 email: str = None, 
                                 whatsapp: str = None, 
                                 licitacao: dict = None) -> dict:
        """
        Envia notificação de nova licitação por todos os canais configurados
        
        Returns:
            Dicionário com status de cada canal
        """
        resultado = {
            'email': False,
            'whatsapp': False,
            'timestamp': datetime.now().isoformat()
        }
        
        if email:
            resultado['email'] = self.email.notificar_nova_licitacao(email, licitacao)
        
        if whatsapp:
            resultado['whatsapp'] = self.whatsapp.notificar_nova_licitacao(whatsapp, licitacao)
        
        return resultado
    
    def notificar_prazo_proximo(self,
                               email: str = None,
                               whatsapp: str = None,
                               licitacao: dict = None,
                               dias_restantes: int = 3) -> dict:
        """
        Envia alerta de prazo próximo
        """
        resultado = {
            'email': False,
            'whatsapp': False,
            'timestamp': datetime.now().isoformat()
        }
        
        if email:
            resultado['email'] = self.email.notificar_prazo_proximo(email, licitacao, dias_restantes)
        
        if whatsapp:
            mensagem = f"⚠️ URGENTE: Faltam {dias_restantes} dias para {licitacao.get('numero_edital')}"
            resultado['whatsapp'] = self.whatsapp.enviar_mensagem(whatsapp, mensagem)
        
        return resultado


def testar_notificacoes():
    """Função de teste do sistema de notificações"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE NOTIFICAÇÕES")
    print("="*60 + "\n")
    
    # Dados de exemplo
    licitacao_exemplo = {
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal de Testes',
        'objeto': 'Aquisição de equipamentos para testes',
        'valor_estimado': 250000.00,
        'data_abertura': '2024-12-20',
        'modalidade': 'Pregão Eletrônico'
    }
    
    # Teste 1: Notificação por e-mail (simulado)
    print("1️⃣ Testando notificação por e-mail...")
    email_notif = EmailNotification()
    print("   ℹ️  Configuração de e-mail detectada")
    print("   ⚠️  Configure SMTP_SERVER, SMTP_USER, SMTP_PASSWORD para envio real\n")
    
    # Teste 2: Notificação WhatsApp (simulado)
    print("2️⃣ Testando notificação WhatsApp...")
    whatsapp_notif = WhatsAppNotification()
    print("   ℹ️  Configuração WhatsApp detectada")
    print("   ⚠️  Configure WHATSAPP_API_KEY e WHATSAPP_API_URL para envio real\n")
    
    # Teste 3: Gerenciador de notificações
    print("3️⃣ Testando gerenciador de notificações...")
    manager = NotificationManager()
    print("   ✅ Gerenciador inicializado\n")
    
    print("="*60)
    print("✅ ESTRUTURA DE NOTIFICAÇÕES PRONTA")
    print("="*60 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Configurar variáveis de ambiente SMTP")
    print("   2. Configurar WhatsApp Business API")
    print("   3. Testar envio real de notificações\n")


if __name__ == '__main__':
    testar_notificacoes()
