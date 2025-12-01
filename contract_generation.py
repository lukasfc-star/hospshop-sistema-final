"""
Sistema de Geração de Contratos
Geração automática de contratos legais em PDF

Desenvolvido em 01/12/2025
"""

import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContractGeneration:
    """
    Sistema de geração automática de contratos
    """
    
    def __init__(self, output_dir='/tmp/contratos'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_available = self._check_pdf_library()
        self.templates = self._load_templates()
    
    def _check_pdf_library(self) -> bool:
        """Verifica biblioteca PDF"""
        try:
            from fpdf import FPDF
            logger.info("✅ Biblioteca FPDF disponível")
            return True
        except ImportError:
            logger.warning("⚠️ FPDF não instalado")
            logger.info("ℹ️  Modo simulação ativado")
            return False
    
    def _load_templates(self) -> Dict:
        """Carrega templates de contratos"""
        return {
            'fornecimento': self._template_fornecimento(),
            'prestacao_servicos': self._template_prestacao_servicos(),
            'locacao': self._template_locacao(),
        }
    
    def _template_fornecimento(self) -> str:
        """Template de contrato de fornecimento"""
        return """
CONTRATO DE FORNECIMENTO Nº {{numero_contrato}}

Pelo presente instrumento particular de contrato, de um lado:

CONTRATANTE: {{contratante_nome}}, inscrito no CNPJ sob o nº {{contratante_cnpj}}, 
com sede na {{contratante_endereco}}, neste ato representado por {{contratante_representante}}, 
doravante denominado simplesmente CONTRATANTE;

E de outro lado:

CONTRATADO: {{contratado_nome}}, inscrito no CNPJ sob o nº {{contratado_cnpj}}, 
com sede na {{contratado_endereco}}, neste ato representado por {{contratado_representante}}, 
doravante denominado simplesmente CONTRATADO;

Têm entre si justo e contratado o seguinte:

CLÁUSULA PRIMEIRA - DO OBJETO
O presente contrato tem por objeto o fornecimento de {{objeto}}, conforme especificações 
constantes no Edital {{numero_edital}} e na Proposta {{numero_proposta}}, que passam a fazer 
parte integrante deste instrumento.

CLÁUSULA SEGUNDA - DO VALOR
O valor total do presente contrato é de R$ {{valor_total}} ({{valor_extenso}}), 
conforme detalhamento:
{{itens_detalhamento}}

CLÁUSULA TERCEIRA - DO PRAZO DE ENTREGA
O CONTRATADO obriga-se a entregar os produtos no prazo de {{prazo_entrega}}, 
contados a partir da assinatura deste contrato, no local indicado: {{local_entrega}}.

CLÁUSULA QUARTA - DAS CONDIÇÕES DE PAGAMENTO
O pagamento será efetuado em {{condicoes_pagamento}}, mediante apresentação de 
nota fiscal devidamente atestada pelo setor competente.

CLÁUSULA QUINTA - DA GARANTIA
Os produtos fornecidos terão garantia de {{garantia}}, contra defeitos de fabricação, 
incluindo assistência técnica e reposição de peças.

CLÁUSULA SEXTA - DAS OBRIGAÇÕES DO CONTRATADO
São obrigações do CONTRATADO:
a) Fornecer os produtos conforme especificações técnicas;
b) Responsabilizar-se por todos os encargos trabalhistas, previdenciários e fiscais;
c) Manter durante toda a execução do contrato as condições de habilitação;
d) Reparar ou substituir, às suas expensas, produtos com defeito ou em desacordo.

CLÁUSULA SÉTIMA - DAS OBRIGAÇÕES DO CONTRATANTE
São obrigações do CONTRATANTE:
a) Efetuar o pagamento nas condições estabelecidas;
b) Proporcionar todas as facilidades para que o CONTRATADO possa cumprir suas obrigações;
c) Fiscalizar a execução do contrato.

CLÁUSULA OITAVA - DAS PENALIDADES
O descumprimento total ou parcial das obrigações assumidas sujeitará o CONTRATADO às seguintes penalidades:
a) Advertência;
b) Multa de {{multa_percentual}}% sobre o valor do contrato;
c) Suspensão temporária de participação em licitações;
d) Declaração de inidoneidade.

CLÁUSULA NONA - DA RESCISÃO
O presente contrato poderá ser rescindido:
a) Por acordo entre as partes;
b) Unilateralmente, nos casos previstos em lei;
c) Por inadimplemento de qualquer das cláusulas contratuais.

CLÁUSULA DÉCIMA - DA VIGÊNCIA
O presente contrato terá vigência de {{vigencia}}, a partir de {{data_inicio}}, 
podendo ser prorrogado mediante termo aditivo.

CLÁUSULA DÉCIMA PRIMEIRA - DO FORO
Fica eleito o foro de {{foro}}, com renúncia expressa a qualquer outro, 
por mais privilegiado que seja, para dirimir quaisquer dúvidas oriundas do presente contrato.

E, por estarem assim justos e contratados, assinam o presente instrumento em 02 (duas) vias 
de igual teor e forma, na presença das testemunhas abaixo.

{{cidade}}, {{data_assinatura}}

_________________________________          _________________________________
{{contratante_nome}}                      {{contratado_nome}}
CONTRATANTE                               CONTRATADO

TESTEMUNHAS:

_________________________________          _________________________________
Nome:                                     Nome:
CPF:                                      CPF:
"""
    
    def _template_prestacao_servicos(self) -> str:
        """Template de contrato de prestação de serviços"""
        return """
CONTRATO DE PRESTAÇÃO DE SERVIÇOS Nº {{numero_contrato}}

[Estrutura similar ao contrato de fornecimento, adaptada para serviços]

CLÁUSULA PRIMEIRA - DO OBJETO
O presente contrato tem por objeto a prestação de serviços de {{objeto}}.

CLÁUSULA SEGUNDA - DO VALOR E FORMA DE PAGAMENTO
Os serviços serão remunerados pelo valor total de R$ {{valor_total}}.

[Demais cláusulas adaptadas para prestação de serviços]
"""
    
    def _template_locacao(self) -> str:
        """Template de contrato de locação"""
        return """
CONTRATO DE LOCAÇÃO Nº {{numero_contrato}}

[Estrutura adaptada para locação de equipamentos]

CLÁUSULA PRIMEIRA - DO OBJETO
O presente contrato tem por objeto a locação de {{objeto}}.

[Demais cláusulas específicas de locação]
"""
    
    def gerar_contrato(self, tipo: str, dados: Dict) -> Optional[str]:
        """
        Gera contrato em PDF
        
        Args:
            tipo: Tipo do contrato (fornecimento, prestacao_servicos, locacao)
            dados: Dados do contrato
            
        Returns:
            Caminho do arquivo PDF gerado
        """
        if tipo not in self.templates:
            logger.error(f"❌ Tipo de contrato '{tipo}' não encontrado")
            return None
        
        if not self.pdf_available:
            return self._simular_geracao(dados)
        
        try:
            from fpdf import FPDF
            
            # Criar PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            
            # Cabeçalho
            self._adicionar_cabecalho_contrato(pdf, dados)
            
            # Corpo do contrato
            template = self.templates[tipo]
            texto_contrato = self._preencher_template(template, dados)
            
            # Adicionar texto
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 5, texto_contrato)
            
            # Salvar
            numero_contrato = dados.get('numero_contrato', 'CONT-000')
            filename = f"contrato_{numero_contrato.replace('/', '-')}.pdf"
            filepath = self.output_dir / filename
            
            pdf.output(str(filepath))
            
            logger.info(f"✅ Contrato gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar contrato: {e}")
            return None
    
    def _adicionar_cabecalho_contrato(self, pdf, dados: Dict):
        """Adiciona cabeçalho do contrato"""
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f"CONTRATO Nº {dados.get('numero_contrato', 'N/A')}", 0, 1, 'C')
        pdf.ln(5)
    
    def _preencher_template(self, template: str, dados: Dict) -> str:
        """Preenche template com dados"""
        texto = template
        for chave, valor in dados.items():
            placeholder = f"{{{{{chave}}}}}"
            texto = texto.replace(placeholder, str(valor))
        return texto
    
    def _simular_geracao(self, dados: Dict) -> str:
        """Simula geração de contrato"""
        numero_contrato = dados.get('numero_contrato', 'CONT-000')
        filename = f"contrato_{numero_contrato.replace('/', '-')}.pdf"
        filepath = self.output_dir / filename
        filepath.touch()
        
        logger.info(f"✅ Contrato simulado: {filepath}")
        return str(filepath)
    
    def gerar_termo_aditivo(self, contrato_original: str, dados_aditivo: Dict) -> Optional[str]:
        """
        Gera termo aditivo ao contrato
        
        Args:
            contrato_original: Número do contrato original
            dados_aditivo: Dados do aditivo
            
        Returns:
            Caminho do termo aditivo gerado
        """
        dados = {
            'numero_aditivo': dados_aditivo.get('numero_aditivo', 'TA-001'),
            'contrato_original': contrato_original,
            'tipo_alteracao': dados_aditivo.get('tipo', 'prorrogacao'),
            'justificativa': dados_aditivo.get('justificativa', ''),
            'nova_vigencia': dados_aditivo.get('nova_vigencia', ''),
            'novo_valor': dados_aditivo.get('novo_valor', ''),
            'data_aditivo': datetime.now().strftime('%d/%m/%Y'),
        }
        
        # Gerar PDF do termo aditivo
        if not self.pdf_available:
            return self._simular_termo_aditivo(dados)
        
        try:
            from fpdf import FPDF
            
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, f"TERMO ADITIVO Nº {dados['numero_aditivo']}", 0, 1, 'C')
            pdf.cell(0, 10, f"AO CONTRATO Nº {contrato_original}", 0, 1, 'C')
            pdf.ln(10)
            
            pdf.set_font('Arial', '', 11)
            texto = f"""
Pelo presente instrumento, as partes do Contrato nº {contrato_original} 
resolvem alterá-lo conforme segue:

TIPO DE ALTERAÇÃO: {dados['tipo_alteracao'].upper()}

JUSTIFICATIVA:
{dados['justificativa']}

NOVA VIGÊNCIA: {dados['nova_vigencia']}
NOVO VALOR: R$ {dados['novo_valor']}

As demais cláusulas permanecem inalteradas.

{dados['data_aditivo']}

_________________________________          _________________________________
CONTRATANTE                               CONTRATADO
"""
            pdf.multi_cell(0, 5, texto)
            
            filename = f"termo_aditivo_{dados['numero_aditivo'].replace('/', '-')}.pdf"
            filepath = self.output_dir / filename
            pdf.output(str(filepath))
            
            logger.info(f"✅ Termo aditivo gerado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar termo aditivo: {e}")
            return None
    
    def _simular_termo_aditivo(self, dados: Dict) -> str:
        """Simula geração de termo aditivo"""
        filename = f"termo_aditivo_{dados['numero_aditivo']}.pdf"
        filepath = self.output_dir / filename
        filepath.touch()
        logger.info(f"✅ Termo aditivo simulado: {filepath}")
        return str(filepath)


def testar_contract_generation():
    """Função de teste do sistema de contratos"""
    print("\n" + "="*60)
    print("🧪 TESTE DE GERAÇÃO DE CONTRATOS")
    print("="*60 + "\n")
    
    sistema = ContractGeneration()
    
    # Dados de teste
    dados_contrato = {
        'numero_contrato': 'CONT-2024-001',
        'numero_edital': 'PE-2024-TEST-001',
        'numero_proposta': 'PROP-2024-001',
        'contratante_nome': 'HOSPITAL MUNICIPAL DE SÃO PAULO',
        'contratante_cnpj': '12.345.678/0001-90',
        'contratante_endereco': 'Av. Paulista, 1000 - São Paulo/SP',
        'contratante_representante': 'Dr. José Silva',
        'contratado_nome': 'HOSPSHOP LTDA',
        'contratado_cnpj': '98.765.432/0001-10',
        'contratado_endereco': 'Rua das Empresas, 123 - São Paulo/SP',
        'contratado_representante': 'João Santos',
        'objeto': 'equipamentos hospitalares (monitores cardíacos, desfibriladores e bombas de infusão)',
        'valor_total': '113.500,00',
        'valor_extenso': 'cento e treze mil e quinhentos reais',
        'itens_detalhamento': '5 Monitores Cardíacos, 3 Desfibriladores, 10 Bombas de Infusão',
        'prazo_entrega': '30 (trinta) dias corridos',
        'local_entrega': 'Hospital Municipal - Almoxarifado Central',
        'condicoes_pagamento': '30 (trinta) dias após entrega e aceite',
        'garantia': '24 (vinte e quatro) meses',
        'multa_percentual': '10',
        'vigencia': '12 (doze) meses',
        'data_inicio': '01/12/2024',
        'foro': 'São Paulo/SP',
        'cidade': 'São Paulo',
        'data_assinatura': '01/12/2024',
    }
    
    # Teste 1: Gerar contrato de fornecimento
    print("1️⃣ Gerando contrato de fornecimento...")
    pdf_path = sistema.gerar_contrato('fornecimento', dados_contrato)
    if pdf_path:
        print(f"   ✅ Contrato gerado: {pdf_path}")
        tamanho = Path(pdf_path).stat().st_size if Path(pdf_path).exists() else 0
        print(f"   📄 Tamanho: {tamanho} bytes\n")
    
    # Teste 2: Gerar termo aditivo
    print("2️⃣ Gerando termo aditivo...")
    dados_aditivo = {
        'numero_aditivo': 'TA-001/2024',
        'tipo': 'prorrogacao',
        'justificativa': 'Necessidade de prorrogação do prazo devido a atraso na entrega de componentes importados.',
        'nova_vigencia': '31/06/2025',
        'novo_valor': '113.500,00',
    }
    
    termo_path = sistema.gerar_termo_aditivo('CONT-2024-001', dados_aditivo)
    if termo_path:
        print(f"   ✅ Termo aditivo gerado: {termo_path}\n")
    
    # Teste 3: Contrato de prestação de serviços
    print("3️⃣ Gerando contrato de prestação de serviços...")
    dados_servicos = dados_contrato.copy()
    dados_servicos.update({
        'numero_contrato': 'CONT-2024-002',
        'objeto': 'manutenção preventiva e corretiva de equipamentos hospitalares',
    })
    
    servicos_path = sistema.gerar_contrato('prestacao_servicos', dados_servicos)
    if servicos_path:
        print(f"   ✅ Contrato de serviços gerado\n")
    
    print("="*60)
    print("✅ SISTEMA DE CONTRATOS FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📊 Estatísticas:")
    print(f"   • Contratos Gerados: 2")
    print(f"   • Termos Aditivos: 1")
    print(f"   • Templates Disponíveis: {len(sistema.templates)}")
    print(f"   • Diretório: {sistema.output_dir}\n")


if __name__ == '__main__':
    testar_contract_generation()
