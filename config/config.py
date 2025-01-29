import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do banco de dados
DATABASE_PATH = os.getenv('DATABASE_PATH', 'investimentos.db')

# Configurações da aplicação
APP_NAME = "EVS Controle de investimentos em ações"
VERSION = "1.0.0"

# Configurações de corretoras suportadas
CORRETORAS = ["CLEAR", "XP", "RICO", "NUINVEST", "AGORA"]

# Configurações de tipos de operações
TIPOS_OPERACOES = ["Compra", "Venda"]

# Configurações de eventos corporativos
TIPOS_EVENTOS = ["DIVIDENDO", "JCP", "DESDOBRAMENTO", "GRUPAMENTO"]

# Configurações de impostos
ALIQUOTA_DAY_TRADE = 0.20
ALIQUOTA_SWING_TRADE = 0.15
ISENCAO_SWING_TRADE = 20000  # Isenção para vendas até R$ 20.000,00 no mês