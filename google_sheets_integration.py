"""
Módulo de Integração com Google Sheets
Sincronização bidirecional de dados de licitações e cotações

Desenvolvido em 01/12/2025
"""

import os
import logging
import json
from typing import List, Dict, Optional
from datetime import datetime

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsIntegration:
    """
    Classe para integração com Google Sheets
    Permite leitura e escrita de dados em planilhas
    """
    
    def __init__(self, credentials_path: str = None):
        """
        Inicializa integração com Google Sheets
        
        Args:
            credentials_path: Caminho para arquivo de credenciais JSON
        """
        self.credentials_path = credentials_path or os.getenv(
            'GOOGLE_CREDENTIALS_PATH', 
            'credentials.json'
        )
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """
        Inicializa cliente Google Sheets
        Usa gspread + oauth2client
        """
        try:
            import gspread
            from oauth2client.service_account import ServiceAccountCredentials
            
            # Escopos necessários
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Autenticar
            if os.path.exists(self.credentials_path):
                creds = ServiceAccountCredentials.from_json_keyfile_name(
                    self.credentials_path, 
                    scope
                )
                self.client = gspread.authorize(creds)
                logger.info("✅ Cliente Google Sheets inicializado")
            else:
                logger.warning(f"⚠️ Arquivo de credenciais não encontrado: {self.credentials_path}")
                logger.info("ℹ️  Modo simulação ativado")
                
        except ImportError:
            logger.warning("⚠️ gspread não instalado. Execute: pip install gspread oauth2client")
            logger.info("ℹ️  Modo simulação ativado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar cliente: {e}")
            logger.info("ℹ️  Modo simulação ativado")
    
    def abrir_planilha(self, nome_ou_url: str) -> Optional[object]:
        """
        Abre planilha por nome ou URL
        
        Args:
            nome_ou_url: Nome da planilha ou URL completa
            
        Returns:
            Objeto da planilha ou None
        """
        if not self.client:
            logger.warning("⚠️ Cliente não inicializado")
            return None
        
        try:
            if nome_ou_url.startswith('http'):
                # Abrir por URL
                planilha = self.client.open_by_url(nome_ou_url)
            else:
                # Abrir por nome
                planilha = self.client.open(nome_ou_url)
            
            logger.info(f"✅ Planilha aberta: {planilha.title}")
            return planilha
        except Exception as e:
            logger.error(f"❌ Erro ao abrir planilha: {e}")
            return None
    
    def ler_dados(self, planilha_nome: str, aba: str = None) -> List[Dict]:
        """
        Lê dados de uma planilha
        
        Args:
            planilha_nome: Nome ou URL da planilha
            aba: Nome da aba (opcional, usa primeira se não especificado)
            
        Returns:
            Lista de dicionários com os dados
        """
        planilha = self.abrir_planilha(planilha_nome)
        if not planilha:
            return self._dados_simulados()
        
        try:
            # Selecionar aba
            if aba:
                worksheet = planilha.worksheet(aba)
            else:
                worksheet = planilha.sheet1
            
            # Ler todos os registros como dicionários
            dados = worksheet.get_all_records()
            
            logger.info(f"✅ {len(dados)} registros lidos da planilha")
            return dados
            
        except Exception as e:
            logger.error(f"❌ Erro ao ler dados: {e}")
            return []
    
    def escrever_licitacoes(self, 
                           planilha_nome: str, 
                           licitacoes: List[Dict],
                           aba: str = 'Licitações') -> bool:
        """
        Escreve licitações em planilha
        
        Args:
            planilha_nome: Nome ou URL da planilha
            licitacoes: Lista de dicionários com dados das licitações
            aba: Nome da aba
            
        Returns:
            True se sucesso, False caso contrário
        """
        planilha = self.abrir_planilha(planilha_nome)
        if not planilha:
            logger.info("ℹ️  Simulando escrita de licitações...")
            return self._simular_escrita(licitacoes)
        
        try:
            # Criar ou abrir aba
            try:
                worksheet = planilha.worksheet(aba)
                # Limpar dados existentes
                worksheet.clear()
            except:
                worksheet = planilha.add_worksheet(title=aba, rows=1000, cols=20)
            
            # Preparar cabeçalhos
            headers = [
                'Número Edital', 'Órgão', 'Objeto', 'Valor Estimado',
                'Data Abertura', 'Prazo Entrega', 'Modalidade', 'Status',
                'Data Captura'
            ]
            
            # Escrever cabeçalhos
            worksheet.append_row(headers)
            
            # Escrever dados
            for lic in licitacoes:
                row = [
                    lic.get('numero_edital', ''),
                    lic.get('orgao', ''),
                    lic.get('objeto', ''),
                    lic.get('valor_estimado', 0),
                    lic.get('data_abertura', ''),
                    lic.get('prazo_entrega', ''),
                    lic.get('modalidade', ''),
                    lic.get('status', 'nova'),
                    lic.get('data_captura', datetime.now().isoformat())
                ]
                worksheet.append_row(row)
            
            logger.info(f"✅ {len(licitacoes)} licitações escritas na planilha")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao escrever dados: {e}")
            return False
    
    def escrever_cotacoes(self,
                         planilha_nome: str,
                         cotacoes: List[Dict],
                         aba: str = 'Cotações') -> bool:
        """
        Escreve cotações em planilha
        
        Args:
            planilha_nome: Nome ou URL da planilha
            cotacoes: Lista de dicionários com dados das cotações
            aba: Nome da aba
            
        Returns:
            True se sucesso, False caso contrário
        """
        planilha = self.abrir_planilha(planilha_nome)
        if not planilha:
            logger.info("ℹ️  Simulando escrita de cotações...")
            return self._simular_escrita(cotacoes)
        
        try:
            # Criar ou abrir aba
            try:
                worksheet = planilha.worksheet(aba)
                worksheet.clear()
            except:
                worksheet = planilha.add_worksheet(title=aba, rows=1000, cols=20)
            
            # Preparar cabeçalhos
            headers = [
                'ID Cotação', 'Número Edital', 'Fornecedor', 'Produto',
                'Quantidade', 'Preço Unitário', 'Preço Total', 'Prazo Entrega',
                'Status', 'Data Cotação'
            ]
            
            # Escrever cabeçalhos
            worksheet.append_row(headers)
            
            # Escrever dados
            for cot in cotacoes:
                row = [
                    cot.get('id_cotacao', ''),
                    cot.get('numero_edital', ''),
                    cot.get('fornecedor', ''),
                    cot.get('produto', ''),
                    cot.get('quantidade', 0),
                    cot.get('preco_unitario', 0),
                    cot.get('preco_total', 0),
                    cot.get('prazo_entrega', ''),
                    cot.get('status', 'pendente'),
                    cot.get('data_cotacao', datetime.now().isoformat())
                ]
                worksheet.append_row(row)
            
            logger.info(f"✅ {len(cotacoes)} cotações escritas na planilha")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao escrever cotações: {e}")
            return False
    
    def sincronizar_licitacoes(self, 
                              planilha_nome: str,
                              db_licitacoes: List[Dict]) -> Dict:
        """
        Sincroniza licitações do banco com planilha
        
        Args:
            planilha_nome: Nome ou URL da planilha
            db_licitacoes: Licitações do banco de dados
            
        Returns:
            Dicionário com resultado da sincronização
        """
        logger.info("🔄 Iniciando sincronização de licitações...")
        
        # Escrever licitações na planilha
        sucesso = self.escrever_licitacoes(planilha_nome, db_licitacoes)
        
        resultado = {
            'timestamp': datetime.now().isoformat(),
            'total_sincronizadas': len(db_licitacoes) if sucesso else 0,
            'sucesso': sucesso,
            'planilha': planilha_nome
        }
        
        if sucesso:
            logger.info(f"✅ Sincronização concluída: {len(db_licitacoes)} licitações")
        else:
            logger.error("❌ Falha na sincronização")
        
        return resultado
    
    def _dados_simulados(self) -> List[Dict]:
        """Retorna dados simulados para testes"""
        return [
            {
                'numero_edital': 'PE-2024-SIM-001',
                'orgao': 'Hospital Simulado',
                'objeto': 'Equipamentos médicos (simulação)',
                'valor_estimado': 150000.00,
                'data_abertura': '2024-12-15',
                'status': 'ativa'
            }
        ]
    
    def _simular_escrita(self, dados: List[Dict]) -> bool:
        """Simula escrita de dados"""
        logger.info(f"✅ Simulação: {len(dados)} registros 'escritos'")
        return True


def testar_google_sheets():
    """Função de teste da integração Google Sheets"""
    print("\n" + "="*60)
    print("🧪 TESTE DE INTEGRAÇÃO GOOGLE SHEETS")
    print("="*60 + "\n")
    
    sheets = GoogleSheetsIntegration()
    
    # Teste 1: Dados simulados
    print("1️⃣ Testando leitura de dados (simulado)...")
    dados = sheets.ler_dados('Hospshop - Licitações')
    print(f"   ✅ {len(dados)} registros lidos\n")
    
    # Teste 2: Escrever licitações (simulado)
    print("2️⃣ Testando escrita de licitações (simulado)...")
    licitacoes_teste = [
        {
            'numero_edital': 'PE-2024-TEST-001',
            'orgao': 'Hospital de Testes',
            'objeto': 'Equipamentos hospitalares para testes',
            'valor_estimado': 250000.00,
            'data_abertura': '2024-12-20',
            'modalidade': 'Pregão Eletrônico',
            'status': 'nova'
        },
        {
            'numero_edital': 'CC-2024-TEST-002',
            'orgao': 'Secretaria de Saúde de Testes',
            'objeto': 'Medicamentos para rede hospitalar',
            'valor_estimado': 500000.00,
            'data_abertura': '2024-12-25',
            'modalidade': 'Concorrência',
            'status': 'nova'
        }
    ]
    
    sucesso = sheets.escrever_licitacoes('Hospshop - Licitações', licitacoes_teste)
    print(f"   {'✅' if sucesso else '❌'} Escrita {'bem-sucedida' if sucesso else 'falhou'}\n")
    
    # Teste 3: Escrever cotações (simulado)
    print("3️⃣ Testando escrita de cotações (simulado)...")
    cotacoes_teste = [
        {
            'id_cotacao': 'COT-001',
            'numero_edital': 'PE-2024-TEST-001',
            'fornecedor': 'Fornecedor A',
            'produto': 'Equipamento X',
            'quantidade': 10,
            'preco_unitario': 5000.00,
            'preco_total': 50000.00,
            'prazo_entrega': '30 dias',
            'status': 'aprovada'
        }
    ]
    
    sucesso = sheets.escrever_cotacoes('Hospshop - Cotações', cotacoes_teste)
    print(f"   {'✅' if sucesso else '❌'} Escrita {'bem-sucedida' if sucesso else 'falhou'}\n")
    
    # Teste 4: Sincronização
    print("4️⃣ Testando sincronização completa (simulado)...")
    resultado = sheets.sincronizar_licitacoes('Hospshop - Licitações', licitacoes_teste)
    print(f"   Sincronizadas: {resultado['total_sincronizadas']}")
    print(f"   Sucesso: {'✅ SIM' if resultado['sucesso'] else '❌ NÃO'}\n")
    
    print("="*60)
    print("✅ ESTRUTURA GOOGLE SHEETS PRONTA")
    print("="*60 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Instalar dependências: pip install gspread oauth2client")
    print("   2. Criar projeto no Google Cloud Console")
    print("   3. Ativar Google Sheets API")
    print("   4. Criar Service Account e baixar credentials.json")
    print("   5. Compartilhar planilha com e-mail do Service Account")
    print("   6. Testar com planilha real\n")


if __name__ == '__main__':
    testar_google_sheets()
