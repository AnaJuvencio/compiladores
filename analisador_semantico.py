import sys
from ast_alguma import *

# Definição dos tipos básicos da linguagem
class Type:
    def __init__(self, name):
        self.typename = name
    def __repr__(self):
        return self.typename

class UChuckType(Type):
    def __init__(self, name, binary_ops=set(), unary_ops=set(), rel_ops=set()):
        super().__init__(name)
        self.binary_ops = binary_ops
        self.unary_ops = unary_ops
        self.rel_ops = rel_ops

# Instâncias dos tipos para usar no resto do código
IntType = UChuckType(
    "int",
    unary_ops  = {"-", "+", "!"},
    binary_ops = {"+", "-", "*", "/", "%"},
    rel_ops    = {"==", "!=", "<", ">", "<=", ">=", "&&", "||"},
)
FloatType = UChuckType(
    "float",
    unary_ops  = {"-", "+"},
    binary_ops = {"+", "-", "*", "/", "%"},
    rel_ops    = {"==", "!=", "<", ">", "<=", ">="},
)
StringType = UChuckType(
    "string",
    binary_ops = {"+"},
    rel_ops    = {"==", "!="},
)

# Tabela de símbolos (usada para armazenar as variáveis e tipos)
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    def add(self, name, value):
        self.symbols[name] = value
    def lookup(self, name):
        value = self.symbols.get(name, None)
        if value is None and self.parent is not None:
            return self.parent.lookup(name)
        return value

# Visitor principal, vai passar por cada nó da AST
class Visitor(NodeVisitor):
    def __init__(self):
        self.symtab = None
        # Só esses tipos que aceito aqui 
        self.typemap = {
            "int": IntType,
            "float": FloatType,
            "string": StringType,
        }

    # Função para dar erro semântico, já imprime na tela e para tudo
    def _assert_semantic(self, condition, msg_code, coord, name="", ltype="", rtype=""):
        msgs = {
             1: f"'{name}' is not defined",
             2: f"Cannot assign type '{rtype}' to type '{ltype}'",
             3: f"Binary operator '{name}' does not have matching LHS/RHS types",
             4: f"Binary operator '{name}' is not supported by type '{ltype}'",
             5: "Break/Continue statement must be inside a loop",
             6: f"The condition expression must be of type 'int', not type '{ltype}'",
             7: "Expression is not of basic type",
             8: f"Right-side operand is not a variable",
             9: f"Name '{name}' is already defined in this scope",
            10: f"Unary operator '{name}' is not supported by type '{ltype}'",
        }
        if not condition:
            print("SemanticError: %s %s" % (msgs.get(msg_code), coord), file=sys.stdout)
            sys.exit(1)

    def visit_Program(self, node):
        # Cria uma tabela de símbolos nova para esse programa
        node.attrs['symtab'] = SymbolTable()
        self.symtab = node.attrs['symtab']
        # Lista para controlar os loops (break/continue)
        self.symtab.add('loops', [])
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_VarDecl(self, node):
        var_name = getattr(node, 'name', None)
        if hasattr(node, 'name') and hasattr(node.name, 'name'):
            var_name = node.name.name
        self._assert_semantic(
            var_name is not None,
            1, node.coord,
            name="VarDecl"
        )
        self._assert_semantic(
            self.symtab.lookup(var_name) is None,
            9, node.coord,
            name=var_name
        )
        self.visit(node.dtype)
        var_type = node.dtype.attrs.get('uchuck_type')
        # Bloqueia tipo inválido
        self._assert_semantic(
            var_type in self.typemap.values(),
            1, node.coord,
            name=str(var_type)
        )
        node.attrs['uchuck_type'] = var_type
        self.symtab.add(var_name, node)



    def visit_Type(self, node):
        type_name = getattr(node, 'typename', None) or getattr(node, 'name', None)
        self._assert_semantic(type_name in self.typemap, 1, node.coord, name=type_name)
        node.attrs['uchuck_type'] = self.typemap[type_name]

    def visit_Location(self, node):
        varname = node.name
        decl = self.symtab.lookup(varname)
        self._assert_semantic(decl is not None, 1, node.coord, name=varname)
        node.attrs['defn'] = decl
        node.attrs['uchuck_type'] = decl.attrs['uchuck_type']


    def visit_Literal(self, node):
        type_name = getattr(node, 'type', None)
        if type_name == 'bool':  # trata bool como int
            type_name = 'int'
        # Bloqueia literais de tipo desconhecido
        self._assert_semantic(
            type_name in self.typemap,
            1, node.coord,
            name=type_name
        )
        node.attrs['uchuck_type'] = self.typemap[type_name]


    def visit_BinaryOp(self, node):
        # Visita os filhos
        self.visit(node.left)
        self.visit(node.right)
        
        # Recupera tipos
        ltype = node.left.attrs.get('uchuck_type')
        rtype = node.right.attrs.get('uchuck_type')

        # Garante que ambos os tipos estão definidos
        self._assert_semantic(
            ltype is not None and rtype is not None,
            3, node.coord,
            name=getattr(node, 'op', '?'),
            ltype=str(ltype),
            rtype=str(rtype)
        )

        # Pega o operador (adapta ao nome da AST)
        op = getattr(node, 'op', getattr(node, 'operator', None))
        self._assert_semantic(
            op is not None,
            4, node.coord,
            name="(undefined op)",
            ltype=str(ltype)
        )

        # Tipos precisam ser idênticos (não aceita int + float, por exemplo)
        self._assert_semantic(
            ltype == rtype,
            3, node.coord,
            name=op,
            ltype=str(ltype),
            rtype=str(rtype)
        )

        # Aceita só tipos conhecidos (evita pegar tipos "None")
        self._assert_semantic(
            ltype in self.typemap.values(),
            3, node.coord,
            name=op,
            ltype=str(ltype)
        )

        # Operador precisa ser suportado por esse tipo!
        if op in getattr(ltype, 'binary_ops', set()):
            node.attrs['uchuck_type'] = ltype
        elif op in getattr(ltype, 'rel_ops', set()):
            node.attrs['uchuck_type'] = self.typemap['int']
        else:
            self._assert_semantic(
                False, 4, node.coord, name=op, ltype=str(ltype)
            )



    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        operand_type = node.operand.attrs.get('uchuck_type')
        op = getattr(node, 'op', None)
        self._assert_semantic(
            operand_type is not None and hasattr(operand_type, 'unary_ops'),
            10, node.coord, name=op, ltype=str(operand_type)
        )
        self._assert_semantic(
            op in operand_type.unary_ops,
            10, node.coord, name=op, ltype=str(operand_type)
        )
        node.attrs['uchuck_type'] = operand_type


    def visit_ChuckOp(self, node):
        self.visit(node.expression)
        expr_type = node.expression.attrs.get('uchuck_type')
        self.visit(node.location)
        loc_type = node.location.attrs.get('uchuck_type')

        # Só permite atribuição para VarDecl ou Location
        is_assignable = type(node.location).__name__ in ('Location', 'VarDecl')
        self._assert_semantic(is_assignable, 8, node.coord)

        # Tipos precisam bater e não podem ser None!
        self._assert_semantic(
            expr_type is not None and loc_type is not None and loc_type == expr_type,
            2, node.coord, ltype=str(loc_type), rtype=str(expr_type)
        )
        node.attrs['uchuck_type'] = loc_type


    def visit_PrintStatement(self, node):
        self.visit(node.expression)
        expr_type = node.expression.attrs.get('uchuck_type')
        self._assert_semantic(
            expr_type in [self.typemap['int'], self.typemap['float'], self.typemap['string']],
            7, node.coord
        )
        node.attrs['uchuck_type'] = expr_type



    def visit_ExpressionAsStatement(self, node):
        if node.expression:
            self.visit(node.expression)

    def visit_IfStatement(self, node):
        self.visit(node.test)
        test_type = node.test.attrs['uchuck_type']
        self._assert_semantic(test_type == IntType, 6, node.coord, ltype=str(test_type))
        self.visit(node.consequence)
        if node.alternative:
            self.visit(node.alternative)

    def visit_WhileStatement(self, node):
        loops = self.symtab.lookup('loops')
        loops.append(node)
        self.visit(node.test)
        test_type = node.test.attrs['uchuck_type']
        self._assert_semantic(test_type == IntType, 6, node.coord, ltype=str(test_type))
        self.visit(node.body)
        loops.pop()

    def visit_BreakStatement(self, node):
        loops = self.symtab.lookup('loops')
        self._assert_semantic(
            isinstance(loops, list) and len(loops) > 0,
            5, node.coord
        )
        node.attrs['loop'] = loops[-1]


    def visit_ContinueStatement(self, node):
        loops = self.symtab.lookup('loops')
        self._assert_semantic(len(loops) > 0, 5, node.coord)
        node.attrs['loop'] = loops[-1]

    def visit_ExprList(self, node):
        for expr in node.exprs:
            self.visit(expr)
        if node.exprs:
            node.attrs['uchuck_type'] = node.exprs[-1].attrs['uchuck_type']
