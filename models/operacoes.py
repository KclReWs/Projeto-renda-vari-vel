from typing import Dict
from database.database import Database
from datetime import datetime
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Operacoes:
    def __init__(self, database: Database):
        self.db = database

        # Create tables if they do not exist
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS operacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ativo_id INTEGER,
                tipo TEXT,
                quantidade INTEGER,
                preco REAL,
                data TEXT,
                corretagem REAL,
                valor REAL,
                preco_venda REAL,
                preco_compra REAL,
                FOREIGN KEY (ativo_id) REFERENCES ativos(id)
            );
        ''')
        self.db.execute_query('''
            CREATE TABLE IF NOT EXISTS ativos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE
            );
        ''')

    def registrar_operacao(self, dados_operacao: Dict) -> bool:
        """Registra uma nova operação"""
        try:
            # Primeiro, verifica se o ativo existe
            ativo_id = self.obter_ativo_id(dados_operacao['codigo'])
            if not ativo_id:
                # Se não existe, cria o ativo
                self.criar_ativo(dados_operacao['codigo'])
                ativo_id = self.obter_ativo_id(dados_operacao['codigo'])

            # Registra a operação
            query = '''
                INSERT INTO operacoes 
                (ativo_id, tipo, quantidade, preco, data, corretagem, valor, preco_venda, preco_compra)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            self.db.execute_query(query, (
                ativo_id,
                dados_operacao['tipo'],
                dados_operacao['quantidade'],
                dados_operacao['preco'],
                dados_operacao['data'],
                dados_operacao.get('corretagem', 0),
                dados_operacao.get('valor', 0),
                dados_operacao.get('preco_venda', 0),
                dados_operacao.get('preco_compra', 0)
            ))
            logger.info(f"Operação registrada com sucesso: {dados_operacao}")
            return True
        except Exception as e:
            logger.error(f"Erro ao registrar operação: {e}")
            return False

    def obter_ativo_id(self, codigo: str) -> int:
        """Obtém o ID do ativo pelo código"""
        query = '''
        SELECT id FROM ativos WHERE codigo = ?
        '''
        try:
            resultado = self.db.execute_query(query, (codigo,))
            if resultado:
                return resultado[0]['id']
            else:
                return None
        except Exception as e:
            logger.error(f"Erro ao obter ID do ativo: {e}")
            return None

    def criar_ativo(self, codigo: str) -> bool:
        """Cria um novo ativo"""
        query = '''
        INSERT INTO ativos (codigo) VALUES (?)
        '''
        try:
            self.db.execute_query(query, (codigo,))
            logger.info(f"Ativo criado com sucesso: {codigo}")
            return True
        except Exception as e:
            logger.error(f"Erro ao criar ativo: {e}")
            return False

    def obter_operacoes(self, data_inicio, data_fim):
        query = '''
        SELECT * FROM operacoes WHERE data BETWEEN ? AND ?
        '''
        return pd.read_sql_query(query, self.db.connection, params=(data_inicio, data_fim))

    def obter_todas_operacoes(self):
        query = '''
        SELECT * FROM operacoes
        '''
        return pd.read_sql_query(query, self.db.connection)

    def calcular_saldo_total(self):
        query = '''
        SELECT SUM(valor) as saldo_total FROM operacoes
        '''
        resultado = self.db.execute_query(query)
        return resultado[0]['saldo_total'] if resultado else 0

    def calcular_lucro_prejuizo(self):
        query = '''
        SELECT SUM((preco_venda - preco_compra) * quantidade) as lucro_prejuizo FROM operacoes
        '''
        resultado = self.db.execute_query(query)
        return resultado[0]['lucro_prejuizo'] if resultado else 0