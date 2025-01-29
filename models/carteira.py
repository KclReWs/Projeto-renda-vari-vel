import pandas as pd

class Operacoes:
    def __init__(self, db):
        self.db = db

    def obter_operacoes(self):
        query = '''
        SELECT o.codigo, o.tipo, o.quantidade, o.preco, o.data, o.corretagem
        FROM operacoes o
        ORDER BY o.data DESC
        '''
        try:
            resultado = self.db.execute_query(query)
        except Exception as e:
            print(f"Erro ao executar query: {e}")
            return pd.DataFrame()

        operacoes = []
        for codigo, tipo, quantidade, preco, data, corretagem in resultado:
            operacoes.append({
                'codigo': codigo,
                'tipo': tipo,
                'quantidade': quantidade,
                'preco': preco,
                'data': data,
                'corretagem': corretagem,
                'valor_total': quantidade * preco
            })

        return pd.DataFrame(operacoes)