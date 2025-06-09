from analisador_sintatico import UChuckParser, build_tree


def run_test(source_code, expected_output):
    parser = UChuckParser()
    ast = parser.parse(source_code)  # Gera a árvore em formato tuplas/listas

    output = build_tree(ast)  # Converte a árvore para string formatada

    if output.strip() == expected_output.strip():
        print("✅ Test passou!")
    else:
        print("❌ Test falhou!")
        print("--- Entrada ---")
        print(source_code)
        print("--- Esperado ---")
        print(expected_output)
        print("--- Recebido ---")
        print(output)

        #print("\n--- Diferenças (diff) ---")

        print("\n--- Análise detalhada das linhas ---")
        print("Esperado:")
        for i, line in enumerate(expected_output.splitlines(), 1):
            print(f"{i:03}: {repr(line)} (len={len(line)})")
        print("Recebido:")
        for i, line in enumerate(output.splitlines(), 1):
            print(f"{i:03}: {repr(line)} (len={len(line)})")

# Testes aqui
tests = [
    (
        """/* print values of factorials */
1 => int n;
1 => int value;

while( n < 10 )
{
	value * n => value;
	<<< value >>>;
	n + 1 => n;
}
""",
    """┬─ program
└─┬─┬─ expr
  │ └─┬─ chuck_op @ 2:1
  │   ├─┬─ var_decl
  │   │ ├─ type: int @ 2:6
  │   │ └─ id: n @ 2:10
  │   └─ literal: int, 1 @ 2:1
  ├─┬─ expr
  │ └─┬─ chuck_op @ 3:1
  │   ├─┬─ var_decl
  │   │ ├─ type: int @ 3:6
  │   │ └─ id: value @ 3:10
  │   └─ literal: int, 1 @ 3:1
  └─┬─ while @ 5:1
    ├─┬─ binary_op: < @ 5:8
    │ ├─ location: n @ 5:8
    │ └─ literal: int, 10 @ 5:12
    └─┬─ stmt_list @ 6:1
      └─┬─┬─ expr
        │ └─┬─ chuck_op @ 7:2
        │   ├─ location: value @ 7:15
        │   └─┬─ binary_op: * @ 7:2
        │     ├─ location: value @ 7:2
        │     └─ location: n @ 7:10
        ├─┬─ expr
        │ └─┬─ print @ 8:2
        │   └─ location: value @ 8:6
        └─┬─ expr
          └─┬─ chuck_op @ 9:2
            ├─ location: n @ 9:11
            └─┬─ binary_op: + @ 9:2
              ├─ location: n @ 9:2
              └─ literal: int, 1 @ 9:6
"""
    ),
]

for i, (input_code, expected) in enumerate(tests, 1):
    print(f"\n--- Rodando teste #{i} ---")
    run_test(input_code, expected)
