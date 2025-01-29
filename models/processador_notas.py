import re
from typing import Dict
from datetime import datetime
import logging
import PyPDF2
from io import BytesIO

logger = logging.getLogger(__name__)

class ProcessadorNotas:
    def __init__(self, database):
        self.db = database

    def processar_nota(self, arquivo_pdf, corretora: str) -> Dict:
        """Processa uma nota de corretagem detectando a corretora e extraindo os dados."""
        # Detectar a corretora e chamar o método de processamento correspondente
        processadores = {
            'CLEAR': self._processar_clear,
            'XP': self._processar_xp,
            'RICO': self._processar_rico,
            'AGORA': self._processar_agora,
            # Adicione outras corretoras aqui
        }

        if corretora not in processadores:
            raise ValueError(f"Corretora {corretora} não suportada.")

        # Abrir o arquivo PDF usando PyPDF2
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(arquivo_pdf.read()))
            texto_completo = ""
            for page in pdf_reader.pages:
                texto_completo += page.extract_text()
            logger.debug(f"Texto completo extraído do PDF: {texto_completo}")
            return processadores[corretora](texto_completo)
        except Exception as e:
            raise ValueError(f"Erro ao abrir o arquivo PDF: {e}")

    def salvar_operacoes(self, dados_nota: Dict) -> bool:
        """Salva as operações extraídas no banco de dados."""
        try:
            for operacao in dados_nota['operacoes']:
                query = '''
                    INSERT INTO operacoes (corretora, tipo, ativo, quantidade, preco, data, numero_nota)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                '''
                self.db.execute_query(query, (
                    dados_nota['corretora'],
                    operacao['tipo'],
                    operacao['ativo'],
                    operacao['quantidade'],
                    operacao['preco'],
                    dados_nota['data_pregao'],
                    dados_nota.get('numero_nota', None)  # Use None if 'numero_nota' is not present
                ))
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar operações: {e}")
            return False

    def _processar_clear(self, texto_completo) -> Dict:
        # Implementação específica para notas da Clear
        # ...
        pass

    def _processar_xp(self, texto_completo) -> Dict:
        dados_nota = {
            'corretora': 'XP',
            'operacoes': [],
            'taxas': {},
            'data_pregao': None,
            'numero_nota': None
        }

        # Extrair data do pregão
        padrao_data = r'Data pregão:\s*(\d{2}/\d{2}/\d{4})'
        if match := re.search(padrao_data, texto_completo):
            dados_nota['data_pregao'] = datetime.strptime(match.group(1), '%d/%m/%Y')

        # Tentar extrair o número da nota
        padrao_nota = r'Nr\. nota:\s*(\d+)'
        if match := re.search(padrao_nota, texto_completo):
            dados_nota['numero_nota'] = match.group(1)

        # Extrair operações
        padrao_operacao = r'([A-Z0-9]+)\s+([CV])\s+(\d+)\s+([\d.,]+)'
        for match in re.finditer(padrao_operacao, texto_completo):
            ativo, tipo, quantidade, preco = match.groups()
            operacao = {
                'tipo': 'Compra' if tipo == 'C' else 'Venda',
                'ativo': ativo,
                'quantidade': int(quantidade),
                'preco': float(preco.replace('.', '').replace(',', '.'))
            }
            dados_nota['operacoes'].append(operacao)

        if not dados_nota['operacoes']:
            logger.debug("Nenhuma operação encontrada.")

        # Extrair taxas
        dados_nota['taxas'] = self._extrair_taxas(texto_completo)

        logger.debug(f"Número da nota extraído: {dados_nota['numero_nota']}")
        logger.debug(f"Data do pregão extraída: {dados_nota['data_pregao']}")
        logger.debug(f"Operações extraídas: {dados_nota['operacoes']}")
        logger.debug(f"Taxas extraídas: {dados_nota['taxas']}")

        return dados_nota

    def _processar_rico(self, texto_completo) -> Dict:
        dados_nota = {
            'corretora': 'RICO',
            'operacoes': [],
            'taxas': {},
            'data_pregao': None,
            'numero_nota': None
        }

        # Extrair data do pregão
        padrao_data = r'Data pregão:\s*(\d{2}/\d{2}/\d{4})'
        if match := re.search(padrao_data, texto_completo):
            dados_nota['data_pregao'] = datetime.strptime(match.group(1), '%d/%m/%Y')
        else:
            logger.debug("Data do pregão não encontrada.")

        # Tentar extrair o número da nota
        padrao_nota = r'Nr\. nota:\s*(\d+)'
        if match := re.search(padrao_nota, texto_completo):
            dados_nota['numero_nota'] = match.group(1)
        else:
            logger.debug("Número da nota não encontrado.")

        # Extrair operações
        padrao_operacao = r'(\d+)\s+(\d+)\s+([CV])\s+(VISTA|FRACIONARIO)\s+(\w+)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)'
        for match in re.finditer(padrao_operacao, texto_completo):
            _, _, tipo, mercado, ativo, quantidade, preco, valor = match.groups()
            operacao = {
                'tipo': 'Compra' if tipo == 'C' else 'Venda',
                'ativo': ativo,
                'quantidade': int(quantidade),
                'preco': float(preco.replace('.', '').replace(',', '.')),
                'valor': float(valor.replace('.', '').replace(',', '.')),
                'mercado': mercado
            }
            dados_nota['operacoes'].append(operacao)

        if not dados_nota['operacoes']:
            logger.debug("Nenhuma operação encontrada.")

        # Extrair taxas
        dados_nota['taxas'] = self._extrair_taxas(texto_completo)

        logger.debug(f"Número da nota extraído: {dados_nota['numero_nota']}")
        logger.debug(f"Data do pregão extraída: {dados_nota['data_pregao']}")
        logger.debug(f"Operações extraídas: {dados_nota['operacoes']}")
        logger.debug(f"Taxas extraídas: {dados_nota['taxas']}")

        return dados_nota

    def _processar_agora(self, texto_completo) -> Dict:
        dados_nota = {
            'corretora': 'AGORA',
            'operacoes': [],
            'taxas': {},
            'data_pregao': None,
            'numero_nota': None
        }

        # Extrair data do pregão
        padrao_data = r'Data pregão:\s*(\d{2}/\d{2}/\d{4})'
        if match := re.search(padrao_data, texto_completo):
            dados_nota['data_pregao'] = datetime.strptime(match.group(1), '%d/%m/%Y')
        else:
            logger.debug("Data do pregão não encontrada.")

        # Tentar extrair o número da nota
        padrao_nota = r'Nr\. nota:\s*(\d+)'
        if match := re.search(padrao_nota, texto_completo):
            dados_nota['numero_nota'] = match.group(1)
        else:
            logger.debug("Número da nota não encontrado.")

        # Extrair operações
        padrao_operacao = r'(\d+)\s+(\d+)\s+([CV])\s+(VISTA|FRACIONARIO)\s+(\w+)\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)'
        for match in re.finditer(padrao_operacao, texto_completo):
            _, _, tipo, mercado, ativo, quantidade, preco, valor = match.groups()
            operacao = {
                'tipo': 'Compra' if tipo == 'C' else 'Venda',
                'ativo': ativo,
                'quantidade': int(quantidade),
                'preco': float(preco.replace('.', '').replace(',', '.')),
                'valor': float(valor.replace('.', '').replace(',', '.')),
                'mercado': mercado
            }
            dados_nota['operacoes'].append(operacao)

        if not dados_nota['operacoes']:
            logger.debug("Nenhuma operação encontrada.")

        # Extrair taxas
        dados_nota['taxas'] = self._extrair_taxas(texto_completo)

        logger.debug(f"Número da nota extraído: {dados_nota['numero_nota']}")
        logger.debug(f"Data do pregão extraída: {dados_nota['data_pregao']}")
        logger.debug(f"Operações extraídas: {dados_nota['operacoes']}")
        logger.debug(f"Taxas extraídas: {dados_nota['taxas']}")

        return dados_nota

    def _extrair_taxas(self, texto: str) -> Dict:
        """Extrai as taxas do texto completo da nota de corretagem."""
        taxas = {
            'Taxa de liquidação': r'Taxa de liquidação\s+([\d.,]+)',
            'Taxa de registro': r'Taxa de Registro\s+([\d.,]+)',
            'Emolumentos': r'Emolumentos\s+([\d.,]+)',
            'Taxa operacional': r'Taxa Operacional\s+([\d.,]+)',
            'Execução': r'Execução\s+([\d.,]+)',
            'Taxa de custódia': r'Taxa de Custódia\s+([\d.,]+)',
            'Impostos': r'Impostos\s+([\d.,]+)',
            'IRRF': r'I.R.R.F. s/ operações\s+([\d.,]+)',
            'Outros': r'Outros\s+([\d.,]+)'
        }

        taxas_extraidas = {}
        for nome_taxa, padrao in taxas.items():
            if match := re.search(padrao, texto):
                valor = float(match.group(1).replace('.', '').replace(',', '.'))
                taxas_extraidas[nome_taxa] = valor

        return taxas_extraidas