"""
Sistema de Rastreamento de Pagamentos
Controle completo de pagamentos, parcelas e histórico

Desenvolvido em 01/12/2025
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PaymentTracking:
    """
    Sistema de rastreamento de pagamentos
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
        """Cria tabelas de pagamentos"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Tabela de pagamentos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_pagamento TEXT UNIQUE NOT NULL,
                    contrato_id INTEGER,
                    fornecedor_id INTEGER,
                    descricao TEXT NOT NULL,
                    valor_total REAL NOT NULL,
                    numero_parcelas INTEGER DEFAULT 1,
                    forma_pagamento TEXT NOT NULL,
                    status TEXT DEFAULT 'pendente',
                    data_criacao TEXT NOT NULL,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de parcelas
            conn.execute('''
                CREATE TABLE IF NOT EXISTS parcelas_pagamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pagamento_id INTEGER NOT NULL,
                    numero_parcela INTEGER NOT NULL,
                    valor_parcela REAL NOT NULL,
                    data_vencimento TEXT NOT NULL,
                    data_pagamento TEXT,
                    valor_pago REAL,
                    juros REAL DEFAULT 0,
                    multa REAL DEFAULT 0,
                    desconto REAL DEFAULT 0,
                    status TEXT DEFAULT 'pendente',
                    comprovante_path TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pagamento_id) REFERENCES pagamentos(id)
                )
            ''')
            
            # Tabela de histórico de pagamentos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS historico_pagamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parcela_id INTEGER NOT NULL,
                    acao TEXT NOT NULL,
                    usuario TEXT,
                    data_acao TEXT NOT NULL,
                    detalhes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parcela_id) REFERENCES parcelas_pagamento(id)
                )
            ''')
            
            # Tabela de alertas de pagamento
            conn.execute('''
                CREATE TABLE IF NOT EXISTS alertas_pagamento (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parcela_id INTEGER NOT NULL,
                    tipo_alerta TEXT NOT NULL,
                    data_alerta TEXT NOT NULL,
                    enviado BOOLEAN DEFAULT 0,
                    data_envio TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parcela_id) REFERENCES parcelas_pagamento(id)
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tabelas de pagamentos criadas/verificadas")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            conn.close()
    
    def criar_pagamento(self, dados: Dict) -> Optional[int]:
        """
        Cria novo pagamento com parcelas
        
        Args:
            dados: Dicionário com dados do pagamento
            
        Returns:
            ID do pagamento ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            # Gerar número do pagamento
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            numero_pagamento = f"PAG-{timestamp}"
            
            # Inserir pagamento
            cursor = conn.execute('''
                INSERT INTO pagamentos
                (numero_pagamento, contrato_id, fornecedor_id, descricao, valor_total,
                 numero_parcelas, forma_pagamento, data_criacao, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_pagamento,
                dados.get('contrato_id'),
                dados.get('fornecedor_id'),
                dados['descricao'],
                dados['valor_total'],
                dados.get('numero_parcelas', 1),
                dados['forma_pagamento'],
                datetime.now().isoformat(),
                dados.get('observacoes', '')
            ))
            
            pagamento_id = cursor.lastrowid
            
            # Criar parcelas
            self._criar_parcelas(
                conn,
                pagamento_id,
                dados['valor_total'],
                dados.get('numero_parcelas', 1),
                dados.get('data_primeiro_vencimento', datetime.now().isoformat())
            )
            
            conn.commit()
            logger.info(f"✅ Pagamento {numero_pagamento} criado com {dados.get('numero_parcelas', 1)} parcelas")
            return pagamento_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pagamento: {e}")
            return None
        finally:
            conn.close()
    
    def _criar_parcelas(self, conn, pagamento_id: int, valor_total: float, 
                       num_parcelas: int, data_primeiro_vencimento: str):
        """Cria parcelas do pagamento"""
        valor_parcela = valor_total / num_parcelas
        data_vencimento = datetime.fromisoformat(data_primeiro_vencimento)
        
        for i in range(1, num_parcelas + 1):
            conn.execute('''
                INSERT INTO parcelas_pagamento
                (pagamento_id, numero_parcela, valor_parcela, data_vencimento)
                VALUES (?, ?, ?, ?)
            ''', (
                pagamento_id,
                i,
                valor_parcela,
                data_vencimento.isoformat()
            ))
            
            # Próximo vencimento (30 dias depois)
            data_vencimento += timedelta(days=30)
    
    def registrar_pagamento_parcela(self, parcela_id: int, dados: Dict) -> bool:
        """
        Registra pagamento de uma parcela
        
        Args:
            parcela_id: ID da parcela
            dados: Dados do pagamento (valor_pago, data_pagamento, etc)
            
        Returns:
            True se sucesso, False caso contrário
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Atualizar parcela
            conn.execute('''
                UPDATE parcelas_pagamento
                SET data_pagamento = ?,
                    valor_pago = ?,
                    juros = ?,
                    multa = ?,
                    desconto = ?,
                    status = 'paga',
                    comprovante_path = ?,
                    observacoes = ?
                WHERE id = ?
            ''', (
                dados.get('data_pagamento', datetime.now().isoformat()),
                dados['valor_pago'],
                dados.get('juros', 0),
                dados.get('multa', 0),
                dados.get('desconto', 0),
                dados.get('comprovante_path', ''),
                dados.get('observacoes', ''),
                parcela_id
            ))
            
            # Registrar no histórico
            conn.execute('''
                INSERT INTO historico_pagamentos
                (parcela_id, acao, usuario, data_acao, detalhes)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                parcela_id,
                'pagamento_realizado',
                dados.get('usuario', 'sistema'),
                datetime.now().isoformat(),
                f"Valor pago: R$ {dados['valor_pago']:.2f}"
            ))
            
            # Verificar se todas as parcelas foram pagas
            cursor = conn.execute('''
                SELECT COUNT(*) as total,
                       SUM(CASE WHEN status = 'paga' THEN 1 ELSE 0 END) as pagas
                FROM parcelas_pagamento
                WHERE pagamento_id = (
                    SELECT pagamento_id FROM parcelas_pagamento WHERE id = ?
                )
            ''', (parcela_id,))
            
            row = cursor.fetchone()
            if row['total'] == row['pagas']:
                # Atualizar status do pagamento principal
                conn.execute('''
                    UPDATE pagamentos
                    SET status = 'pago'
                    WHERE id = (SELECT pagamento_id FROM parcelas_pagamento WHERE id = ?)
                ''', (parcela_id,))
            
            conn.commit()
            logger.info(f"✅ Parcela {parcela_id} paga: R$ {dados['valor_pago']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar pagamento: {e}")
            return False
        finally:
            conn.close()
    
    def listar_parcelas_vencendo(self, dias: int = 7) -> List[Dict]:
        """
        Lista parcelas que vencem nos próximos X dias
        
        Args:
            dias: Número de dias para considerar
            
        Returns:
            Lista de parcelas
        """
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            data_limite = (datetime.now() + timedelta(days=dias)).isoformat()
            
            cursor = conn.execute('''
                SELECT p.*, pag.numero_pagamento, pag.descricao as pagamento_descricao
                FROM parcelas_pagamento p
                JOIN pagamentos pag ON p.pagamento_id = pag.id
                WHERE p.status = 'pendente'
                AND p.data_vencimento <= ?
                ORDER BY p.data_vencimento ASC
            ''', (data_limite,))
            
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Erro ao listar parcelas: {e}")
            return []
        finally:
            conn.close()
    
    def listar_parcelas_vencidas(self) -> List[Dict]:
        """Lista parcelas vencidas e não pagas"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            hoje = datetime.now().isoformat()
            
            cursor = conn.execute('''
                SELECT p.*, pag.numero_pagamento, pag.descricao as pagamento_descricao
                FROM parcelas_pagamento p
                JOIN pagamentos pag ON p.pagamento_id = pag.id
                WHERE p.status = 'pendente'
                AND p.data_vencimento < ?
                ORDER BY p.data_vencimento ASC
            ''', (hoje,))
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def obter_historico_parcela(self, parcela_id: int) -> List[Dict]:
        """Retorna histórico de uma parcela"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM historico_pagamentos
                WHERE parcela_id = ?
                ORDER BY created_at DESC
            ''', (parcela_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def criar_alerta_vencimento(self, parcela_id: int, dias_antecedencia: int = 3):
        """Cria alerta de vencimento para parcela"""
        conn = self.get_db_connection()
        if not conn:
            return
        
        try:
            # Obter data de vencimento
            cursor = conn.execute('''
                SELECT data_vencimento FROM parcelas_pagamento WHERE id = ?
            ''', (parcela_id,))
            row = cursor.fetchone()
            
            if row:
                data_vencimento = datetime.fromisoformat(row['data_vencimento'])
                data_alerta = data_vencimento - timedelta(days=dias_antecedencia)
                
                conn.execute('''
                    INSERT INTO alertas_pagamento
                    (parcela_id, tipo_alerta, data_alerta)
                    VALUES (?, ?, ?)
                ''', (parcela_id, 'vencimento_proximo', data_alerta.isoformat()))
                
                conn.commit()
                logger.info(f"✅ Alerta criado para parcela {parcela_id}")
        except Exception as e:
            logger.error(f"Erro ao criar alerta: {e}")
        finally:
            conn.close()
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas de pagamentos"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            stats = {}
            
            # Total de pagamentos
            cursor = conn.execute('SELECT COUNT(*) as total FROM pagamentos')
            stats['total_pagamentos'] = cursor.fetchone()['total']
            
            # Total de parcelas
            cursor = conn.execute('SELECT COUNT(*) as total FROM parcelas_pagamento')
            stats['total_parcelas'] = cursor.fetchone()['total']
            
            # Parcelas pagas
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM parcelas_pagamento WHERE status = 'paga'
            ''')
            stats['parcelas_pagas'] = cursor.fetchone()['total']
            
            # Parcelas pendentes
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM parcelas_pagamento WHERE status = 'pendente'
            ''')
            stats['parcelas_pendentes'] = cursor.fetchone()['total']
            
            # Valor total pago
            cursor = conn.execute('''
                SELECT SUM(valor_pago) as total FROM parcelas_pagamento WHERE status = 'paga'
            ''')
            stats['valor_total_pago'] = cursor.fetchone()['total'] or 0
            
            # Valor total pendente
            cursor = conn.execute('''
                SELECT SUM(valor_parcela) as total FROM parcelas_pagamento WHERE status = 'pendente'
            ''')
            stats['valor_total_pendente'] = cursor.fetchone()['total'] or 0
            
            return stats
        except:
            return {}
        finally:
            conn.close()


def testar_payment_tracking():
    """Função de teste do sistema de pagamentos"""
    print("\n" + "="*60)
    print("🧪 TESTE DE RASTREAMENTO DE PAGAMENTOS")
    print("="*60 + "\n")
    
    sistema = PaymentTracking()
    
    # Teste 1: Criar pagamento parcelado
    print("1️⃣ Criando pagamento parcelado...")
    dados_pagamento = {
        'contrato_id': 1,
        'fornecedor_id': 1,
        'descricao': 'Fornecimento de equipamentos hospitalares',
        'valor_total': 113500.00,
        'numero_parcelas': 3,
        'forma_pagamento': 'transferencia',
        'data_primeiro_vencimento': '2024-12-15',
        'observacoes': 'Pagamento conforme contrato CONT-2024-001'
    }
    
    pag_id = sistema.criar_pagamento(dados_pagamento)
    print(f"   ✅ Pagamento criado: ID {pag_id}\n")
    
    # Teste 2: Registrar pagamento de parcela
    print("2️⃣ Registrando pagamento da 1ª parcela...")
    dados_parcela = {
        'valor_pago': 37833.33,
        'data_pagamento': '2024-12-15',
        'juros': 0,
        'multa': 0,
        'desconto': 0,
        'usuario': 'admin',
        'observacoes': 'Pagamento em dia'
    }
    
    sucesso = sistema.registrar_pagamento_parcela(1, dados_parcela)
    print(f"   {'✅' if sucesso else '❌'} Parcela {'paga' if sucesso else 'falhou'}\n")
    
    # Teste 3: Parcelas vencendo
    print("3️⃣ Verificando parcelas vencendo (próximos 30 dias)...")
    vencendo = sistema.listar_parcelas_vencendo(30)
    print(f"   📊 Total: {len(vencendo)} parcelas")
    for parcela in vencendo:
        print(f"   • Parcela {parcela['numero_parcela']}: R$ {parcela['valor_parcela']:,.2f} - Venc: {parcela['data_vencimento'][:10]}")
    print()
    
    # Teste 4: Parcelas vencidas
    print("4️⃣ Verificando parcelas vencidas...")
    vencidas = sistema.listar_parcelas_vencidas()
    print(f"   📊 Total: {len(vencidas)} parcelas vencidas\n")
    
    # Teste 5: Histórico da parcela
    print("5️⃣ Consultando histórico da parcela 1...")
    historico = sistema.obter_historico_parcela(1)
    print(f"   📜 Total de registros: {len(historico)}")
    for reg in historico:
        print(f"   • {reg['acao']} - {reg['data_acao'][:10]} - {reg['detalhes']}")
    print()
    
    # Teste 6: Criar alertas
    print("6️⃣ Criando alertas de vencimento...")
    sistema.criar_alerta_vencimento(2, dias_antecedencia=3)
    sistema.criar_alerta_vencimento(3, dias_antecedencia=3)
    print(f"   ✅ Alertas criados\n")
    
    # Teste 7: Estatísticas
    print("7️⃣ Estatísticas de pagamentos...")
    stats = sistema.obter_estatisticas()
    print(f"   📊 Total de Pagamentos: {stats['total_pagamentos']}")
    print(f"   📊 Total de Parcelas: {stats['total_parcelas']}")
    print(f"   ✅ Parcelas Pagas: {stats['parcelas_pagas']}")
    print(f"   ⏳ Parcelas Pendentes: {stats['parcelas_pendentes']}")
    print(f"   💰 Valor Pago: R$ {stats['valor_total_pago']:,.2f}")
    print(f"   💸 Valor Pendente: R$ {stats['valor_total_pendente']:,.2f}\n")
    
    print("="*60)
    print("✅ SISTEMA DE PAGAMENTOS FUNCIONANDO")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_payment_tracking()
