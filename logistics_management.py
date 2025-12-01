"""
Sistema de Gestão de Logística
Rastreamento de entregas, agendamentos e status de pedidos

Desenvolvido em 01/12/2025
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogisticsManagement:
    """
    Sistema de gestão de logística e entregas
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
        """Cria tabelas de logística"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Tabela de pedidos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pedidos_entrega (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_pedido TEXT UNIQUE NOT NULL,
                    contrato_id INTEGER,
                    fornecedor_id INTEGER,
                    descricao TEXT NOT NULL,
                    quantidade_itens INTEGER NOT NULL,
                    peso_total REAL,
                    volume_total REAL,
                    endereco_entrega TEXT NOT NULL,
                    cidade TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    cep TEXT NOT NULL,
                    contato_recebimento TEXT,
                    telefone_contato TEXT,
                    status TEXT DEFAULT 'aguardando_envio',
                    prioridade TEXT DEFAULT 'normal',
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de agendamentos
            conn.execute('''
                CREATE TABLE IF NOT EXISTS agendamentos_entrega (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    data_agendada TEXT NOT NULL,
                    horario_inicio TEXT NOT NULL,
                    horario_fim TEXT NOT NULL,
                    tipo_veiculo TEXT,
                    motorista TEXT,
                    placa_veiculo TEXT,
                    status TEXT DEFAULT 'agendado',
                    confirmado BOOLEAN DEFAULT 0,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos_entrega(id)
                )
            ''')
            
            # Tabela de rastreamento
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rastreamento_entrega (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    localizacao TEXT,
                    data_hora TEXT NOT NULL,
                    responsavel TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos_entrega(id)
                )
            ''')
            
            # Tabela de comprovantes
            conn.execute('''
                CREATE TABLE IF NOT EXISTS comprovantes_entrega (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id INTEGER NOT NULL,
                    tipo_comprovante TEXT NOT NULL,
                    arquivo_path TEXT NOT NULL,
                    data_upload TEXT NOT NULL,
                    recebedor_nome TEXT,
                    recebedor_documento TEXT,
                    observacoes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos_entrega(id)
                )
            ''')
            
            conn.commit()
            logger.info("✅ Tabelas de logística criadas/verificadas")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar tabelas: {e}")
            return False
        finally:
            conn.close()
    
    def criar_pedido(self, dados: Dict) -> Optional[int]:
        """
        Cria novo pedido de entrega
        
        Args:
            dados: Dados do pedido
            
        Returns:
            ID do pedido ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            # Gerar número do pedido
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            numero_pedido = f"PED-{timestamp}"
            
            cursor = conn.execute('''
                INSERT INTO pedidos_entrega
                (numero_pedido, contrato_id, fornecedor_id, descricao, quantidade_itens,
                 peso_total, volume_total, endereco_entrega, cidade, estado, cep,
                 contato_recebimento, telefone_contato, prioridade, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                numero_pedido,
                dados.get('contrato_id'),
                dados.get('fornecedor_id'),
                dados['descricao'],
                dados['quantidade_itens'],
                dados.get('peso_total', 0),
                dados.get('volume_total', 0),
                dados['endereco_entrega'],
                dados['cidade'],
                dados['estado'],
                dados['cep'],
                dados.get('contato_recebimento', ''),
                dados.get('telefone_contato', ''),
                dados.get('prioridade', 'normal'),
                dados.get('observacoes', '')
            ))
            
            pedido_id = cursor.lastrowid
            
            # Registrar status inicial
            self._registrar_rastreamento(
                conn,
                pedido_id,
                'pedido_criado',
                'Sistema',
                'Pedido criado e aguardando processamento'
            )
            
            conn.commit()
            logger.info(f"✅ Pedido {numero_pedido} criado")
            return pedido_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar pedido: {e}")
            return None
        finally:
            conn.close()
    
    def agendar_entrega(self, pedido_id: int, dados: Dict) -> Optional[int]:
        """
        Agenda entrega para um pedido
        
        Args:
            pedido_id: ID do pedido
            dados: Dados do agendamento
            
        Returns:
            ID do agendamento ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.execute('''
                INSERT INTO agendamentos_entrega
                (pedido_id, data_agendada, horario_inicio, horario_fim,
                 tipo_veiculo, motorista, placa_veiculo, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido_id,
                dados['data_agendada'],
                dados['horario_inicio'],
                dados['horario_fim'],
                dados.get('tipo_veiculo', ''),
                dados.get('motorista', ''),
                dados.get('placa_veiculo', ''),
                dados.get('observacoes', '')
            ))
            
            agendamento_id = cursor.lastrowid
            
            # Atualizar status do pedido
            conn.execute('''
                UPDATE pedidos_entrega
                SET status = 'agendado'
                WHERE id = ?
            ''', (pedido_id,))
            
            # Registrar rastreamento
            self._registrar_rastreamento(
                conn,
                pedido_id,
                'entrega_agendada',
                dados.get('motorista', 'Sistema'),
                f"Entrega agendada para {dados['data_agendada']} {dados['horario_inicio']}"
            )
            
            conn.commit()
            logger.info(f"✅ Entrega agendada para pedido {pedido_id}")
            return agendamento_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao agendar entrega: {e}")
            return None
        finally:
            conn.close()
    
    def atualizar_status_pedido(self, pedido_id: int, novo_status: str, 
                               localizacao: str = None, responsavel: str = 'Sistema',
                               observacoes: str = '') -> bool:
        """
        Atualiza status do pedido
        
        Args:
            pedido_id: ID do pedido
            novo_status: Novo status
            localizacao: Localização atual (opcional)
            responsavel: Responsável pela atualização
            observacoes: Observações
            
        Returns:
            True se sucesso, False caso contrário
        """
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            # Atualizar pedido
            conn.execute('''
                UPDATE pedidos_entrega
                SET status = ?
                WHERE id = ?
            ''', (novo_status, pedido_id))
            
            # Registrar rastreamento
            self._registrar_rastreamento(
                conn,
                pedido_id,
                novo_status,
                responsavel,
                observacoes,
                localizacao
            )
            
            conn.commit()
            logger.info(f"✅ Status atualizado: {novo_status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar status: {e}")
            return False
        finally:
            conn.close()
    
    def _registrar_rastreamento(self, conn, pedido_id: int, status: str,
                               responsavel: str, observacoes: str = '',
                               localizacao: str = None):
        """Registra evento de rastreamento"""
        conn.execute('''
            INSERT INTO rastreamento_entrega
            (pedido_id, status, localizacao, data_hora, responsavel, observacoes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            pedido_id,
            status,
            localizacao,
            datetime.now().isoformat(),
            responsavel,
            observacoes
        ))
    
    def registrar_comprovante(self, pedido_id: int, dados: Dict) -> Optional[int]:
        """
        Registra comprovante de entrega
        
        Args:
            pedido_id: ID do pedido
            dados: Dados do comprovante
            
        Returns:
            ID do comprovante ou None
        """
        conn = self.get_db_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.execute('''
                INSERT INTO comprovantes_entrega
                (pedido_id, tipo_comprovante, arquivo_path, data_upload,
                 recebedor_nome, recebedor_documento, observacoes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                pedido_id,
                dados['tipo_comprovante'],
                dados['arquivo_path'],
                datetime.now().isoformat(),
                dados.get('recebedor_nome', ''),
                dados.get('recebedor_documento', ''),
                dados.get('observacoes', '')
            ))
            
            comprovante_id = cursor.lastrowid
            
            # Atualizar status do pedido
            conn.execute('''
                UPDATE pedidos_entrega
                SET status = 'entregue'
                WHERE id = ?
            ''', (pedido_id,))
            
            # Registrar rastreamento
            self._registrar_rastreamento(
                conn,
                pedido_id,
                'entregue',
                dados.get('recebedor_nome', 'Recebedor'),
                f"Entrega confirmada. Documento: {dados.get('recebedor_documento', 'N/A')}"
            )
            
            conn.commit()
            logger.info(f"✅ Comprovante registrado para pedido {pedido_id}")
            return comprovante_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar comprovante: {e}")
            return None
        finally:
            conn.close()
    
    def obter_rastreamento(self, pedido_id: int) -> List[Dict]:
        """Retorna histórico de rastreamento do pedido"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM rastreamento_entrega
                WHERE pedido_id = ?
                ORDER BY created_at ASC
            ''', (pedido_id,))
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def listar_entregas_pendentes(self) -> List[Dict]:
        """Lista entregas pendentes"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT * FROM pedidos_entrega
                WHERE status NOT IN ('entregue', 'cancelado')
                ORDER BY prioridade DESC, created_at ASC
            ''')
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def listar_agendamentos_dia(self, data: str) -> List[Dict]:
        """Lista agendamentos de um dia específico"""
        conn = self.get_db_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.execute('''
                SELECT a.*, p.numero_pedido, p.endereco_entrega, p.cidade
                FROM agendamentos_entrega a
                JOIN pedidos_entrega p ON a.pedido_id = p.id
                WHERE a.data_agendada = ?
                ORDER BY a.horario_inicio ASC
            ''', (data,))
            
            return [dict(row) for row in cursor.fetchall()]
        except:
            return []
        finally:
            conn.close()
    
    def obter_estatisticas(self) -> Dict:
        """Retorna estatísticas de logística"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            stats = {}
            
            # Total de pedidos
            cursor = conn.execute('SELECT COUNT(*) as total FROM pedidos_entrega')
            stats['total_pedidos'] = cursor.fetchone()['total']
            
            # Pedidos por status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as total
                FROM pedidos_entrega
                GROUP BY status
            ''')
            stats['por_status'] = {row['status']: row['total'] for row in cursor.fetchall()}
            
            # Entregas do dia
            hoje = datetime.now().date().isoformat()
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM agendamentos_entrega
                WHERE data_agendada = ?
            ''', (hoje,))
            stats['entregas_hoje'] = cursor.fetchone()['total']
            
            # Taxa de entrega
            total = stats['total_pedidos']
            entregues = stats['por_status'].get('entregue', 0)
            stats['taxa_entrega'] = (entregues / total * 100) if total > 0 else 0
            
            return stats
        except:
            return {}
        finally:
            conn.close()


def testar_logistics_management():
    """Função de teste do sistema de logística"""
    print("\n" + "="*60)
    print("🧪 TESTE DE GESTÃO DE LOGÍSTICA")
    print("="*60 + "\n")
    
    sistema = LogisticsManagement()
    
    # Teste 1: Criar pedido
    print("1️⃣ Criando pedido de entrega...")
    dados_pedido = {
        'contrato_id': 1,
        'fornecedor_id': 1,
        'descricao': '5 Monitores Cardíacos + 3 Desfibriladores',
        'quantidade_itens': 8,
        'peso_total': 150.5,
        'volume_total': 2.5,
        'endereco_entrega': 'Av. Paulista, 1000',
        'cidade': 'São Paulo',
        'estado': 'SP',
        'cep': '01310-100',
        'contato_recebimento': 'Dr. João Silva',
        'telefone_contato': '(11) 3000-0000',
        'prioridade': 'alta',
        'observacoes': 'Entrega urgente - UTI'
    }
    
    ped_id = sistema.criar_pedido(dados_pedido)
    print(f"   ✅ Pedido criado: ID {ped_id}\n")
    
    # Teste 2: Agendar entrega
    print("2️⃣ Agendando entrega...")
    dados_agendamento = {
        'data_agendada': '2024-12-15',
        'horario_inicio': '14:00',
        'horario_fim': '16:00',
        'tipo_veiculo': 'Caminhão baú',
        'motorista': 'Carlos Santos',
        'placa_veiculo': 'ABC-1234',
        'observacoes': 'Entrada pela garagem'
    }
    
    agend_id = sistema.agendar_entrega(ped_id, dados_agendamento)
    print(f"   ✅ Entrega agendada: ID {agend_id}\n")
    
    # Teste 3: Atualizar status
    print("3️⃣ Atualizando status do pedido...")
    sistema.atualizar_status_pedido(
        ped_id,
        'em_transito',
        'Rodovia Anhanguera, KM 45',
        'Carlos Santos',
        'Saiu do CD às 13:30'
    )
    print(f"   ✅ Status atualizado: em_transito\n")
    
    # Teste 4: Registrar comprovante
    print("4️⃣ Registrando comprovante de entrega...")
    dados_comprovante = {
        'tipo_comprovante': 'nota_fiscal',
        'arquivo_path': '/tmp/comprovantes/nf_001.pdf',
        'recebedor_nome': 'Dr. João Silva',
        'recebedor_documento': '123.456.789-00',
        'observacoes': 'Produtos conferidos e em perfeito estado'
    }
    
    comp_id = sistema.registrar_comprovante(ped_id, dados_comprovante)
    print(f"   ✅ Comprovante registrado: ID {comp_id}\n")
    
    # Teste 5: Rastreamento
    print("5️⃣ Consultando rastreamento...")
    rastreamento = sistema.obter_rastreamento(ped_id)
    print(f"   📍 Total de eventos: {len(rastreamento)}")
    for evento in rastreamento:
        print(f"   • {evento['status']} - {evento['data_hora'][:16]} - {evento['responsavel']}")
    print()
    
    # Teste 6: Entregas pendentes
    print("6️⃣ Listando entregas pendentes...")
    pendentes = sistema.listar_entregas_pendentes()
    print(f"   📦 Total: {len(pendentes)} entregas pendentes\n")
    
    # Teste 7: Agendamentos do dia
    print("7️⃣ Agendamentos de 2024-12-15...")
    agendamentos = sistema.listar_agendamentos_dia('2024-12-15')
    print(f"   📅 Total: {len(agendamentos)} agendamentos")
    for ag in agendamentos:
        print(f"   • {ag['horario_inicio']}-{ag['horario_fim']} - {ag['numero_pedido']} - {ag['motorista']}")
    print()
    
    # Teste 8: Estatísticas
    print("8️⃣ Estatísticas de logística...")
    stats = sistema.obter_estatisticas()
    print(f"   📊 Total de Pedidos: {stats['total_pedidos']}")
    print(f"   📦 Entregas Hoje: {stats['entregas_hoje']}")
    print(f"   ✅ Taxa de Entrega: {stats['taxa_entrega']:.1f}%")
    print(f"   📈 Por Status:")
    for status, total in stats['por_status'].items():
        print(f"      • {status}: {total}")
    print()
    
    print("="*60)
    print("✅ SISTEMA DE LOGÍSTICA FUNCIONANDO")
    print("="*60 + "\n")


if __name__ == '__main__':
    testar_logistics_management()
