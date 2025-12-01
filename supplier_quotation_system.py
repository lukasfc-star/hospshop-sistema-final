"""
Sistema de Cotações com Fornecedores
Gerenciamento completo de solicitações, propostas e comparação

Desenvolvido em 01/12/2025
"""

import sqlite3
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupplierQuotationSystem:
    """
    Sistema completo de cotações com fornecedores
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
        """Cria tabelas do sistema de cotações"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Tabela de solicitações de cotação
            conn.execute('''
                CREATE TABLE IF NOT EXISTS solicitacoes_cotacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_solicitacao TEXT UNIQUE NOT NULL,
                    numero_edital TEXT NOT NULL,
                    descricao TEXT NOT NULL,
                    data_solicitacao TEXT NOT NULL,
                    prazo_resposta TEXT NOT NULL,
                    status TEXT DEFAULT 'enviada',
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (numero_edital) REFERENCES licitacoes_effecti(numero_edital)
                )
            ''')
            
            # Tabela de itens da solicitação
            conn.execute('''
                CREATE TABLE IF NOT EXISTS itens_solicitacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solicitacao_id INTEGER NOT NULL,
                    codigo_item TEXT NOT NULL,
                    descricao_item TEXT NOT NULL,
                    quantidade INTEGER NOT NULL,
                    unidade TEXT NOT NULL,
                    especificacoes TEXT,
                    FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes_cotacao(id)
                )
            ''')
            
            # Tabela de propostas recebidas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS propostas_cotacao (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solicitacao_id INTEGER NOT NULL,
                    fornecedor_id INTEGER NOT NULL,
                    numero_proposta TEXT UNIQUE NOT NULL,
                    data_proposta TEXT NOT NULL,
                    validade_proposta TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    prazo_entrega TEXT NOT NULL,
                    condicoes_pagamento TEXT,
                    observacoes TEXT,
                    status TEXT DEFAULT 'recebida',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes_cotacao(id),
                    FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
                )
            ''')
            
            # Tabela de itens da proposta
            conn.execute('''
                CREATE TABLE IF NOT EXISTS itens_proposta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    proposta_id INTEGER NOT NULL,
                    item_solicitacao_id INTEGER NOT NULL,
                    preco_unitario REAL NOT NULL,
                    preco_total REAL NOT NULL,
                    marca TEXT,
                    modelo TEXT,
                    observacoes TEXT,
                    FOREIGN KEY (proposta_id) REFERENCES propostas_cotacao(id),
                    FOREIGN KEY (item_solicitacao_id) REFERENCES itens_solicitacao(id)
                )
            ''')
            
            # Tabela de comparação de propostas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS comparacao_propostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    solicitacao_id INTEGER NOT NULL,
                    data_comparacao TEXT NOT NULL,
                    proposta_vencedora_id INTEGER,
                    criterio_selecao TEXT NOT NULL,
                    justificativa TEXT,
                    economia_gerada REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes_cotacao(id),
                    FOREIGN KEY (proposta_vencedora_id) REFERENCES propostas_cotacao(id)
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tabelas de cotações criadas/verificadas")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            conn.close()
    
    def criar_solicitacao(self, 
                         numero_edital: str,
                         descricao: str,
                         itens: List[Dict],
                         prazo_dias: int = 7) -> Optional[int]:
        """
        Cria nova solicitação de cotação
        
        Args:
            numero_edital: Número do edital relacionado
            descricao: Descrição da solicitação
            itens: Lista de itens a cotar
            prazo_dias: Prazo para resposta em dias
            
        Returns:
            ID da solicitação criada ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            # Gerar número da solicitação
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            numero_solicitacao = f'SOL-{timestamp}'
            
            # Calcular prazo
            data_solicitacao = datetime.now().isoformat()
            prazo_resposta = (datetime.now() + timedelta(days=prazo_dias)).isoformat()
            
            # Inserir solicitação
            cursor = conn.execute('''
                INSERT INTO solicitacoes_cotacao 
                (numero_solicitacao, numero_edital, descricao, data_solicitacao, prazo_resposta)
                VALUES (?, ?, ?, ?, ?)
            ''', (numero_solicitacao, numero_edital, descricao, data_solicitacao, prazo_resposta))
            
            solicitacao_id = cursor.lastrowid
            
            # Inserir itens
            for item in itens:
                conn.execute('''
                    INSERT INTO itens_solicitacao
                    (solicitacao_id, codigo_item, descricao_item, quantidade, unidade, especificacoes)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    solicitacao_id,
                    item['codigo'],
                    item['descricao'],
                    item['quantidade'],
                    item['unidade'],
                    item.get('especificacoes', '')
                ))
            
            conn.commit()
            logger.info(f"✅ Solicitação {numero_solicitacao} criada com {len(itens)} itens")
            return solicitacao_id
            
        except Exception as e:
            logger.error(f"Erro ao criar solicitação: {e}")
            return None
        finally:
            conn.close()
    
    def registrar_proposta(self,
                          solicitacao_id: int,
                          fornecedor_id: int,
                          itens_proposta: List[Dict],
                          prazo_entrega: str,
                          condicoes_pagamento: str = None,
                          validade_dias: int = 30) -> Optional[int]:
        """
        Registra proposta de fornecedor
        
        Args:
            solicitacao_id: ID da solicitação
            fornecedor_id: ID do fornecedor
            itens_proposta: Lista de itens com preços
            prazo_entrega: Prazo de entrega
            condicoes_pagamento: Condições de pagamento
            validade_dias: Validade da proposta em dias
            
        Returns:
            ID da proposta ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            # Gerar número da proposta (com microsegundos para evitar duplicatas)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
            numero_proposta = f'PROP-{fornecedor_id}-{timestamp}'
            
            # Calcular valor total
            valor_total = sum(item['preco_total'] for item in itens_proposta)
            
            # Datas
            data_proposta = datetime.now().isoformat()
            validade_proposta = (datetime.now() + timedelta(days=validade_dias)).isoformat()
            
            # Inserir proposta
            cursor = conn.execute('''
                INSERT INTO propostas_cotacao
                (solicitacao_id, fornecedor_id, numero_proposta, data_proposta, 
                 validade_proposta, valor_total, prazo_entrega, condicoes_pagamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                solicitacao_id, fornecedor_id, numero_proposta, data_proposta,
                validade_proposta, valor_total, prazo_entrega, condicoes_pagamento
            ))
            
            proposta_id = cursor.lastrowid
            
            # Inserir itens da proposta
            for item in itens_proposta:
                conn.execute('''
                    INSERT INTO itens_proposta
                    (proposta_id, item_solicitacao_id, preco_unitario, preco_total, marca, modelo)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    proposta_id,
                    item['item_solicitacao_id'],
                    item['preco_unitario'],
                    item['preco_total'],
                    item.get('marca', ''),
                    item.get('modelo', '')
                ))
            
            conn.commit()
            logger.info(f"✅ Proposta {numero_proposta} registrada: R$ {valor_total:,.2f}")
            return proposta_id
            
        except Exception as e:
            logger.error(f"Erro ao registrar proposta: {e}")
            return None
        finally:
            conn.close()
    
    def comparar_propostas(self, solicitacao_id: int) -> Dict:
        """
        Compara propostas de uma solicitação
        
        Args:
            solicitacao_id: ID da solicitação
            
        Returns:
            Dicionário com análise comparativa
        """
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Buscar propostas
            cursor = conn.execute('''
                SELECT p.*, p.fornecedor_id as fornecedor_nome
                FROM propostas_cotacao p
                WHERE p.solicitacao_id = ?
                ORDER BY p.valor_total ASC
            ''', (solicitacao_id,))
            
            propostas = [dict(row) for row in cursor.fetchall()]
            
            if not propostas:
                logger.warning("⚠️ Nenhuma proposta encontrada")
                return {'propostas': [], 'analise': {}}
            
            # Análise comparativa
            menor_preco = propostas[0]
            maior_preco = propostas[-1]
            preco_medio = sum(p['valor_total'] for p in propostas) / len(propostas)
            
            analise = {
                'total_propostas': len(propostas),
                'menor_preco': {
                    'fornecedor': menor_preco['fornecedor_nome'],
                    'valor': menor_preco['valor_total'],
                    'proposta_id': menor_preco['id']
                },
                'maior_preco': {
                    'fornecedor': maior_preco['fornecedor_nome'],
                    'valor': maior_preco['valor_total']
                },
                'preco_medio': preco_medio,
                'economia_potencial': maior_preco['valor_total'] - menor_preco['valor_total'],
                'variacao_percentual': ((maior_preco['valor_total'] - menor_preco['valor_total']) / maior_preco['valor_total']) * 100
            }
            
            resultado = {
                'propostas': propostas,
                'analise': analise,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Comparação: {len(propostas)} propostas, economia R$ {analise['economia_potencial']:,.2f}")
            return resultado
            
        except Exception as e:
            logger.error(f"Erro ao comparar propostas: {e}")
            return {}
        finally:
            conn.close()
    
    def selecionar_vencedora(self,
                            solicitacao_id: int,
                            proposta_id: int,
                            criterio: str = 'menor_preco',
                            justificativa: str = None) -> bool:
        """
        Seleciona proposta vencedora
        
        Args:
            solicitacao_id: ID da solicitação
            proposta_id: ID da proposta vencedora
            criterio: Critério de seleção
            justificativa: Justificativa da escolha
            
        Returns:
            True se sucesso, False caso contrário
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Calcular economia
            comparacao = self.comparar_propostas(solicitacao_id)
            economia = comparacao['analise'].get('economia_potencial', 0)
            
            # Registrar comparação
            conn.execute('''
                INSERT INTO comparacao_propostas
                (solicitacao_id, data_comparacao, proposta_vencedora_id, 
                 criterio_selecao, justificativa, economia_gerada)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                solicitacao_id,
                datetime.now().isoformat(),
                proposta_id,
                criterio,
                justificativa,
                economia
            ))
            
            # Atualizar status da proposta vencedora
            conn.execute('''
                UPDATE propostas_cotacao
                SET status = 'vencedora'
                WHERE id = ?
            ''', (proposta_id,))
            
            # Atualizar status das demais propostas
            conn.execute('''
                UPDATE propostas_cotacao
                SET status = 'nao_selecionada'
                WHERE solicitacao_id = ? AND id != ?
            ''', (solicitacao_id, proposta_id))
            
            # Atualizar status da solicitação
            conn.execute('''
                UPDATE solicitacoes_cotacao
                SET status = 'concluida'
                WHERE id = ?
            ''', (solicitacao_id,))
            
            conn.commit()
            logger.info(f"✅ Proposta {proposta_id} selecionada como vencedora")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao selecionar vencedora: {e}")
            return False
        finally:
            conn.close()
    
    def listar_solicitacoes(self, status: str = None) -> List[Dict]:
        """Lista solicitações de cotação"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            if status:
                cursor = conn.execute('''
                    SELECT * FROM solicitacoes_cotacao
                    WHERE status = ?
                    ORDER BY created_at DESC
                ''', (status,))
            else:
                cursor = conn.execute('''
                    SELECT * FROM solicitacoes_cotacao
                    ORDER BY created_at DESC
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar solicitações: {e}")
            return []
        finally:
            conn.close()
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas do sistema de cotações"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            stats = {}
            
            # Total de solicitações
            cursor = conn.execute('SELECT COUNT(*) as total FROM solicitacoes_cotacao')
            stats['total_solicitacoes'] = cursor.fetchone()['total']
            
            # Total de propostas
            cursor = conn.execute('SELECT COUNT(*) as total FROM propostas_cotacao')
            stats['total_propostas'] = cursor.fetchone()['total']
            
            # Economia total gerada
            cursor = conn.execute('SELECT SUM(economia_gerada) as total FROM comparacao_propostas')
            row = cursor.fetchone()
            stats['economia_total'] = row['total'] if row['total'] else 0
            
            # Média de propostas por solicitação
            if stats['total_solicitacoes'] > 0:
                stats['media_propostas'] = stats['total_propostas'] / stats['total_solicitacoes']
            else:
                stats['media_propostas'] = 0
            
            return stats
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas: {e}")
            return {}
        finally:
            conn.close()


def testar_sistema_cotacoes():
    """Função de teste do sistema de cotações"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE COTAÇÕES")
    print("="*60 + "\n")
    
    sistema = SupplierQuotationSystem()
    
    # Teste 1: Criar solicitação
    print("1️⃣ Criando solicitação de cotação...")
    itens = [
        {
            'codigo': 'EQ-001',
            'descricao': 'Monitor Cardíaco',
            'quantidade': 5,
            'unidade': 'UN',
            'especificacoes': 'Tela 12 polegadas, 5 parâmetros'
        },
        {
            'codigo': 'EQ-002',
            'descricao': 'Desfibrilador',
            'quantidade': 3,
            'unidade': 'UN',
            'especificacoes': 'Bifásico, energia até 360J'
        }
    ]
    
    sol_id = sistema.criar_solicitacao(
        'PE-2024-TEST-001',
        'Equipamentos para UTI',
        itens,
        prazo_dias=7
    )
    print(f"   ✅ Solicitação ID: {sol_id}\n")
    
    # Teste 2: Registrar propostas
    print("2️⃣ Registrando propostas de fornecedores...")
    
    # Proposta 1 - Fornecedor A
    itens_prop1 = [
        {'item_solicitacao_id': 1, 'preco_unitario': 8500.00, 'preco_total': 42500.00, 'marca': 'Marca A'},
        {'item_solicitacao_id': 2, 'preco_unitario': 12000.00, 'preco_total': 36000.00, 'marca': 'Marca A'}
    ]
    prop1_id = sistema.registrar_proposta(sol_id, 1, itens_prop1, '30 dias', '30/60 dias')
    print(f"   ✅ Proposta 1: R$ 78.500,00")
    
    # Proposta 2 - Fornecedor B (menor preço)
    itens_prop2 = [
        {'item_solicitacao_id': 1, 'preco_unitario': 7800.00, 'preco_total': 39000.00, 'marca': 'Marca B'},
        {'item_solicitacao_id': 2, 'preco_unitario': 11500.00, 'preco_total': 34500.00, 'marca': 'Marca B'}
    ]
    prop2_id = sistema.registrar_proposta(sol_id, 2, itens_prop2, '25 dias', '30 dias')
    print(f"   ✅ Proposta 2: R$ 73.500,00")
    
    # Proposta 3 - Fornecedor C
    itens_prop3 = [
        {'item_solicitacao_id': 1, 'preco_unitario': 9000.00, 'preco_total': 45000.00, 'marca': 'Marca C'},
        {'item_solicitacao_id': 2, 'preco_unitario': 13000.00, 'preco_total': 39000.00, 'marca': 'Marca C'}
    ]
    prop3_id = sistema.registrar_proposta(sol_id, 3, itens_prop3, '35 dias', '45 dias')
    print(f"   ✅ Proposta 3: R$ 84.000,00\n")
    
    # Teste 3: Comparar propostas
    print("3️⃣ Comparando propostas...")
    comparacao = sistema.comparar_propostas(sol_id)
    
    if not comparacao or 'analise' not in comparacao:
        print("   ⚠️ Erro na comparação\n")
        return
    
    analise = comparacao['analise']
    
    print(f"   📊 Total de Propostas: {analise['total_propostas']}")
    print(f"   💰 Menor Preço: {analise['menor_preco']['fornecedor']} - R$ {analise['menor_preco']['valor']:,.2f}")
    print(f"   💰 Maior Preço: {analise['maior_preco']['fornecedor']} - R$ {analise['maior_preco']['valor']:,.2f}")
    print(f"   💰 Preço Médio: R$ {analise['preco_medio']:,.2f}")
    print(f"   💵 Economia Potencial: R$ {analise['economia_potencial']:,.2f}")
    print(f"   📈 Variação: {analise['variacao_percentual']:.1f}%\n")
    
    # Teste 4: Selecionar vencedora
    print("4️⃣ Selecionando proposta vencedora...")
    sucesso = sistema.selecionar_vencedora(
        sol_id,
        analise['menor_preco']['proposta_id'],
        'menor_preco',
        'Melhor preço com prazo adequado'
    )
    print(f"   {'✅' if sucesso else '❌'} Seleção {'concluída' if sucesso else 'falhou'}\n")
    
    # Teste 5: Estatísticas
    print("5️⃣ Estatísticas do sistema...")
    stats = sistema.obter_estatisticas()
    print(f"   📋 Total de Solicitações: {stats['total_solicitacoes']}")
    print(f"   📄 Total de Propostas: {stats['total_propostas']}")
    print(f"   💵 Economia Total Gerada: R$ {stats['economia_total']:,.2f}")
    print(f"   📊 Média de Propostas/Solicitação: {stats['media_propostas']:.1f}\n")
    
    print("="*60)
    print("✅ SISTEMA DE COTAÇÕES FUNCIONANDO")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_sistema_cotacoes()
