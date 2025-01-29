from typing import List, Dict
from datetime import datetime

ISENCAO_SWING_TRADE = 20000  # Define the exemption limit for swing trade
ALIQUOTA_SWING_TRADE = 0.15  # Define the tax rate for swing trade

class Impostos:
    def __init__(self, operacoes: List[Dict]):
        self.operacoes = operacoes

    def calcular_imposto(self) -> Dict:
        """Calcula o imposto devido sobre as operações."""
        total_vendas = sum(op['valor'] for op in self.operacoes if op['tipo'] == 'Venda')
        total_compras = sum(op['valor'] for op in self.operacoes if op['tipo'] == 'Compra')
        lucro_prejuizo = total_vendas - total_compras

        if total_vendas <= ISENCAO_SWING_TRADE:
            imposto_devido = 0
        else:
            imposto_devido = lucro_prejuizo * ALIQUOTA_SWING_TRADE

        return {
            'total_vendas': total_vendas,
            'total_compras': total_compras,
            'lucro_prejuizo': lucro_prejuizo,
            'imposto_devido': imposto_devido
        }