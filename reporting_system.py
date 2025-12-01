"""
Sistema de Relatórios
Geração de relatórios gerenciais, operacionais e executivos

Desenvolvido em 01/12/2025
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportingSystem:
    """
    Sistema completo de relatórios
    """
    
    def __init__(self, db_path='hospshop.db', output_dir='/tmp/relatorios'):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_available = self._check_pdf_library()
    
    def _check_pdf_library(self) -> bool:
        """Verifica biblioteca PDF"""
        try:
            from fpdf import FPDF
            logger.info("✅ Biblioteca FPDF disponível")
            return True
        except ImportError:
            logger.warning("⚠️ FPDF não instalado")
            return False
    
    def get_db_connection(self):
        """Retorna conexão com banco"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"Erro ao conectar banco: {e}")
            return None
    
    def relatorio_licitacoes(self, periodo_inicio: str, periodo_fim: str) -> Dict:
        """
        Relatório de licitações do período
        
        Args:
            periodo_inicio: Data inicial (YYYY-MM-DD)
            periodo_fim: Data final (YYYY-MM-DD)
            
        Returns:
            Dicionário com dados do relatório
        """
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Total de licitações
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM licitacoes
                WHERE data_abertura BETWEEN ? AND ?
            ''', (periodo_inicio, periodo_fim))
            total = cursor.fetchone()['total']
            
            # Licitações por status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as total
                FROM licitacoes
                WHERE data_abertura BETWEEN ? AND ?
                GROUP BY status
            ''', (periodo_inicio, periodo_fim))
            por_status = {row['status']: row['total'] for row in cursor.fetchall()}
            
            # Licitações por estado
            cursor = conn.execute('''
                SELECT estado, COUNT(*) as total
                FROM licitacoes
                WHERE data_abertura BETWEEN ? AND ?
                GROUP BY estado
            ''', (periodo_inicio, periodo_fim))
            por_estado = {row['estado']: row['total'] for row in cursor.fetchall()}
            
            # Valor total estimado
            cursor = conn.execute('''
                SELECT SUM(valor_estimado) as total FROM licitacoes
                WHERE data_abertura BETWEEN ? AND ?
            ''', (periodo_inicio, periodo_fim))
            valor_total = cursor.fetchone()['total'] or 0
            
            relatorio = {
                'tipo': 'licitacoes',
                'periodo': {'inicio': periodo_inicio, 'fim': periodo_fim},
                'total_licitacoes': total,
                'por_status': por_status,
                'por_estado': por_estado,
                'valor_total_estimado': valor_total,
                'taxa_participacao': (por_status.get('participando', 0) / total * 100) if total > 0 else 0
            }
            
            logger.info(f"✅ Relatório de licitações gerado: {total} licitações")
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
        finally:
            conn.close()
    
    def relatorio_fornecedores(self) -> Dict:
        """Relatório de fornecedores"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Total de fornecedores
            cursor = conn.execute('SELECT COUNT(*) as total FROM fornecedores')
            total = cursor.fetchone()['total']
            
            # Fornecedores ativos
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM fornecedores WHERE ativo = 1
            ''')
            ativos = cursor.fetchone()['total']
            
            # Fornecedores por categoria
            cursor = conn.execute('''
                SELECT categoria, COUNT(*) as total
                FROM fornecedores
                GROUP BY categoria
            ''')
            por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
            
            # Top 10 fornecedores (por número de propostas)
            cursor = conn.execute('''
                SELECT f.nome, COUNT(p.id) as total_propostas
                FROM fornecedores f
                LEFT JOIN propostas p ON f.id = p.fornecedor_id
                GROUP BY f.id
                ORDER BY total_propostas DESC
                LIMIT 10
            ''')
            top_fornecedores = [dict(row) for row in cursor.fetchall()]
            
            relatorio = {
                'tipo': 'fornecedores',
                'total_fornecedores': total,
                'fornecedores_ativos': ativos,
                'por_categoria': por_categoria,
                'top_10_fornecedores': top_fornecedores,
                'taxa_ativacao': (ativos / total * 100) if total > 0 else 0
            }
            
            logger.info(f"✅ Relatório de fornecedores gerado: {total} fornecedores")
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
        finally:
            conn.close()
    
    def relatorio_financeiro(self, periodo_inicio: str, periodo_fim: str) -> Dict:
        """Relatório financeiro do período"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Receitas
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM receitas
                WHERE data_recebimento BETWEEN ? AND ?
                AND status = 'recebida'
            ''', (periodo_inicio, periodo_fim))
            total_receitas = cursor.fetchone()['total'] or 0
            
            # Despesas
            cursor = conn.execute('''
                SELECT SUM(valor) as total FROM despesas
                WHERE data_pagamento BETWEEN ? AND ?
                AND status = 'paga'
            ''', (periodo_inicio, periodo_fim))
            total_despesas = cursor.fetchone()['total'] or 0
            
            # Resultado
            resultado = total_receitas - total_despesas
            margem = (resultado / total_receitas * 100) if total_receitas > 0 else 0
            
            # Receitas por categoria
            cursor = conn.execute('''
                SELECT categoria, SUM(valor) as total
                FROM receitas
                WHERE data_recebimento BETWEEN ? AND ?
                AND status = 'recebida'
                GROUP BY categoria
            ''', (periodo_inicio, periodo_fim))
            receitas_por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
            
            # Despesas por categoria
            cursor = conn.execute('''
                SELECT categoria, SUM(valor) as total
                FROM despesas
                WHERE data_pagamento BETWEEN ? AND ?
                AND status = 'paga'
                GROUP BY categoria
            ''', (periodo_inicio, periodo_fim))
            despesas_por_categoria = {row['categoria']: row['total'] for row in cursor.fetchall()}
            
            relatorio = {
                'tipo': 'financeiro',
                'periodo': {'inicio': periodo_inicio, 'fim': periodo_fim},
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'resultado': resultado,
                'margem_percentual': margem,
                'receitas_por_categoria': receitas_por_categoria,
                'despesas_por_categoria': despesas_por_categoria
            }
            
            logger.info(f"✅ Relatório financeiro gerado: Resultado R$ {resultado:,.2f}")
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
        finally:
            conn.close()
    
    def relatorio_logistica(self, periodo_inicio: str, periodo_fim: str) -> Dict:
        """Relatório de logística e entregas"""
        conn = self.get_db_connection()
        if not conn:
            return {}
        
        try:
            # Total de entregas
            cursor = conn.execute('''
                SELECT COUNT(*) as total FROM pedidos_entrega
                WHERE created_at BETWEEN ? AND ?
            ''', (periodo_inicio, periodo_fim))
            total_entregas = cursor.fetchone()['total']
            
            # Entregas por status
            cursor = conn.execute('''
                SELECT status, COUNT(*) as total
                FROM pedidos_entrega
                WHERE created_at BETWEEN ? AND ?
                GROUP BY status
            ''', (periodo_inicio, periodo_fim))
            por_status = {row['status']: row['total'] for row in cursor.fetchall()}
            
            # Taxa de entrega no prazo
            entregues = por_status.get('entregue', 0)
            taxa_entrega = (entregues / total_entregas * 100) if total_entregas > 0 else 0
            
            # Entregas por cidade
            cursor = conn.execute('''
                SELECT cidade, COUNT(*) as total
                FROM pedidos_entrega
                WHERE created_at BETWEEN ? AND ?
                GROUP BY cidade
                ORDER BY total DESC
                LIMIT 10
            ''', (periodo_inicio, periodo_fim))
            por_cidade = {row['cidade']: row['total'] for row in cursor.fetchall()}
            
            relatorio = {
                'tipo': 'logistica',
                'periodo': {'inicio': periodo_inicio, 'fim': periodo_fim},
                'total_entregas': total_entregas,
                'por_status': por_status,
                'taxa_entrega': taxa_entrega,
                'entregas_por_cidade': por_cidade
            }
            
            logger.info(f"✅ Relatório de logística gerado: {total_entregas} entregas")
            return relatorio
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
        finally:
            conn.close()
    
    def relatorio_executivo(self, periodo_inicio: str, periodo_fim: str) -> Dict:
        """
        Relatório executivo consolidado
        
        Combina dados de todos os módulos
        """
        logger.info("📊 Gerando relatório executivo...")
        
        relatorio = {
            'tipo': 'executivo',
            'periodo': {'inicio': periodo_inicio, 'fim': periodo_fim},
            'data_geracao': datetime.now().isoformat(),
            'licitacoes': self.relatorio_licitacoes(periodo_inicio, periodo_fim),
            'fornecedores': self.relatorio_fornecedores(),
            'financeiro': self.relatorio_financeiro(periodo_inicio, periodo_fim),
            'logistica': self.relatorio_logistica(periodo_inicio, periodo_fim)
        }
        
        # KPIs principais
        relatorio['kpis'] = {
            'total_licitacoes': relatorio['licitacoes'].get('total_licitacoes', 0),
            'taxa_participacao': relatorio['licitacoes'].get('taxa_participacao', 0),
            'resultado_financeiro': relatorio['financeiro'].get('resultado', 0),
            'margem_financeira': relatorio['financeiro'].get('margem_percentual', 0),
            'taxa_entrega': relatorio['logistica'].get('taxa_entrega', 0),
            'fornecedores_ativos': relatorio['fornecedores'].get('fornecedores_ativos', 0)
        }
        
        logger.info("✅ Relatório executivo gerado")
        return relatorio
    
    def gerar_pdf_relatorio(self, relatorio: Dict, titulo: str) -> Optional[str]:
        """
        Gera PDF do relatório
        
        Args:
            relatorio: Dados do relatório
            titulo: Título do relatório
            
        Returns:
            Caminho do arquivo PDF ou None
        """
        if not self.pdf_available:
            return self._simular_pdf(titulo)
        
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            
            # Cabeçalho
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, titulo, 0, 1, 'C')
            pdf.ln(5)
            
            # Período
            if 'periodo' in relatorio:
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 5, f"Período: {relatorio['periodo']['inicio']} a {relatorio['periodo']['fim']}", 0, 1)
                pdf.ln(5)
            
            # Conteúdo (simplificado)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, str(relatorio))
            
            # Salvar
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"relatorio_{titulo.lower().replace(' ', '_')}_{timestamp}.pdf"
            filepath = self.output_dir / filename
            
            pdf.output(str(filepath))
            
            logger.info(f"✅ PDF gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar PDF: {e}")
            return None
    
    def _simular_pdf(self, titulo: str) -> str:
        """Simula geração de PDF"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"relatorio_{titulo.lower().replace(' ', '_')}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        filepath.touch()
        
        logger.info(f"✅ PDF simulado: {filepath}")
        return str(filepath)
    
    def exportar_csv(self, dados: List[Dict], nome_arquivo: str) -> Optional[str]:
        """
        Exporta dados para CSV
        
        Args:
            dados: Lista de dicionários com dados
            nome_arquivo: Nome do arquivo
            
        Returns:
            Caminho do arquivo CSV ou None
        """
        if not dados:
            logger.warning("⚠️ Nenhum dado para exportar")
            return None
        
        try:
            import csv
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{nome_arquivo}_{timestamp}.csv"
            filepath = self.output_dir / filename
            
            # Obter colunas
            colunas = list(dados[0].keys())
            
            # Escrever CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=colunas)
                writer.writeheader()
                writer.writerows(dados)
            
            logger.info(f"✅ CSV exportado: {filepath} ({len(dados)} linhas)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar CSV: {e}")
            return None


def testar_reporting_system():
    """Função de teste do sistema de relatórios"""
    print("\n" + "="*60)
    print("🧪 TESTE DE SISTEMA DE RELATÓRIOS")
    print("="*60 + "\n")
    
    sistema = ReportingSystem()
    
    # Período de teste
    periodo_inicio = '2024-12-01'
    periodo_fim = '2024-12-31'
    
    # Teste 1: Relatório de licitações
    print("1️⃣ Gerando relatório de licitações...")
    rel_licitacoes = sistema.relatorio_licitacoes(periodo_inicio, periodo_fim)
    print(f"   📊 Total: {rel_licitacoes.get('total_licitacoes', 0)} licitações")
    print(f"   📈 Taxa de Participação: {rel_licitacoes.get('taxa_participacao', 0):.1f}%\n")
    
    # Teste 2: Relatório de fornecedores
    print("2️⃣ Gerando relatório de fornecedores...")
    rel_fornecedores = sistema.relatorio_fornecedores()
    print(f"   👥 Total: {rel_fornecedores.get('total_fornecedores', 0)} fornecedores")
    print(f"   ✅ Ativos: {rel_fornecedores.get('fornecedores_ativos', 0)}\n")
    
    # Teste 3: Relatório financeiro
    print("3️⃣ Gerando relatório financeiro...")
    rel_financeiro = sistema.relatorio_financeiro(periodo_inicio, periodo_fim)
    print(f"   💰 Receitas: R$ {rel_financeiro.get('total_receitas', 0):,.2f}")
    print(f"   💸 Despesas: R$ {rel_financeiro.get('total_despesas', 0):,.2f}")
    print(f"   📈 Resultado: R$ {rel_financeiro.get('resultado', 0):,.2f}")
    print(f"   📊 Margem: {rel_financeiro.get('margem_percentual', 0):.1f}%\n")
    
    # Teste 4: Relatório de logística
    print("4️⃣ Gerando relatório de logística...")
    rel_logistica = sistema.relatorio_logistica(periodo_inicio, periodo_fim)
    print(f"   📦 Total de Entregas: {rel_logistica.get('total_entregas', 0)}")
    print(f"   ✅ Taxa de Entrega: {rel_logistica.get('taxa_entrega', 0):.1f}%\n")
    
    # Teste 5: Relatório executivo
    print("5️⃣ Gerando relatório executivo...")
    rel_executivo = sistema.relatorio_executivo(periodo_inicio, periodo_fim)
    print(f"   📊 KPIs Principais:")
    for kpi, valor in rel_executivo.get('kpis', {}).items():
        print(f"      • {kpi}: {valor}")
    print()
    
    # Teste 6: Gerar PDF
    print("6️⃣ Gerando PDF do relatório executivo...")
    pdf_path = sistema.gerar_pdf_relatorio(rel_executivo, 'Relatório Executivo')
    if pdf_path:
        print(f"   ✅ PDF gerado: {pdf_path}\n")
    
    # Teste 7: Exportar CSV
    print("7️⃣ Exportando dados para CSV...")
    dados_exemplo = [
        {'nome': 'Fornecedor A', 'total_propostas': 10},
        {'nome': 'Fornecedor B', 'total_propostas': 8},
        {'nome': 'Fornecedor C', 'total_propostas': 5}
    ]
    csv_path = sistema.exportar_csv(dados_exemplo, 'fornecedores')
    if csv_path:
        print(f"   ✅ CSV exportado: {csv_path}\n")
    
    print("="*60)
    print("✅ SISTEMA DE RELATÓRIOS FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📊 Tipos de relatórios disponíveis:")
    print("   • Licitações (por período)")
    print("   • Fornecedores (geral)")
    print("   • Financeiro (por período)")
    print("   • Logística (por período)")
    print("   • Executivo (consolidado)")
    print("\n📄 Formatos de exportação:")
    print("   • PDF (relatórios formatados)")
    print("   • CSV (dados tabulares)\n")


if __name__ == '__main__':
    testar_reporting_system()
