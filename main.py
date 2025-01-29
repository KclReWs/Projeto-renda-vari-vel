from interface.app import App
from database.database import Database
from models.processador_notas import ProcessadorNotas
from models.operacoes import Operacoes

def main():
    try:
        # Inicializa o banco de dados
        database = Database()

        # Inicializa o processador de notas
        processador_notas = ProcessadorNotas(database)

        # Inicializa a classe de operações
        operacoes = Operacoes(database)

        # Inicializa o aplicativo
        app = App(processador_notas, operacoes)
        app.executar()
    except Exception as e:
        print(f"Erro ao iniciar o aplicativo: {e}")

if __name__ == "__main__":
    main()