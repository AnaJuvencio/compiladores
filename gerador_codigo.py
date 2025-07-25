import sys
from ast_alguma import *
from analisador_semantico import *

class Function:
    def __init__(self, name, args, rettype):
        self.name = name
        self.args = args
        self.rettype = rettype
        self.locals = []
        self.statements = []

    def __str__(self):
        args = ', '.join(self.args)
        decl = f"{self.rettype} {self.name}({args}) {{\n"
        for l in self.locals:
            decl += f"    {l}\n"
        for s in self.statements:
            decl += f"    {s}\n"
        decl += "}"
        return decl



class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.globals = []
        self.function = None
        CodeGenerator._temporary_counter = 0
        CodeGenerator._label_counter = 0

    def new_temporary(self, c_type):
        CodeGenerator._temporary_counter += 1
        name = f'_t{CodeGenerator._temporary_counter}'
        self.function.locals.append(f'{c_type} {name};')
        return name

    def new_label(self):
        CodeGenerator._label_counter += 1
        return f'L{CodeGenerator._label_counter}'

    def declare_function(self, funcname, argdefns, rettype):
        self.function = Function(funcname, argdefns, rettype)
        self.globals.append(self.function)

    def append(self, stmt):
        self.function.statements.append(stmt)

    def typeof(self, node):
        uchuck_type = node.attrs['uchuck_type']
        if uchuck_type == IntType:
            return "int"
        elif uchuck_type == FloatType:
            return "double"
        elif uchuck_type == StringType:
            return "char*"
        else:
            raise RuntimeError(f'Unsupported type {uchuck_type}')

    def show(self, buf=sys.stdout):
        main = self.globals[0]
        _str = "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
        _str += str(main) + "\n"
        buf.write(_str)

    def generate(self, ast):
        self.visit(ast)

    def visit_Program(self, node):
        self.declare_function('main', [], 'int')
        for stmt in node.stmts:
            self.visit(stmt)
        self.append('return 0;')

    def visit_StmtList(self, node):
        for stmt in node.stmts:
            self.visit(stmt)

    def visit_VarDecl(self, node):
        self.visit(node.dtype)
        ctype = self.typeof(node)
        varname = node.name.name if hasattr(node.name, 'name') else node.name
        if ctype == 'char*':
            self.function.locals.append(f"{ctype} {varname} = NULL;")
        else:
            self.function.locals.append(f"{ctype} {varname};")
        node.attrs['gen_location'] = varname

    def visit_Type(self, node):
        pass

    def visit_Literal(self, node):
        value = getattr(node, 'valor', None) if hasattr(node, 'valor') else getattr(node, 'value', None)
        uchuck_type = node.attrs['uchuck_type']

        if uchuck_type == IntType or uchuck_type == FloatType:
            temp = str(value)
        elif uchuck_type == StringType:
            temp = self.new_temporary('char*')

            # Remove aspas externas se houver (ex: '"x"' vira 'x')
            if isinstance(value, str) and value.startswith('"') and value.endswith('"'):
                value_inner = value[1:-1]
            else:
                value_inner = value

            # CASO ESPECIAL: apenas uma quebra de linha
            if value_inner == '\\n' or value_inner == '\n':
                c_value = '\\n' if value_inner == '\\n' else '\n'
            else:
                # Faz escape duplo: unicode_escape cobre multiline e \n, replace cobre aspas duplas
                c_value = (
                    value_inner.encode('unicode_escape').decode('ascii')
                    .replace('"', '\\"')
                )
            self.append(f'{temp} = strdup("{c_value}");')
        else:
            raise RuntimeError("Unsupported literal type")
        node.attrs['gen_location'] = temp



    def visit_BinaryOp(self, node):
        self.visit(node.left)
        lvalue = node.left.attrs['gen_location']
        self.visit(node.right)
        rvalue = node.right.attrs['gen_location']
        result = self.new_temporary(self.typeof(node))
        op = getattr(node, 'op', getattr(node, 'operator', None))
        if op == '+' and self.typeof(node) == 'char*':
            temp_len = self.new_temporary('int')
            self.append(f'{temp_len} = strlen({lvalue}) + strlen({rvalue});')
            self.append(f'{result} = malloc({temp_len} + 1);')
            self.append(f'strcpy({result}, {lvalue});')
            self.append(f'strcat({result}, {rvalue});')
        else:
            self.append(f"{result} = {lvalue} {op} {rvalue};")
        node.attrs['gen_location'] = result





    def visit_Location(self, node):
        node.attrs['gen_location'] = node.name

    def visit_BinaryOp(self, node):
        self.visit(node.left)
        lvalue = node.left.attrs['gen_location']
        self.visit(node.right)
        rvalue = node.right.attrs['gen_location']
        result = self.new_temporary(self.typeof(node))
        op = getattr(node, 'op', getattr(node, 'operator', None))
        
        # Correto para concatenação de strings (char*) usando malloc, strcpy, strcat
        if op == '+' and self.typeof(node) == 'char*':
            temp_len = self.new_temporary('int')
            self.append(f'{temp_len} = strlen({lvalue}) + strlen({rvalue});')
            self.append(f'{result} = malloc({temp_len} + 1);')
            self.append(f'strcpy({result}, {lvalue});')
            self.append(f'strcat({result}, {rvalue});')
        else:
            self.append(f"{result} = {lvalue} {op} {rvalue};")
        node.attrs['gen_location'] = result



    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        val = node.operand.attrs['gen_location']
        result = self.new_temporary(self.typeof(node))
        self.append(f"{result} = {node.op}{val};")
        node.attrs['gen_location'] = result

    def visit_ChuckOp(self, node):
        self.visit(node.location)
        varname = node.location.attrs['gen_location']
        self.visit(node.expression)
        value = node.expression.attrs['gen_location']
        if self.typeof(node.location) == 'char*':
            self.append(f'{varname} = strcpy(realloc({varname}, strlen({value})+1), {value});')
        else:
            self.append(f'{varname} = {value};')
        node.attrs['gen_location'] = varname

    def visit_ExpressionAsStatement(self, node):
        if node.expression:
            self.visit(node.expression)

    def visit_IfStatement(self, node):
        self.visit(node.test)
        cond = node.test.attrs['gen_location']
        label_else = self.new_label()
        label_end = self.new_label()
        self.append(f'if (!{cond}) goto {label_else};')
        self.visit(node.consequence)
        self.append(f'goto {label_end};')
        self.append(f'{label_else}: ;')
        if hasattr(node, 'alternative') and node.alternative:
            self.visit(node.alternative)
        self.append(f'{label_end}: ;')

    def visit_WhileStatement(self, node):
        start_label = self.new_label()
        end_label = self.new_label()
        self.append(f"{start_label}:")
        self.visit(node.test)
        cond = node.test.attrs['gen_location']
        self.append(f"if (!{cond}) goto {end_label};")
        # Salva labels de break/continue atuais (caso de laço aninhado)
        old_break = getattr(self, '_break_label', None)
        old_continue = getattr(self, '_continue_label', None)
        self._break_label = end_label
        self._continue_label = start_label
        self.visit(node.body)
        self._break_label = old_break
        self._continue_label = old_continue
        self.append(f"goto {start_label};")
        self.append(f"{end_label}:")

    def visit_BreakStatement(self, node):
        # Gera goto para o label de saída do laço mais próximo
        if hasattr(self, '_break_label') and self._break_label:
            self.append(f"goto {self._break_label};")

    def visit_ContinueStatement(self, node):
        # Gera goto para o label de início do laço mais próximo
        if hasattr(self, '_continue_label') and self._continue_label:
            self.append(f"goto {self._continue_label};")

    def visit_ExprList(self, node):
        last = None
        for expr in node.exprs:
            self.visit(expr)
            last = expr.attrs.get('gen_location')
        node.attrs['gen_location'] = last

    def visit_PrintStatement(self, node):
        exprs = node.expression.exprs if hasattr(node.expression, 'exprs') else [node.expression]
        for expr in exprs:
            # Checa se é string "\n" para imprimir direto um ENTER
            if hasattr(expr, 'attrs') and expr.attrs.get('uchuck_type', None) == StringType:
                val = getattr(expr, 'valor', None) if hasattr(expr, 'valor') else getattr(expr, 'value', None)
                if val == '"\\n"' or val == '"\n"' or val == '\n' or val == '\\n':
                    self.append('printf("\\n");')
                    continue
            self.visit(expr)
            val = expr.attrs['gen_location']
            ctype = self.typeof(expr)
            if ctype == "int":
                self.append(f'printf("%d\\n", {val});')
            elif ctype == "double":
                self.append(f'printf("%f\\n", {val});')
            elif ctype == "char*":
                self.append(f'printf("%s\\n", {val});')


