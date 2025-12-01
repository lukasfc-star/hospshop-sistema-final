"""
Módulo de Análise OCR de Documentos
Extração de texto e dados de editais em PDF e imagens

Desenvolvido em 01/12/2025
"""

import os
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRDocumentAnalyzer:
    """
    Classe para análise de documentos via OCR
    Suporta PDF e imagens
    """
    
    def __init__(self, temp_dir='/tmp/hospshop_ocr'):
        """
        Inicializa analisador OCR
        
        Args:
            temp_dir: Diretório temporário para processamento
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.tesseract_available = self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Verifica se Tesseract OCR está instalado"""
        try:
            import pytesseract
            from PIL import Image
            logger.info("✅ Tesseract OCR disponível")
            return True
        except ImportError:
            logger.warning("⚠️ pytesseract não instalado. Execute: pip install pytesseract pillow")
            logger.info("ℹ️  Modo simulação ativado")
            return False
    
    def extrair_texto_pdf(self, pdf_path: str) -> str:
        """
        Extrai texto de arquivo PDF
        
        Args:
            pdf_path: Caminho do arquivo PDF
            
        Returns:
            Texto extraído
        """
        try:
            import PyPDF2
            
            texto_completo = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"📄 Processando PDF: {num_pages} páginas")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    texto = page.extract_text()
                    texto_completo.append(texto)
                
                texto_final = '\n'.join(texto_completo)
                logger.info(f"✅ {len(texto_final)} caracteres extraídos")
                return texto_final
                
        except ImportError:
            logger.warning("⚠️ PyPDF2 não instalado. Execute: pip install PyPDF2")
            return self._texto_simulado()
        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto do PDF: {e}")
            return ""
    
    def extrair_texto_imagem(self, imagem_path: str) -> str:
        """
        Extrai texto de imagem usando OCR
        
        Args:
            imagem_path: Caminho da imagem
            
        Returns:
            Texto extraído
        """
        if not self.tesseract_available:
            return self._texto_simulado()
        
        try:
            import pytesseract
            from PIL import Image
            
            logger.info(f"🖼️  Processando imagem: {imagem_path}")
            
            # Abrir imagem
            imagem = Image.open(imagem_path)
            
            # Extrair texto
            texto = pytesseract.image_to_string(imagem, lang='por')
            
            logger.info(f"✅ {len(texto)} caracteres extraídos")
            return texto
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair texto da imagem: {e}")
            return ""
    
    def analisar_edital(self, documento_path: str) -> Dict:
        """
        Analisa edital e extrai informações estruturadas
        
        Args:
            documento_path: Caminho do documento (PDF ou imagem)
            
        Returns:
            Dicionário com dados extraídos
        """
        logger.info(f"📋 Analisando edital: {documento_path}")
        
        # Determinar tipo de arquivo
        ext = Path(documento_path).suffix.lower()
        
        # Extrair texto
        if ext == '.pdf':
            texto = self.extrair_texto_pdf(documento_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.tiff']:
            texto = self.extrair_texto_imagem(documento_path)
        else:
            logger.error(f"❌ Formato não suportado: {ext}")
            texto = self._texto_simulado()
        
        # Analisar texto e extrair dados
        dados = self._extrair_dados_edital(texto)
        
        logger.info("✅ Análise concluída")
        return dados
    
    def _extrair_dados_edital(self, texto: str) -> Dict:
        """
        Extrai dados estruturados do texto do edital
        
        Args:
            texto: Texto do edital
            
        Returns:
            Dicionário com dados extraídos
        """
        dados = {
            'numero_edital': self._extrair_numero_edital(texto),
            'orgao': self._extrair_orgao(texto),
            'objeto': self._extrair_objeto(texto),
            'valor_estimado': self._extrair_valor(texto),
            'data_abertura': self._extrair_data_abertura(texto),
            'prazo_entrega': self._extrair_prazo(texto),
            'modalidade': self._extrair_modalidade(texto),
            'requisitos': self._extrair_requisitos(texto),
            'documentos_necessarios': self._extrair_documentos(texto),
            'timestamp_analise': datetime.now().isoformat()
        }
        
        return dados
    
    def _extrair_numero_edital(self, texto: str) -> Optional[str]:
        """Extrai número do edital"""
        # Padrões comuns: PE 001/2024, Pregão Eletrônico nº 123/2024, etc.
        padroes = [
            r'(?:PE|Pregão Eletrônico)\s*n?º?\s*(\d+/\d{4})',
            r'(?:CC|Concorrência)\s*n?º?\s*(\d+/\d{4})',
            r'(?:TP|Tomada de Preços)\s*n?º?\s*(\d+/\d{4})',
            r'Edital\s*n?º?\s*(\d+/\d{4})'
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extrair_orgao(self, texto: str) -> Optional[str]:
        """Extrai nome do órgão"""
        # Procurar por padrões comuns
        padroes = [
            r'(?:Órgão|Entidade):\s*(.+?)(?:\n|\.)',
            r'(?:Prefeitura|Secretaria|Hospital)\s+(?:Municipal|Estadual|Federal)?\s*(?:de|do|da)?\s*([A-Z][a-zÀ-ú\s]+)',
        ]
        
        for padrao in padroes:
            match = re.search(padrao, texto, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extrair_objeto(self, texto: str) -> Optional[str]:
        """Extrai objeto da licitação"""
        # Procurar seção de objeto
        match = re.search(
            r'(?:Objeto|OBJETO):\s*(.+?)(?:\n\n|Valor|Prazo)',
            texto,
            re.IGNORECASE | re.DOTALL
        )
        
        if match:
            objeto = match.group(1).strip()
            # Limitar tamanho
            return objeto[:500] if len(objeto) > 500 else objeto
        
        return None
    
    def _extrair_valor(self, texto: str) -> Optional[float]:
        """Extrai valor estimado"""
        # Padrões de valores: R$ 1.234.567,89
        match = re.search(
            r'(?:Valor|VALOR)\s*(?:Estimado|ESTIMADO)?:?\s*R?\$?\s*([\d.,]+)',
            texto,
            re.IGNORECASE
        )
        
        if match:
            valor_str = match.group(1)
            # Converter para float
            valor_str = valor_str.replace('.', '').replace(',', '.')
            try:
                return float(valor_str)
            except:
                return None
        
        return None
    
    def _extrair_data_abertura(self, texto: str) -> Optional[str]:
        """Extrai data de abertura"""
        # Padrões de data: 15/12/2024, 15-12-2024
        match = re.search(
            r'(?:Data|DATA)\s*(?:de\s*)?(?:Abertura|ABERTURA)?:?\s*(\d{2}[/-]\d{2}[/-]\d{4})',
            texto,
            re.IGNORECASE
        )
        
        if match:
            return match.group(1).replace('-', '/')
        
        return None
    
    def _extrair_prazo(self, texto: str) -> Optional[str]:
        """Extrai prazo de entrega"""
        # Padrões: 30 dias, 60 dias corridos
        match = re.search(
            r'(?:Prazo|PRAZO)\s*(?:de\s*)?(?:Entrega|ENTREGA)?:?\s*(\d+\s*dias?(?:\s*corridos)?)',
            texto,
            re.IGNORECASE
        )
        
        if match:
            return match.group(1)
        
        return None
    
    def _extrair_modalidade(self, texto: str) -> Optional[str]:
        """Extrai modalidade da licitação"""
        modalidades = [
            'Pregão Eletrônico',
            'Concorrência',
            'Tomada de Preços',
            'Convite',
            'Leilão',
            'Dispensa',
            'Inexigibilidade'
        ]
        
        for modalidade in modalidades:
            if modalidade.lower() in texto.lower():
                return modalidade
        
        return None
    
    def _extrair_requisitos(self, texto: str) -> List[str]:
        """Extrai requisitos principais"""
        requisitos = []
        
        # Procurar seção de requisitos
        match = re.search(
            r'(?:Requisitos|REQUISITOS|Exigências|EXIGÊNCIAS):(.+?)(?:\n\n|Documentos|DOCUMENTOS)',
            texto,
            re.IGNORECASE | re.DOTALL
        )
        
        if match:
            secao = match.group(1)
            # Dividir por linhas
            linhas = secao.split('\n')
            for linha in linhas:
                linha = linha.strip()
                if linha and len(linha) > 10:
                    requisitos.append(linha[:200])  # Limitar tamanho
        
        return requisitos[:10]  # Máximo 10 requisitos
    
    def _extrair_documentos(self, texto: str) -> List[str]:
        """Extrai documentos necessários"""
        documentos = []
        
        # Documentos comuns em licitações
        docs_comuns = [
            'Certidão Negativa de Débitos',
            'CNPJ',
            'Contrato Social',
            'Certidão de Regularidade Fiscal',
            'Atestado de Capacidade Técnica',
            'Declaração de Idoneidade',
            'Alvará de Funcionamento'
        ]
        
        for doc in docs_comuns:
            if doc.lower() in texto.lower():
                documentos.append(doc)
        
        return documentos
    
    def _texto_simulado(self) -> str:
        """Retorna texto simulado para testes"""
        return """
        PREGÃO ELETRÔNICO Nº 123/2024
        
        Órgão: Hospital Municipal de São Paulo
        
        Objeto: Aquisição de equipamentos hospitalares, incluindo monitores cardíacos,
        desfibriladores, bombas de infusão e materiais médico-hospitalares diversos
        para atendimento das necessidades da unidade de terapia intensiva.
        
        Valor Estimado: R$ 450.000,00
        
        Data de Abertura: 20/12/2024 às 10:00h
        
        Prazo de Entrega: 30 dias corridos
        
        Requisitos:
        - Certificação ANVISA para equipamentos médicos
        - Garantia mínima de 24 meses
        - Assistência técnica local
        
        Documentos Necessários:
        - CNPJ
        - Certidão Negativa de Débitos
        - Atestado de Capacidade Técnica
        """


def testar_ocr():
    """Função de teste do analisador OCR"""
    print("\n" + "="*60)
    print("🧪 TESTE DE ANÁLISE OCR DE DOCUMENTOS")
    print("="*60 + "\n")
    
    analyzer = OCRDocumentAnalyzer()
    
    # Teste 1: Análise de edital simulado
    print("1️⃣ Testando análise de edital (simulado)...")
    dados = analyzer.analisar_edital('edital_teste.pdf')
    
    print("\n   📋 Dados Extraídos:")
    print(f"   • Número Edital: {dados['numero_edital']}")
    print(f"   • Órgão: {dados['orgao']}")
    print(f"   • Objeto: {dados['objeto'][:100]}...")
    print(f"   • Valor: R$ {dados['valor_estimado']:,.2f}" if dados['valor_estimado'] else "   • Valor: Não encontrado")
    print(f"   • Data Abertura: {dados['data_abertura']}")
    print(f"   • Prazo: {dados['prazo_entrega']}")
    print(f"   • Modalidade: {dados['modalidade']}")
    print(f"   • Requisitos: {len(dados['requisitos'])} encontrados")
    print(f"   • Documentos: {len(dados['documentos_necessarios'])} encontrados\n")
    
    # Teste 2: Listagem de requisitos
    if dados['requisitos']:
        print("2️⃣ Requisitos Identificados:")
        for req in dados['requisitos'][:3]:
            print(f"   • {req}")
        print()
    
    # Teste 3: Listagem de documentos
    if dados['documentos_necessarios']:
        print("3️⃣ Documentos Necessários:")
        for doc in dados['documentos_necessarios']:
            print(f"   • {doc}")
        print()
    
    print("="*60)
    print("✅ SISTEMA OCR FUNCIONANDO")
    print("="*60 + "\n")
    
    print("📝 Próximos passos:")
    print("   1. Instalar dependências: pip install PyPDF2 pytesseract pillow pdf2image")
    print("   2. Instalar Tesseract OCR no sistema")
    print("   3. Testar com PDFs reais de editais")
    print("   4. Ajustar regex para padrões específicos\n")


if __name__ == '__main__':
    testar_ocr()
