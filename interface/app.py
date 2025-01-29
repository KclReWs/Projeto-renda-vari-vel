import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from models.relatorios import RelatorioPDF
from models.impostos import Impostos

class App:
    def __init__(self, processador_notas, operacoes):
        self.processador_notas = processador_notas
        self.operacoes = operacoes

    def executar(self):
        st.title("EVS Controle de Investimentos em Ações")

        # Seção de upload de notas
        st.header("Upload de Notas de Corretagem")
        corretora = st.selectbox(
            "Selecione a corretora",
            ["CLEAR", "XP", "RICO", "NUINVEST", "AGORA"]
        )

        arquivos = st.file_uploader(
            "Selecione as notas de corretagem (PDF)",
            type=['pdf'],
            accept_multiple_files=True
        )

        if st.button("Processar Notas") and arquivos:
            with st.spinner("Processando notas..."):
                for arquivo in arquivos:
                    try:
                        dados_nota = self.processador_notas.processar_nota(arquivo, corretora)
                        for operacao in dados_nota['operacoes']:
                            operacao['codigo'] = operacao['ativo']  # Adiciona o código do ativo à operação
                            if self.operacoes.registrar_operacao(operacao):
                                st.success(f"Operação {operacao['tipo']} de {operacao['quantidade']} {operacao['ativo']} registrada com sucesso!")
                            else:
                                st.error(f"Erro ao registrar operação {operacao['tipo']} de {operacao['quantidade']} {operacao['ativo']}")

                        # Mostrar resumo da nota
                        st.subheader(f"Resumo da Nota {dados_nota['numero_nota']}")

                        # Tabela de operações
                        df_operacoes = pd.DataFrame(dados_nota['operacoes'])
                        st.write("Operações:")
                        st.dataframe(df_operacoes)

                        # Taxas
                        st.write("Taxas:")
                        for taxa, valor in dados_nota['taxas'].items():
                            st.write(f"{taxa}: R$ {valor:.2f}")

                    except Exception as e:
                        st.error(f"Erro ao processar arquivo: {str(e)}")

        # Seção de visualização de operações
        st.header("Visualização de Operações")
        filtro_data_inicio = st.date_input("Data de início")
        filtro_data_fim = st.date_input("Data de fim")

        if st.button("Filtrar Operações"):
            df_operacoes = self.operacoes.obter_operacoes(filtro_data_inicio, filtro_data_fim)
            st.write("Operações filtradas:")
            st.dataframe(df_operacoes)

            # Resumo por ativo
            st.subheader("Resumo por Ativo")
            resumo_ativos = df_operacoes.groupby('ativo').agg({
                'quantidade': 'sum',
                'preco': 'mean',
                'valor': 'sum'
            }).reset_index()
            st.dataframe(resumo_ativos)

            # Gráfico de desempenho
            st.subheader("Gráfico de Desempenho")
            fig, ax = plt.subplots()
            for ativo in resumo_ativos['ativo']:
                df_ativo = df_operacoes[df_operacoes['ativo'] == ativo]
                ax.plot(df_ativo['data'], df_ativo['valor'], label=ativo)
            ax.legend()
            st.pyplot(fig)

        # Seção de exportação de dados
        st.header("Exportação de Dados")
        if st.button("Exportar para CSV"):
            df_operacoes = self.operacoes.obter_todas_operacoes()
            df_operacoes.to_csv("operacoes.csv", index=False)
            st.success("Dados exportados com sucesso!")

        # Seção de saldo total e lucro/prejuízo
        st.header("Saldo Total e Lucro/Prejuízo")
        saldo_total = self.operacoes.calcular_saldo_total()
        lucro_prejuizo = self.operacoes.calcular_lucro_prejuizo()
        st.write(f"Saldo Total: R$ {saldo_total:.2f}")
        st.write(f"Lucro/Prejuízo: R$ {lucro_prejuizo:.2f}")

        # Seção de geração de relatórios
        st.header("Geração de Relatórios")
        if st.button("Gerar Relatório PDF"):
            dados = {
                'resumo': {
                    'saldo_total': saldo_total,
                    'lucro_prejuizo': lucro_prejuizo
                },
                'operacoes': df_operacoes.to_dict(orient='records'),
                'impostos': Impostos(df_operacoes.to_dict(orient='records')).calcular_imposto()
            }
            relatorio_pdf = RelatorioPDF()
            pdf_bytes = relatorio_pdf.gerar_relatorio(dados)
            st.download_button(
                label="Baixar Relatório PDF",
                data=pdf_bytes,
                file_name="relatorio.pdf",
                mime="application/pdf"
            )

