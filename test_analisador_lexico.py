import sys
from analisador_lexico import main

# Criação do arquivo de teste no mesmo diretório
test_file = "test.uck"
with open(test_file, "w") as f:
    f.write("""/* print values of factorials */
1 => int n;
1 => int value;

while( n < 10 )
{
    value * n => value;
    <<< value >>>;
    n + 1 => n;
}""")

# Executa o analisador léxico no arquivo de teste
if __name__ == "__main__":
    sys.argv = [test_file]  # Simula o argumento de linha de comando
    main(sys.argv)