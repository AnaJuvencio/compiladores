import sys
from analisador_lexico import main

# Criação do arquivo de teste no mesmo diretório
test_file = "test.uck"

# Executa o analisador léxico no arquivo de teste
if __name__ == "__main__":
    sys.argv = [test_file]  # Simula o argumento de linha de comando
    main(sys.argv)