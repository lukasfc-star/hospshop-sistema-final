"""
Módulo de Padronização de Captação de Licitações
Sistema de filtros e validação de critérios

Desenvolvido originalmente no Chat 2 e reconstruído em 01/12/2025
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PadronizacaoCaptacao:
    """
    Classe para gerenciar padronização e filtros de captação de licitações
    """
    
    def __init__(self, db_path='hospshop.db'):
        self.db_path = db_path
        self.init_tables()
    
    def get_db_connection(self):
        """Retorna conexão com banco de dados"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return None
    
    def init_tables(self):
        """Cria tabelas de configuração se não existirem"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Tabela de configurações de filtros
            conn.execute('''
                CREATE TABLE IF NOT EXISTS config_filtros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    configuracao TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de estados prioritários
            conn.execute('''
                CREATE TABLE IF NOT EXISTS estados_prioritarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uf TEXT UNIQUE NOT NULL,
                    nome TEXT NOT NULL,
                    prioridade INTEGER DEFAULT 1,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de tipos de cliente
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tipos_cliente (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tipo TEXT UNIQUE NOT NULL,
                    descricao TEXT,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de palavras-chave
            conn.execute('''
                CREATE TABLE IF NOT EXISTS palavras_chave (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    palavra TEXT UNIQUE NOT NULL,
                    categoria TEXT,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tabelas de padronização criadas/verificadas")
            
            # Inserir dados padrão se tabelas estiverem vazias
            self._inserir_dados_padrao(conn)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            conn.close()
    
    def _inserir_dados_padrao(self, conn):
        """Insere dados padrão nas tabelas de configuração"""
        try:
            # Estados prioritários padrão
            estados_padrao = [
                ('SP', 'São Paulo', 1),
                ('RJ', 'Rio de Janeiro', 1),
                ('MG', 'Minas Gerais', 1),
                ('PR', 'Paraná', 2),
                ('RS', 'Rio Grande do Sul', 2),
                ('SC', 'Santa Catarina', 2),
                ('BA', 'Bahia', 3),
                ('PE', 'Pernambuco', 3),
                ('CE', 'Ceará', 3)
            ]
            
            for uf, nome, prioridade in estados_padrao:
                conn.execute('''
                    INSERT OR IGNORE INTO estados_prioritarios (uf, nome, prioridade)
                    VALUES (?, ?, ?)
                ''', (uf, nome, prioridade))
            
            # Tipos de cliente padrão
            tipos_padrao = [
                ('Hospital Público', 'Hospitais municipais, estaduais e federais'),
                ('Hospital Privado', 'Hospitais e clínicas privadas'),
                ('Secretaria de Saúde', 'Secretarias municipais e estaduais'),
                ('Unidade Básica de Saúde', 'UBS e postos de saúde'),
                ('Laboratório', 'Laboratórios de análises clínicas'),
                ('Clínica Especializada', 'Clínicas de especialidades médicas')
            ]
            
            for tipo, descricao in tipos_padrao:
                conn.execute('''
                    INSERT OR IGNORE INTO tipos_cliente (tipo, descricao)
                    VALUES (?, ?)
                ''', (tipo, descricao))
            
            # Palavras-chave padrão
            palavras_padrao = [
                ('hospitalar', 'Equipamentos'),
                ('medicamentos', 'Medicamentos'),
                ('equipamentos médicos', 'Equipamentos'),
                ('material cirúrgico', 'Materiais'),
                ('insumos hospitalares', 'Materiais'),
                ('aparelhos médicos', 'Equipamentos'),
                ('UTI', 'Equipamentos'),
                ('centro cirúrgico', 'Equipamentos'),
                ('diagnóstico', 'Equipamentos'),
                ('laboratório', 'Equipamentos')
            ]
            
            for palavra, categoria in palavras_padrao:
                conn.execute('''
                    INSERT OR IGNORE INTO palavras_chave (palavra, categoria)
                    VALUES (?, ?)
                ''', (palavra, categoria))
            
            conn.commit()
            logger.info("✅ Dados padrão inseridos")
            
        except Exception as e:
            logger.error(f"Erro ao inserir dados padrão: {e}")
    
    def criar_filtro(self, nome: str, descricao: str, configuracao: dict) -> bool:
        """
        Cria novo filtro de captação
        
        Args:
            nome: Nome do filtro
            descricao: Descrição do filtro
            configuracao: Dicionário com configurações do filtro
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            config_json = json.dumps(configuracao)
            conn.execute('''
                INSERT INTO config_filtros (nome, descricao, configuracao)
                VALUES (?, ?, ?)
            ''', (nome, descricao, config_json))
            conn.commit()
            logger.info(f"✅ Filtro '{nome}' criado")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar filtro: {e}")
            return False
        finally:
            conn.close()
    
    def obter_filtro(self, nome: str) -> Optional[Dict]:
        """
        Obtém configuração de um filtro
        
        Args:
            nome: Nome do filtro
            
        Returns:
            Dicionário com configuração do filtro ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.execute('''
                SELECT * FROM config_filtros WHERE nome = ?
            ''', (nome,))
            row = cursor.fetchone()
            
            if row:
                filtro = dict(row)
                filtro['configuracao'] = json.loads(filtro['configuracao'])
                return filtro
            return None
        except Exception as e:
            logger.error(f"Erro ao obter filtro: {e}")
            return None
        finally:
            conn.close()
    
    def listar_estados_prioritarios(self) -> List[Dict]:
        """Lista estados prioritários ativos"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM estados_prioritarios 
                WHERE ativo = 1 
                ORDER BY prioridade, nome
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar estados: {e}")
            return []
        finally:
            conn.close()
    
    def listar_tipos_cliente(self) -> List[Dict]:
        """Lista tipos de cliente ativos"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM tipos_cliente 
                WHERE ativo = 1 
                ORDER BY tipo
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar tipos de cliente: {e}")
            return []
        finally:
            conn.close()
    
    def listar_palavras_chave(self, categoria: str = None) -> List[Dict]:
        """
        Lista palavras-chave ativas
        
        Args:
            categoria: Filtrar por categoria (opcional)
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            if categoria:
                cursor = conn.execute('''
                    SELECT * FROM palavras_chave 
                    WHERE ativo = 1 AND categoria = ?
                    ORDER BY palavra
                ''', (categoria,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM palavras_chave 
                    WHERE ativo = 1 
                    ORDER BY categoria, palavra
                ''')
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar palavras-chave: {e}")
            return []
        finally:
            conn.close()
    
    def validar_licitacao(self, licitacao: Dict) -> Dict:
        """
        Valida se licitação atende aos critérios de captação
        
        Args:
            licitacao: Dicionário com dados da licitação
            
        Returns:
            Dicionário com resultado da validação
        """
        resultado = {
            'valida': True,
            'motivos': [],
            'score': 0,
            'prioridade': 'baixa'
        }
        
        # Validar estado
        estados = self.listar_estados_prioritarios()
        ufs_prioritarias = [e['uf'] for e in estados]
        
        # Extrair UF do órgão (simplificado)
        orgao = licitacao.get('orgao', '').upper()
        uf_encontrada = None
        for uf in ufs_prioritarias:
            if uf in orgao:
                uf_encontrada = uf
                break
        
        if uf_encontrada:
            resultado['score'] += 30
            resultado['motivos'].append(f"Estado prioritário: {uf_encontrada}")
        
        # Validar palavras-chave
        palavras = self.listar_palavras_chave()
        objeto = licitacao.get('objeto', '').lower()
        
        palavras_encontradas = []
        for p in palavras:
            if p['palavra'].lower() in objeto:
                palavras_encontradas.append(p['palavra'])
                resultado['score'] += 20
        
        if palavras_encontradas:
            resultado['motivos'].append(f"Palavras-chave: {', '.join(palavras_encontradas)}")
        
        # Validar valor
        valor = licitacao.get('valor_estimado', 0)
        if valor >= 100000:
            resultado['score'] += 30
            resultado['motivos'].append(f"Valor alto: R$ {valor:,.2f}")
        elif valor >= 50000:
            resultado['score'] += 15
            resultado['motivos'].append(f"Valor médio: R$ {valor:,.2f}")
        
        # Definir prioridade baseada no score
        if resultado['score'] >= 70:
            resultado['prioridade'] = 'alta'
        elif resultado['score'] >= 40:
            resultado['prioridade'] = 'média'
        else:
            resultado['prioridade'] = 'baixa'
        
        # Validar se atende critérios mínimos
        if resultado['score'] < 20:
            resultado['valida'] = False
            resultado['motivos'].append("Score abaixo do mínimo")
        
        return resultado
    
    def adicionar_palavra_chave(self, palavra: str, categoria: str = 'Geral') -> bool:
        """Adiciona nova palavra-chave"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            conn.execute('''
                INSERT OR IGNORE INTO palavras_chave (palavra, categoria)
                VALUES (?, ?)
            ''', (palavra, categoria))
            conn.commit()
            logger.info(f"✅ Palavra-chave '{palavra}' adicionada")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar palavra-chave: {e}")
            return False
        finally:
            conn.close()
    
    def adicionar_estado_prioritario(self, uf: str, nome: str, prioridade: int = 1) -> bool:
        """Adiciona estado prioritário"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            conn.execute('''
                INSERT OR IGNORE INTO estados_prioritarios (uf, nome, prioridade)
                VALUES (?, ?, ?)
            ''', (uf, nome, prioridade))
            conn.commit()
            logger.info(f"✅ Estado '{uf}' adicionado")
            return True
        except Exception as e:
            logger.error(f"Erro ao adicionar estado: {e}")
            return False
        finally:
            conn.close()


def testar_padronizacao():
    """Função de teste do sistema de padronização"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE PADRONIZAÇÃO")
    print("="*60 + "\n")
    
    padrao = PadronizacaoCaptacao()
    
    # Teste 1: Listar estados prioritários
    print("1️⃣ Estados Prioritários:")
    estados = padrao.listar_estados_prioritarios()
    for e in estados[:5]:
        print(f"   {e['uf']} - {e['nome']} (Prioridade: {e['prioridade']})")
    print()
    
    # Teste 2: Listar tipos de cliente
    print("2️⃣ Tipos de Cliente:")
    tipos = padrao.listar_tipos_cliente()
    for t in tipos[:5]:
        print(f"   • {t['tipo']}")
    print()
    
    # Teste 3: Listar palavras-chave
    print("3️⃣ Palavras-Chave:")
    palavras = padrao.listar_palavras_chave()
    for p in palavras[:5]:
        print(f"   • {p['palavra']} ({p['categoria']})")
    print()
    
    # Teste 4: Validar licitação
    print("4️⃣ Validação de Licitação:")
    licitacao_teste = {
        'numero_edital': 'PE-2024-TEST',
        'orgao': 'Hospital Municipal de São Paulo - SP',
        'objeto': 'Aquisição de equipamentos hospitalares e medicamentos',
        'valor_estimado': 350000.00
    }
    
    resultado = padrao.validar_licitacao(licitacao_teste)
    print(f"   Válida: {'✅ SIM' if resultado['valida'] else '❌ NÃO'}")
    print(f"   Score: {resultado['score']}")
    print(f"   Prioridade: {resultado['prioridade'].upper()}")
    print(f"   Motivos:")
    for motivo in resultado['motivos']:
        print(f"      • {motivo}")
    print()
    
    print("="*60)
    print("✅ SISTEMA DE PADRONIZAÇÃO FUNCIONANDO")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_padronizacao()
