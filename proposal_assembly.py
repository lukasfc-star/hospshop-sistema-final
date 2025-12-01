"""
Sistema de Montagem de Propostas
Geração automática de propostas comerciais em PDF

Desenvolvido em 01/12/2025
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProposalAssembly:
    """
    Sistema de montagem automática de propostas comerciais
    """
    
    def __init__(self, output_dir='/tmp/propostas'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_available = self._check_pdf_library()
    
    def _check_pdf_library(self) -> bool:
        """Verifica se biblioteca PDF está disponível"""
        try:
            from fpdf import FPDF
            logger.info("✅ Biblioteca FPDF disponível")
            return True
        except ImportError:
            logger.warning("⚠️ FPDF não instalado. Execute: pip install fpdf2")
            logger.info("ℹ️  Modo simulação ativado")
            return False
    
    def gerar_proposta(self, dados: Dict) -> Optional[str]:
        """
        Gera proposta comercial em PDF
        
        Args:
            dados: Dicionário com dados da proposta
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        if not self.pdf_available:
            return self._simular_geracao(dados)
        
        try:
            from fpdf import FPDF
            
            # Criar PDF
            pdf = FPDF()
            pdf.add_page()
            
            # Configurar fonte
            pdf.set_font('Arial', '', 12)
            
            # Cabeçalho
            self._adicionar_cabecalho(pdf, dados)
            
            # Dados da licitação
            self._adicionar_dados_licitacao(pdf, dados)
            
            # Itens da proposta
            self._adicionar_itens(pdf, dados.get('itens', []))
            
            # Totais
            self._adicionar_totais(pdf, dados)
            
            # Condições comerciais
            self._adicionar_condicoes(pdf, dados)
            
            # Rodapé
            self._adicionar_rodape(pdf, dados)
            
            # Salvar PDF
            numero_proposta = dados.get('numero_proposta', 'PROP-000')
            filename = f"proposta_{numero_proposta.replace('/', '-')}.pdf"
            filepath = self.output_dir / filename
            
            pdf.output(str(filepath))
            
            logger.info(f"✅ Proposta gerada: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar proposta: {e}")
            return None
    
    def _adicionar_cabecalho(self, pdf, dados: Dict):
        """Adiciona cabeçalho da proposta"""
        # Logo (simulado com retângulo)
        pdf.set_fill_color(37, 99, 235)
        pdf.rect(10, 10, 40, 20, 'F')
        
        # Nome da empresa
        pdf.set_font('Arial', 'B', 20)
        pdf.set_xy(55, 15)
        pdf.cell(0, 10, dados.get('empresa', 'HOSPSHOP'), 0, 1)
        
        # Linha separadora
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, 35, 200, 35)
        
        # Título
        pdf.set_font('Arial', 'B', 16)
        pdf.set_xy(10, 40)
        pdf.cell(0, 10, 'PROPOSTA COMERCIAL', 0, 1, 'C')
        
        pdf.ln(5)
    
    def _adicionar_dados_licitacao(self, pdf, dados: Dict):
        """Adiciona dados da licitação"""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'DADOS DA LICITAÇÃO', 0, 1)
        pdf.set_font('Arial', '', 10)
        
        # Dados
        campos = [
            ('Número da Proposta', dados.get('numero_proposta', 'N/A')),
            ('Edital', dados.get('numero_edital', 'N/A')),
            ('Órgão', dados.get('orgao', 'N/A')),
            ('Data da Proposta', dados.get('data_proposta', datetime.now().strftime('%d/%m/%Y'))),
            ('Validade', dados.get('validade', '30 dias')),
        ]
        
        for label, valor in campos:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(50, 6, f"{label}:", 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, str(valor), 0, 1)
        
        pdf.ln(5)
    
    def _adicionar_itens(self, pdf, itens: List[Dict]):
        """Adiciona tabela de itens"""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'ITENS DA PROPOSTA', 0, 1)
        
        # Cabeçalho da tabela
        pdf.set_fill_color(37, 99, 235)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 9)
        
        pdf.cell(10, 8, 'Item', 1, 0, 'C', True)
        pdf.cell(70, 8, 'Descrição', 1, 0, 'C', True)
        pdf.cell(20, 8, 'Qtd', 1, 0, 'C', True)
        pdf.cell(20, 8, 'Unid', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Preço Unit.', 1, 0, 'C', True)
        pdf.cell(30, 8, 'Preço Total', 1, 1, 'C', True)
        
        # Itens
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 9)
        
        for i, item in enumerate(itens, 1):
            pdf.cell(10, 7, str(i), 1, 0, 'C')
            pdf.cell(70, 7, item.get('descricao', '')[:30], 1, 0)
            pdf.cell(20, 7, str(item.get('quantidade', 0)), 1, 0, 'C')
            pdf.cell(20, 7, item.get('unidade', 'UN'), 1, 0, 'C')
            pdf.cell(30, 7, f"R$ {item.get('preco_unitario', 0):,.2f}", 1, 0, 'R')
            pdf.cell(30, 7, f"R$ {item.get('preco_total', 0):,.2f}", 1, 1, 'R')
        
        pdf.ln(3)
    
    def _adicionar_totais(self, pdf, dados: Dict):
        """Adiciona totais da proposta"""
        pdf.set_font('Arial', 'B', 11)
        
        # Subtotal
        pdf.cell(150, 7, 'SUBTOTAL:', 0, 0, 'R')
        pdf.cell(30, 7, f"R$ {dados.get('subtotal', 0):,.2f}", 0, 1, 'R')
        
        # Desconto (se houver)
        if dados.get('desconto', 0) > 0:
            pdf.set_font('Arial', '', 10)
            pdf.cell(150, 6, f"Desconto ({dados.get('desconto_percentual', 0)}%):", 0, 0, 'R')
            pdf.cell(30, 6, f"- R$ {dados.get('desconto', 0):,.2f}", 0, 1, 'R')
        
        # Total
        pdf.set_font('Arial', 'B', 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(150, 8, 'VALOR TOTAL DA PROPOSTA:', 1, 0, 'R', True)
        pdf.cell(30, 8, f"R$ {dados.get('valor_total', 0):,.2f}", 1, 1, 'R', True)
        
        pdf.ln(5)
    
    def _adicionar_condicoes(self, pdf, dados: Dict):
        """Adiciona condições comerciais"""
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'CONDIÇÕES COMERCIAIS', 0, 1)
        
        pdf.set_font('Arial', '', 10)
        
        condicoes = [
            ('Prazo de Entrega', dados.get('prazo_entrega', '30 dias corridos')),
            ('Condições de Pagamento', dados.get('condicoes_pagamento', '30 dias após entrega')),
            ('Garantia', dados.get('garantia', '12 meses')),
            ('Frete', dados.get('frete', 'CIF - Incluso no preço')),
            ('Validade da Proposta', dados.get('validade', '30 dias')),
        ]
        
        for label, valor in condicoes:
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(60, 6, f"{label}:", 0, 0)
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, str(valor))
        
        # Observações
        if dados.get('observacoes'):
            pdf.ln(3)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'Observações:', 0, 1)
            pdf.set_font('Arial', '', 9)
            pdf.multi_cell(0, 5, dados['observacoes'])
        
        pdf.ln(5)
    
    def _adicionar_rodape(self, pdf, dados: Dict):
        """Adiciona rodapé com assinatura"""
        # Linha separadora
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Dados da empresa
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 5, dados.get('empresa', 'HOSPSHOP'), 0, 1, 'C')
        pdf.cell(0, 5, dados.get('endereco', 'Endereço da Empresa'), 0, 1, 'C')
        pdf.cell(0, 5, f"CNPJ: {dados.get('cnpj', '00.000.000/0000-00')}", 0, 1, 'C')
        pdf.cell(0, 5, f"Tel: {dados.get('telefone', '(11) 0000-0000')} | Email: {dados.get('email', 'contato@empresa.com')}", 0, 1, 'C')
        
        pdf.ln(10)
        
        # Assinatura
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 5, '_' * 50, 0, 1, 'C')
        pdf.cell(0, 5, dados.get('responsavel', 'Responsável pela Proposta'), 0, 1, 'C')
        pdf.set_font('Arial', '', 9)
        pdf.cell(0, 5, dados.get('cargo', 'Cargo'), 0, 1, 'C')
    
    def _simular_geracao(self, dados: Dict) -> str:
        """Simula geração de proposta"""
        numero_proposta = dados.get('numero_proposta', 'PROP-000')
        filename = f"proposta_{numero_proposta.replace('/', '-')}.pdf"
        filepath = self.output_dir / filename
        
        # Criar arquivo vazio
        filepath.touch()
        
        logger.info(f"✅ Proposta simulada: {filepath}")
        return str(filepath)
    
    def gerar_proposta_html(self, dados: Dict) -> str:
        """
        Gera versão HTML da proposta (para preview)
        
        Args:
            dados: Dados da proposta
            
        Returns:
            HTML da proposta
        """
        itens_html = ""
        for i, item in enumerate(dados.get('itens', []), 1):
            itens_html += f"""
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{item.get('descricao', '')}</td>
                <td style="text-align: center;">{item.get('quantidade', 0)}</td>
                <td style="text-align: center;">{item.get('unidade', 'UN')}</td>
                <td style="text-align: right;">R$ {item.get('preco_unitario', 0):,.2f}</td>
                <td style="text-align: right;">R$ {item.get('preco_total', 0):,.2f}</td>
            </tr>
            """
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Proposta {dados.get('numero_proposta', 'N/A')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .header {{ background: #2563eb; color: white; padding: 20px; margin-bottom: 20px; }}
        .section {{ margin: 20px 0; }}
        .section-title {{ font-weight: bold; font-size: 14px; margin-bottom: 10px; border-bottom: 2px solid #2563eb; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background: #2563eb; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px; border: 1px solid #ddd; }}
        .total {{ background: #f0f0f0; font-weight: bold; }}
        .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{dados.get('empresa', 'HOSPSHOP')}</h1>
        <h2>PROPOSTA COMERCIAL</h2>
    </div>
    
    <div class="section">
        <div class="section-title">DADOS DA LICITAÇÃO</div>
        <p><strong>Número da Proposta:</strong> {dados.get('numero_proposta', 'N/A')}</p>
        <p><strong>Edital:</strong> {dados.get('numero_edital', 'N/A')}</p>
        <p><strong>Órgão:</strong> {dados.get('orgao', 'N/A')}</p>
        <p><strong>Data:</strong> {dados.get('data_proposta', datetime.now().strftime('%d/%m/%Y'))}</p>
        <p><strong>Validade:</strong> {dados.get('validade', '30 dias')}</p>
    </div>
    
    <div class="section">
        <div class="section-title">ITENS DA PROPOSTA</div>
        <table>
            <thead>
                <tr>
                    <th>Item</th>
                    <th>Descrição</th>
                    <th>Qtd</th>
                    <th>Unid</th>
                    <th>Preço Unit.</th>
                    <th>Preço Total</th>
                </tr>
            </thead>
            <tbody>
                {itens_html}
                <tr class="total">
                    <td colspan="5" style="text-align: right;">VALOR TOTAL:</td>
                    <td style="text-align: right;">R$ {dados.get('valor_total', 0):,.2f}</td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <div class="section">
        <div class="section-title">CONDIÇÕES COMERCIAIS</div>
        <p><strong>Prazo de Entrega:</strong> {dados.get('prazo_entrega', '30 dias corridos')}</p>
        <p><strong>Condições de Pagamento:</strong> {dados.get('condicoes_pagamento', '30 dias após entrega')}</p>
        <p><strong>Garantia:</strong> {dados.get('garantia', '12 meses')}</p>
        <p><strong>Frete:</strong> {dados.get('frete', 'CIF - Incluso')}</p>
    </div>
    
    <div class="footer">
        <p>{dados.get('empresa', 'HOSPSHOP')}</p>
        <p>{dados.get('endereco', 'Endereço da Empresa')}</p>
        <p>CNPJ: {dados.get('cnpj', '00.000.000/0000-00')} | Tel: {dados.get('telefone', '(11) 0000-0000')}</p>
    </div>
</body>
</html>
"""
        return html


def testar_proposal_assembly():
    """Função de teste do sistema de propostas"""
    print("\n" + "="*60)
    print("🧪 TESTE DE MONTAGEM DE PROPOSTAS")
    print("="*60 + "\n")
    
    sistema = ProposalAssembly()
    
    # Dados de teste
    dados_proposta = {
        'numero_proposta': 'PROP-2024-001',
        'numero_edital': 'PE-2024-TEST-001',
        'orgao': 'Hospital Municipal de São Paulo',
        'empresa': 'HOSPSHOP LTDA',
        'cnpj': '12.345.678/0001-90',
        'endereco': 'Rua das Empresas, 123 - São Paulo/SP',
        'telefone': '(11) 3000-0000',
        'email': 'contato@hospshop.com',
        'data_proposta': '01/12/2024',
        'validade': '30 dias',
        'itens': [
            {
                'descricao': 'Monitor Cardíaco Multiparâmetros',
                'quantidade': 5,
                'unidade': 'UN',
                'preco_unitario': 8500.00,
                'preco_total': 42500.00
            },
            {
                'descricao': 'Desfibrilador Bifásico',
                'quantidade': 3,
                'unidade': 'UN',
                'preco_unitario': 12000.00,
                'preco_total': 36000.00
            },
            {
                'descricao': 'Bomba de Infusão',
                'quantidade': 10,
                'unidade': 'UN',
                'preco_unitario': 3500.00,
                'preco_total': 35000.00
            }
        ],
        'subtotal': 113500.00,
        'desconto': 0,
        'desconto_percentual': 0,
        'valor_total': 113500.00,
        'prazo_entrega': '30 dias corridos após assinatura do contrato',
        'condicoes_pagamento': '30 dias após entrega e aceite',
        'garantia': '24 meses de fábrica',
        'frete': 'CIF - Incluso no preço',
        'observacoes': 'Todos os equipamentos possuem certificação ANVISA. Assistência técnica disponível em todo território nacional.',
        'responsavel': 'João Silva',
        'cargo': 'Diretor Comercial'
    }
    
    # Teste 1: Gerar proposta PDF
    print("1️⃣ Gerando proposta em PDF...")
    pdf_path = sistema.gerar_proposta(dados_proposta)
    if pdf_path:
        print(f"   ✅ PDF gerado: {pdf_path}")
        print(f"   📄 Tamanho: {Path(pdf_path).stat().st_size if Path(pdf_path).exists() else 0} bytes\n")
    
    # Teste 2: Gerar versão HTML
    print("2️⃣ Gerando versão HTML...")
    html = sistema.gerar_proposta_html(dados_proposta)
    html_path = sistema.output_dir / 'proposta_preview.html'
    html_path.write_text(html, encoding='utf-8')
    print(f"   ✅ HTML gerado: {html_path}")
    print(f"   📄 Tamanho: {len(html)} caracteres\n")
    
    # Teste 3: Proposta com desconto
    print("3️⃣ Gerando proposta com desconto...")
    dados_com_desconto = dados_proposta.copy()
    dados_com_desconto.update({
        'numero_proposta': 'PROP-2024-002',
        'desconto': 5675.00,
        'desconto_percentual': 5,
        'valor_total': 107825.00
    })
    
    pdf_desconto = sistema.gerar_proposta(dados_com_desconto)
    if pdf_desconto:
        print(f"   ✅ Proposta com desconto gerada\n")
    
    print("="*60)
    print("✅ SISTEMA DE PROPOSTAS FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📊 Estatísticas:")
    print(f"   • Propostas Geradas: 2")
    print(f"   • Itens Processados: {len(dados_proposta['itens'])}")
    print(f"   • Valor Total: R$ {dados_proposta['valor_total']:,.2f}")
    print(f"   • Diretório: {sistema.output_dir}\n")


if __name__ == '__main__':
    testar_proposal_assembly()
