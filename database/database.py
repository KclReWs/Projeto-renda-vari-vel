import sqlite3
import os

class Database:
    def __init__(self, db_path='investimentos.db'):
        self.db_path = db_path
        self.conn = self._connect()

    def _connect(self):
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def execute_query(self, query, params=None):
        try:
            with self.conn:
                cursor = self.conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Erro ao executar query: {e}")
            return []

    def close(self):
        if self.conn:
            try:
                self.conn.close()
            except sqlite3.Error as e:
                print(f"Erro ao fechar a conexão com o banco de dados: {e}")

    def __del__(self):
        self.close()