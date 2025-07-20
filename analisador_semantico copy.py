import sys
from ast_alguma import *  

# === Tipos básicos da linguagem (baseado no PDF) ===

class SemanticType:
    """
    Classe base para representar tipos.
    """
    def __init__(self, name):
        self.typename = name

    def __repr__(self):
        return self.typename

class UChuckType(SemanticType):
    def __init__(self, name, binary_ops=set(), unary_ops=set(), rel_ops=set()):
        super().__init__(name)
        self.binary_ops = binary_ops
        self.unary_ops = unary_ops
        self.rel_ops = rel_ops

# Instâncias dos tipos primitivos com seus operadores válidos
IntType = UChuckType(
    "int",
    unary_ops={"-", "+", "!"},
    binary_ops={"+", "-", "*", "/", "%"},
    rel_ops={"==", "!=", "<", ">", "<=", ">=", "&&", "||"},
)

FloatType = UChuckType(
    "float",
    unary_ops={"-", "+"},
    binary_ops={"+", "-", "*", "/", "%"},
    rel_ops={"==", "!=", "<", ">", "<=", ">="},
)

StringType = UChuckType(
    "string",
    binary_ops={"+"},
    rel_ops={"==", "!="},
)

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



class Visitor(NodeVisitor):
    def __init__(self):
        self.symtab = None
        self.typemap = {
            "int": IntType,
            "float": FloatType,
            "string": StringType,
        }

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

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        ltype = node.left.attrs['uchuck_type']
        rtype = node.right.attrs['uchuck_type']
        op = node.operator
        self._assert_semantic(ltype == rtype, 3, node.coord, name=op)

        if op in ltype.binary_ops:
            node.attrs['uchuck_type'] = ltype
        elif op in ltype.rel_ops:
            node.attrs['uchuck_type'] = IntType
        else:
            self._assert_semantic(False, 4, node.coord, name=op, ltype=ltype)

    def visit_BreakStatement(self, node):
        loops = self.symtab.lookup('loops')
        self._assert_semantic(len(loops) > 0, 5, node.coord)
        node.attrs['loop'] = loops[-1]

    def visit_ChuckOp(self, node):
        self.visit(node.target)  # VarDecl
        self.visit(node.source)  # Literal ou expressão

    def visit_ContinueStatement(self, node):
        loops = self.symtab.lookup('loops')
        self._assert_semantic(len(loops) > 0, 5, node.coord)
        node.attrs['loop'] = loops[-1]

    def visit_ExpressionAsStatement(self, node):
        if type(node.expression).__name__ == "VarDecl":
            self.visit(node.expression)
            return
        if node.expression:
            self.visit(node.expression)




    def visit_ExprList(self, node):
        last_type = None
        for expr in node.exprs:
            self.visit(expr)
            last_type = expr.attrs['uchuck_type']
        node.attrs['uchuck_type'] = last_type

    def visit_IfStatement(self, node):
        self.visit(node.condition)
        test_type = node.condition.attrs['uchuck_type']
        self._assert_semantic(test_type == IntType, 6, node.condition.coord, ltype=test_type)
        self.visit(node.if_body)
        if node.else_body:
            self.visit(node.else_body)

    def visit_Literal(self, node):
        typename = node.tipo
        self._assert_semantic(typename in self.typemap, 1, node.coord, name=typename)
        node.attrs['uchuck_type'] = self.typemap[typename]

    def visit_Location(self, node):
        varname = node.name
        decl = self.symtab.lookup(varname)
        self._assert_semantic(decl is not None, 1, node.coord, name=varname)
        node.attrs['defn'] = decl
        node.attrs['uchuck_type'] = decl.attrs['uchuck_type']

    def visit_PrintStatement(self, node):
        self.visit(node.expr)
        expr_type = node.expr.attrs['uchuck_type']
        self._assert_semantic(expr_type in [IntType, FloatType, StringType], 7, node.coord)
        node.attrs['uchuck_type'] = expr_type

    def visit_Program(self, node):
        node.attrs['symtab'] = SymbolTable()
        self.symtab = node.attrs['symtab']
        self.symtab.add('loops', [])
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_Type(self, node):
        typename = node.typename
        self._assert_semantic(typename in self.typemap, 1, node.coord, name=typename)
        node.attrs['uchuck_type'] = self.typemap[typename]

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        operand_type = node.operand.attrs['uchuck_type']
        op = node.op
        self._assert_semantic(op in operand_type.unary_ops, 10, node.coord, name=op, ltype=operand_type)
        node.attrs['uchuck_type'] = operand_type

    def visit_VarDecl(self, node):
        if 'uchuck_type' in node.attrs:
            return  # Já processado por ChuckOp

        varname = node.identifier
        self._assert_semantic(self.symtab.lookup(varname) is None, 9, node.coord, name=varname)

        type_node = Type(node.typename, coord=node.coord)
        self.visit(type_node)
        dtype_type = type_node.attrs['uchuck_type']

        self.symtab.add(varname, node)
        node.attrs['uchuck_type'] = dtype_type
        node.attrs['defn'] = node




    def visit_WhileStatement(self, node):
        loops = self.symtab.lookup('loops')
        loops.append(node)
        self.visit(node.condition)
        test_type = node.condition.attrs['uchuck_type']
        self._assert_semantic(test_type == IntType, 6, node.condition.coord, ltype=test_type)
        self.visit(node.body)
        loops.pop()