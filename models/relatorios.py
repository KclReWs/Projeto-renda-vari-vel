from fpdf import FPDF
from typing import Dict

class RelatorioPDF(FPDF):
    def __init__(self):
        super().__init__()

    def gerar_relatorio(self, dados: Dict) -> bytes:
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "Resumo do Período", ln=True)

        self.set_font('Arial', '', 10)
        for item, valor in dados['resumo'].items():
            self.cell(0, 8, f"{item.replace('_', ' ').title()}: R$ {valor:,.2f}", ln=True)

        # Operações
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "Operações do Período", ln=True)

        for op in dados['operacoes']:
            self.set_font('Arial', '', 10)
            texto = (f"{op['data']} - {op['tipo']} {op['quantidade']} "
                     f"{op['codigo']} @ R$ {op['preco']:,.2f}")
            self.cell(0, 8, texto, ln=True)

        # Impostos
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "Impostos Devidos", ln=True)

        for item, valor in dados['impostos'].items():
            self.set_font('Arial', '', 10)
            self.cell(0, 8, f"{item.replace('_', ' ').title()}: R$ {valor:,.2f}", ln=True)

        try:
            return self.output(dest='S').encode('latin1')
        except Exception as e:
            print(f"Erro ao gerar relatório PDF: {e}")
            return b''