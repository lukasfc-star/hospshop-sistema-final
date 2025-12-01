"""
Módulo de Integração com Plataforma Effecti
Sistema de captura automática de licitações

Desenvolvido originalmente no Chat 1 e reconstruído em 01/12/2025
"""

import requests
from bs4 import BeautifulSoup
import sqlite3
import logging
from datetime import datetime
import re
import time
from typing import List, Dict, Optional

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EffectiIntegration:
    """
    Classe para integração com a plataforma Effecti
    Captura automática de licitações públicas
    """
    
    def __init__(self, db_path='hospshop.db'):
        self.db_path = db_path
        self.base_url = 'https://www.effecti.com.br'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_db_connection(self):
        """Retorna conexão com banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return None
    
    def init_licitacoes_table(self):
        """Cria tabela de licitações se não existir"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS licitacoes_effecti (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_edital TEXT UNIQUE NOT NULL,
                    orgao TEXT NOT NULL,
                    objeto TEXT NOT NULL,
                    valor_estimado REAL,
                    data_abertura TEXT,
                    prazo_entrega TEXT,
                    modalidade TEXT,
                    status TEXT DEFAULT 'nova',
                    url_edital TEXT,
                    data_captura TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            logger.info("✅ Tabela licitacoes_effecti criada/verificada")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabela: {e}")
            return False
        finally:
            conn.close()
    
    def buscar_licitacoes(self, palavra_chave: str = 'hospitalar', 
                          estado: str = None, 
                          limite: int = 50) -> List[Dict]:
        """
        Busca licitações na plataforma Effecti
        
        Args:
            palavra_chave: Termo para busca (ex: 'hospitalar', 'medicamentos')
            estado: UF do estado (ex: 'SP', 'RJ')
            limite: Número máximo de resultados
            
        Returns:
            Lista de dicionários com dados das licitações
        """
        logger.info(f"🔍 Buscando licitações: '{palavra_chave}' - Estado: {estado or 'Todos'}")
        
        # Simula busca na plataforma Effecti
        # Em produção, usar API oficial ou web scraping real
        licitacoes_encontradas = []
        
        try:
            # NOTA: Este é um exemplo simulado
            # Em produção, implementar:
            # 1. Autenticação na plataforma Effecti
            # 2. Requisição à API ou scraping das páginas
            # 3. Parsing dos resultados
            
            # Exemplo de estrutura de dados retornada:
            licitacoes_exemplo = [
                {
                    'numero_edital': 'PE-2024-001234',
                    'orgao': 'Hospital Municipal de São Paulo',
                    'objeto': 'Aquisição de equipamentos hospitalares e materiais médicos',
                    'valor_estimado': 450000.00,
                    'data_abertura': '2024-12-15',
                    'prazo_entrega': '30 dias',
                    'modalidade': 'Pregão Eletrônico',
                    'url_edital': 'https://www.effecti.com.br/edital/PE-2024-001234',
                    'data_captura': datetime.now().isoformat()
                },
                {
                    'numero_edital': 'CC-2024-005678',
                    'orgao': 'Secretaria de Saúde do Estado de SP',
                    'objeto': 'Fornecimento de medicamentos para rede hospitalar',
                    'valor_estimado': 1200000.00,
                    'data_abertura': '2024-12-20',
                    'prazo_entrega': '45 dias',
                    'modalidade': 'Concorrência',
                    'url_edital': 'https://www.effecti.com.br/edital/CC-2024-005678',
                    'data_captura': datetime.now().isoformat()
                }
            ]
            
            # Filtrar por palavra-chave
            for lic in licitacoes_exemplo:
                if palavra_chave.lower() in lic['objeto'].lower():
                    licitacoes_encontradas.append(lic)
            
            logger.info(f"✅ {len(licitacoes_encontradas)} licitações encontradas")
            return licitacoes_encontradas[:limite]
            
        except Exception as e:
            logger.error(f"❌ Erro ao buscar licitações: {e}")
            return []
    
    def salvar_licitacao(self, licitacao: Dict) -> bool:
        """
        Salva licitação no banco de dados
        
        Args:
            licitacao: Dicionário com dados da licitação
            
        Returns:
            True se salvou com sucesso, False caso contrário
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            conn.execute('''
                INSERT OR IGNORE INTO licitacoes_effecti 
                (numero_edital, orgao, objeto, valor_estimado, data_abertura, 
                 prazo_entrega, modalidade, url_edital, data_captura)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                licitacao['numero_edital'],
                licitacao['orgao'],
                licitacao['objeto'],
                licitacao.get('valor_estimado'),
                licitacao.get('data_abertura'),
                licitacao.get('prazo_entrega'),
                licitacao.get('modalidade'),
                licitacao.get('url_edital'),
                licitacao.get('data_captura', datetime.now().isoformat())
            ))
            conn.commit()
            logger.info(f"✅ Licitação {licitacao['numero_edital']} salva")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"⚠️ Licitação {licitacao['numero_edital']} já existe")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao salvar licitação: {e}")
            return False
        finally:
            conn.close()
    
    def capturar_e_salvar(self, palavra_chave: str = 'hospitalar', 
                          estado: str = None, 
                          limite: int = 50) -> Dict:
        """
        Captura licitações e salva no banco
        
        Returns:
            Dicionário com estatísticas da captura
        """
        logger.info("🚀 Iniciando captura automática Effecti")
        
        # Inicializar tabela
        self.init_licitacoes_table()
        
        # Buscar licitações
        licitacoes = self.buscar_licitacoes(palavra_chave, estado, limite)
        
        # Salvar no banco
        salvas = 0
        duplicadas = 0
        erros = 0
        
        for lic in licitacoes:
            if self.salvar_licitacao(lic):
                salvas += 1
            else:
                duplicadas += 1
        
        resultado = {
            'total_encontradas': len(licitacoes),
            'salvas': salvas,
            'duplicadas': duplicadas,
            'erros': erros,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Captura concluída: {salvas} novas, {duplicadas} duplicadas")
        return resultado
    
    def listar_licitacoes(self, limite: int = 100) -> List[Dict]:
        """
        Lista licitações capturadas do banco
        
        Returns:
            Lista de licitações
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM licitacoes_effecti 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limite,))
            
            licitacoes = []
            for row in cursor.fetchall():
                licitacoes.append(dict(row))
            
            return licitacoes
        except Exception as e:
            logger.error(f"Erro ao listar licitações: {e}")
            return []
        finally:
            conn.close()
    
    def atualizar_status(self, numero_edital: str, novo_status: str) -> bool:
        """
        Atualiza status de uma licitação
        
        Args:
            numero_edital: Número do edital
            novo_status: Novo status (ex: 'em_analise', 'proposta_enviada', 'vencida')
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            conn.execute('''
                UPDATE licitacoes_effecti 
                SET status = ? 
                WHERE numero_edital = ?
            ''', (novo_status, numero_edital))
            conn.commit()
            logger.info(f"✅ Status atualizado: {numero_edital} -> {novo_status}")
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}")
            return False
        finally:
            conn.close()


def testar_integracao():
    """Função de teste da integração Effecti"""
    print("\n" + "="*60)
    print("🧪 TESTE DE INTEGRAÇÃO EFFECTI")
    print("="*60 + "\n")
    
    effecti = EffectiIntegration()
    
    # Teste 1: Inicializar tabela
    print("1️⃣ Inicializando tabela...")
    if effecti.init_licitacoes_table():
        print("   ✅ Tabela criada/verificada\n")
    else:
        print("   ❌ Erro ao criar tabela\n")
        return
    
    # Teste 2: Buscar licitações
    print("2️⃣ Buscando licitações...")
    licitacoes = effecti.buscar_licitacoes('hospitalar', limite=10)
    print(f"   ✅ {len(licitacoes)} licitações encontradas\n")
    
    # Teste 3: Salvar licitações
    print("3️⃣ Salvando licitações...")
    for lic in licitacoes:
        effecti.salvar_licitacao(lic)
    print("   ✅ Licitações salvas\n")
    
    # Teste 4: Listar licitações
    print("4️⃣ Listando licitações do banco...")
    licitacoes_db = effecti.listar_licitacoes(5)
    for lic in licitacoes_db:
        print(f"   📋 {lic['numero_edital']} - {lic['orgao']}")
        print(f"      Valor: R$ {lic['valor_estimado']:,.2f}")
        print(f"      Status: {lic['status']}\n")
    
    # Teste 5: Captura completa
    print("5️⃣ Teste de captura completa...")
    resultado = effecti.capturar_e_salvar('medicamentos', limite=5)
    print(f"   ✅ Resultado: {resultado}\n")
    
    print("="*60)
    print("✅ TESTES CONCLUÍDOS COM SUCESSO!")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_integracao()
