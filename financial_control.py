"""
Sistema de Controle Financeiro
Gestão de receitas, despesas, fluxo de caixa e relatórios financeiros

Desenvolvido em 01/12/2025
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinancialControl:
    """
    Sistema completo de controle financeiro
    """
    
    def __init__(self, db_path='hospshop.db'):
        self.db_path = db_path
        self.init_tables()
    
    def get_db_connection(self):
        """Retorna conexão com banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return None
    
    def init_tables(self):
        """Cria tabelas financeiras"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Tabela de receitas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS receitas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data_recebimento TEXT NOT NULL,
                    data_prevista TEXT,
                    categoria TEXT NOT NULL,
                    contrato_id INTEGER,
                    forma_recebimento TEXT,
                    status TEXT DEFAULT 'prevista',
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de despesas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS despesas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor REAL NOT NULL,
                    data_pagamento TEXT NOT NULL,
                    data_vencimento TEXT,
                    categoria TEXT NOT NULL,
                    fornecedor_id INTEGER,
                    forma_pagamento TEXT,
                    status TEXT DEFAULT 'pendente',
                    numero_documento TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de categorias
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categorias_financeiras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE NOT NULL,
                    tipo TEXT NOT NULL,
                    descricao TEXT,
                    ativo BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tabela de fluxo de caixa
            conn.execute('''
                CREATE TABLE IF NOT EXISTS fluxo_caixa (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    valor REAL NOT NULL,
                    saldo_anterior REAL NOT NULL,
                    saldo_atual REAL NOT NULL,
                    descricao TEXT,
                    referencia_id INTEGER,
                    referencia_tipo TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de metas financeiras
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metas_financeiras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    descricao TEXT NOT NULL,
                    valor_meta REAL NOT NULL,
                    periodo_inicio TEXT NOT NULL,
                    periodo_fim TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    status TEXT DEFAULT 'ativa',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tabelas financeiras criadas/verificadas")
            
            # Criar categorias padrão
            self._criar_categorias_padrao(conn)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            conn.close()
    
    def _criar_categorias_padrao(self, conn):
        """Cria categorias financeiras padrão"""
        categorias = [
            ('Licitações Ganhas', 'receita', 'Receitas de licitações vencidas'),
            ('Contratos Firmados', 'receita', 'Receitas de contratos assinados'),
            ('Fornecimento de Produtos', 'despesa', 'Compra de produtos para revenda'),
            ('Salários e Encargos', 'despesa', 'Folha de pagamento'),
            ('Impostos e Taxas', 'despesa', 'Tributos e taxas governamentais'),
            ('Despesas Operacionais', 'despesa', 'Despesas gerais de operação'),
            ('Investimentos', 'despesa', 'Investimentos em equipamentos e infraestrutura'),
        ]
        
        for nome, tipo, descricao in categorias:
            try:
                conn.execute('''
                    INSERT OR IGNORE INTO categorias_financeiras (nome, tipo, descricao)
                    VALUES (?, ?, ?)
                ''', (nome, tipo, descricao))
            except:
                pass
        
        conn.commit()
    
    def registrar_receita(self, dados: Dict) -> Optional[int]:
        """
        Registra nova receita
        
        Args:
            dados: Dicionário com dados da receita
            
        Returns:
            ID da receita ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.execute('''
                INSERT INTO receitas 
                (descricao, valor, data_recebimento, data_prevista, categoria, 
                 contrato_id, forma_recebimento, status, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['descricao'],
                dados['valor'],
                dados.get('data_recebimento', datetime.now().isoformat()),
                dados.get('data_prevista'),
                dados['categoria'],
                dados.get('contrato_id'),
                dados.get('forma_recebimento', 'transferencia'),
                dados.get('status', 'prevista'),
                dados.get('observacoes', '')
            ))
            
            receita_id = cursor.lastrowid
            
            # Atualizar fluxo de caixa se recebida
            if dados.get('status') == 'recebida':
                self._atualizar_fluxo_caixa(
                    'receita',
                    dados['valor'],
                    dados['descricao'],
                    receita_id,
                    'receita'
                )
            
            conn.commit()
            logger.info(f"✅ Receita registrada: R$ {dados['valor']:,.2f}")
            return receita_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar receita: {e}")
            return None
        finally:
            conn.close()
    
    def registrar_despesa(self, dados: Dict) -> Optional[int]:
        """
        Registra nova despesa
        
        Args:
            dados: Dicionário com dados da despesa
            
        Returns:
            ID da despesa ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.execute('''
                INSERT INTO despesas
                (descricao, valor, data_pagamento, data_vencimento, categoria,
                 fornecedor_id, forma_pagamento, status, numero_documento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dados['descricao'],
                dados['valor'],
                dados.get('data_pagamento', datetime.now().isoformat()),
                dados.get('data_vencimento'),
                dados['categoria'],
                dados.get('fornecedor_id'),
                dados.get('forma_pagamento', 'transferencia'),
                dados.get('status', 'pendente'),
                dados.get('numero_documento', ''),
                dados.get('observacoes', '')
            ))
            
            despesa_id = cursor.lastrowid
            
            # Atualizar fluxo de caixa se paga
            if dados.get('status') == 'paga':
                self._atualizar_fluxo_caixa(
                    'despesa',
                    dados['valor'],
                    dados['descricao'],
                    despesa_id,
                    'despesa'
                )
            
            conn.commit()
            logger.info(f"✅ Despesa registrada: R$ {dados['valor']:,.2f}")
            return despesa_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar despesa: {e}")
            return None
        finally:
            conn.close()
    
    def _atualizar_fluxo_caixa(self, tipo: str, valor: float, descricao: str, 
                               ref_id: int, ref_tipo: str):
        """Atualiza fluxo de caixa"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            # Obter saldo anterior
            cursor = conn.execute('''
                SELECT saldo_atual FROM fluxo_caixa
                ORDER BY created_at DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            saldo_anterior = row['saldo_atual'] if row else 0
            
            # Calcular novo saldo
            if tipo == 'receita':
                saldo_atual = saldo_anterior + valor
            else:
                saldo_atual = saldo_anterior - valor
            
            # Inserir movimento
            conn.execute('''
                INSERT INTO fluxo_caixa
                (data, tipo, valor, saldo_anterior, saldo_atual, descricao, 
                 referencia_id, referencia_tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                tipo,
                valor,
                saldo_anterior,
                saldo_atual,
                descricao,
                ref_id,
                ref_tipo
            ))
            
            conn.commit()
            logger.info(f"✅ Fluxo de caixa atualizado: R$ {saldo_atual:,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar fluxo: {e}")
        finally:
            conn.close()
    
    def obter_saldo_atual(self) -> float:
        """Retorna saldo atual do caixa"""
        conn = self.get_db_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.execute('''
                SELECT saldo_atual FROM fluxo_caixa
                ORDER BY created_at DESC LIMIT 1
            ''')
            row = cursor.fetchone()
            return row['saldo_atual'] if row else 0
        except:
            return 0
        finally:
            conn.close()
    
    def relatorio_periodo(self, data_inicio: str, data_fim: str) -> Dict:
        """
        Gera relatório financeiro de período
        
        Args:
            data_inicio: Data inicial (YYYY-MM-DD)
            data_fim: Data final (YYYY-MM-DD)
            
        Returns:
            Dicionário com relatório
        """
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Receitas do período
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM receitas
                WHERE data_recebimento BETWEEN ? AND ?
                AND status = 'recebida'
            ''', (data_inicio, data_fim))
            total_receitas = cursor.fetchone()['total'] or 0
            
            # Despesas do período
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM despesas
                WHERE data_pagamento BETWEEN ? AND ?
                AND status = 'paga'
            ''', (data_inicio, data_fim))
            total_despesas = cursor.fetchone()['total'] or 0
            
            # Receitas por categoria
            cursor = conn.execute('''
                SELECT categoria, SUM(valor) as total
                FROM receitas
                WHERE data_recebimento BETWEEN ? AND ?
                AND status = 'recebida'
                GROUP BY categoria
            ''', (data_inicio, data_fim))
            receitas_por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
            
            # Despesas por categoria
            cursor = conn.execute('''
                SELECT categoria, SUM(valor) as total
                FROM despesas
                WHERE data_pagamento BETWEEN ? AND ?
                AND status = 'paga'
                GROUP BY categoria
            ''', (data_inicio, data_fim))
            despesas_por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
            
            # Resultado
            resultado = total_receitas - total_despesas
            
            relatorio = {
                'periodo': {
                    'inicio': data_inicio,
                    'fim': data_fim
                },
                'resumo': {
                    'total_receitas': total_receitas,
                    'total_despesas': total_despesas,
                    'resultado': resultado,
                    'margem': (resultado / total_receitas * 100) if total_receitas > 0 else 0
                },
                'receitas_por_categoria': receitas_por_categoria,
                'despesas_por_categoria': despesas_por_categoria,
                'saldo_atual': self.obter_saldo_atual()
            }
            
            logger.info(f"✅ Relatório gerado: Resultado R$ {resultado:,.2f}")
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
        finally:
            conn.close()
    
    def contas_a_receber(self) -> List[Dict]:
        """Lista contas a receber (receitas previstas)"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM receitas
                WHERE status = 'prevista'
                ORDER BY data_prevista ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def contas_a_pagar(self) -> List[Dict]:
        """Lista contas a pagar (despesas pendentes)"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM despesas
                WHERE status = 'pendente'
                ORDER BY data_vencimento ASC
            ''')
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas financeiras"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            stats = {}
            
            # Saldo atual
            stats['saldo_atual'] = self.obter_saldo_atual()
            
            # Total a receber
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM receitas WHERE status = 'prevista'
            ''')
            stats['total_a_receber'] = cursor.fetchone()['total'] or 0
            
            # Total a pagar
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM despesas WHERE status = 'pendente'
            ''')
            stats['total_a_pagar'] = cursor.fetchone()['total'] or 0
            
            # Projeção de saldo
            stats['projecao_saldo'] = (
                stats['saldo_atual'] + 
                stats['total_a_receber'] - 
                stats['total_a_pagar']
            )
            
            return stats
        except:
            return {}
        finally:
            conn.close()


def testar_financial_control():
    """Função de teste do controle financeiro"""
    print("\n" + "="*60)
    print("🧪 TESTE DE CONTROLE FINANCEIRO")
    print("="*60 + "\n")
    
    sistema = FinancialControl()
    
    # Teste 1: Registrar receitas
    print("1️⃣ Registrando receitas...")
    receitas = [
        {
            'descricao': 'Licitação PE-2024-001 - Hospital Municipal',
            'valor': 113500.00,
            'categoria': 'Licitações Ganhas',
            'status': 'recebida',
            'forma_recebimento': 'transferencia'
        },
        {
            'descricao': 'Contrato CONT-2024-002 - Prefeitura',
            'valor': 85000.00,
            'categoria': 'Contratos Firmados',
            'status': 'prevista',
            'data_prevista': '2024-12-15'
        }
    ]
    
    for rec in receitas:
        sistema.registrar_receita(rec)
    print(f"   ✅ {len(receitas)} receitas registradas\n")
    
    # Teste 2: Registrar despesas
    print("2️⃣ Registrando despesas...")
    despesas = [
        {
            'descricao': 'Compra de equipamentos - Fornecedor A',
            'valor': 78500.00,
            'categoria': 'Fornecimento de Produtos',
            'status': 'paga',
            'forma_pagamento': 'transferencia'
        },
        {
            'descricao': 'Folha de pagamento - Dezembro/2024',
            'valor': 15000.00,
            'categoria': 'Salários e Encargos',
            'status': 'pendente',
            'data_vencimento': '2024-12-05'
        }
    ]
    
    for desp in despesas:
        sistema.registrar_despesa(desp)
    print(f"   ✅ {len(despesas)} despesas registradas\n")
    
    # Teste 3: Saldo atual
    print("3️⃣ Verificando saldo...")
    saldo = sistema.obter_saldo_atual()
    print(f"   💰 Saldo Atual: R$ {saldo:,.2f}\n")
    
    # Teste 4: Contas a receber
    print("4️⃣ Contas a receber...")
    a_receber = sistema.contas_a_receber()
    print(f"   📊 Total: {len(a_receber)} contas")
    for conta in a_receber:
        print(f"   • R$ {conta['valor']:,.2f} - {conta['descricao'][:50]}")
    print()
    
    # Teste 5: Contas a pagar
    print("5️⃣ Contas a pagar...")
    a_pagar = sistema.contas_a_pagar()
    print(f"   📊 Total: {len(a_pagar)} contas")
    for conta in a_pagar:
        print(f"   • R$ {conta['valor']:,.2f} - {conta['descricao'][:50]}")
    print()
    
    # Teste 6: Relatório do período
    print("6️⃣ Gerando relatório do período...")
    relatorio = sistema.relatorio_periodo('2024-12-01', '2024-12-31')
    print(f"   💰 Receitas: R$ {relatorio['resumo']['total_receitas']:,.2f}")
    print(f"   💸 Despesas: R$ {relatorio['resumo']['total_despesas']:,.2f}")
    print(f"   📈 Resultado: R$ {relatorio['resumo']['resultado']:,.2f}")
    print(f"   📊 Margem: {relatorio['resumo']['margem']:.1f}%\n")
    
    # Teste 7: Estatísticas
    print("7️⃣ Estatísticas financeiras...")
    stats = sistema.obter_estatisticas()
    print(f"   💰 Saldo Atual: R$ {stats['saldo_atual']:,.2f}")
    print(f"   📥 A Receber: R$ {stats['total_a_receber']:,.2f}")
    print(f"   📤 A Pagar: R$ {stats['total_a_pagar']:,.2f}")
    print(f"   🔮 Projeção: R$ {stats['projecao_saldo']:,.2f}\n")
    
    print("="*60)
    print("✅ SISTEMA FINANCEIRO FUNCIONANDO")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_financial_control()
