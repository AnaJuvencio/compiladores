import sys
from sly import Parser
from analisador_lexico import UChuckLexer

class UChuckParser(Parser):
    """A parser for the uChuck language."""

    # Get the token list from the lexer (required)
    tokens = UChuckLexer.tokens

    precedence = (
        ('left', 'COMMA'),
        ('left', 'CHUCK'),
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'EQ', 'NEQ'),
        ('left', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE', 'PERCENT'),
        ('right', 'EXCLAMATION'),
    )

    def __init__(self, error_func=lambda msg, x, y: print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stdout)):
        """Create a new Parser.
        An error function for the lexer.
        """
        self.lexer = UChuckLexer(error_func)

    def parse(self, text, lineno=1, index=0):
        return super().parse(self.lexer.tokenize(text, lineno, index))

    # Internal auxiliary methods
    def _token_coord(self, p):
        return self.lexer._make_location(p)

    # Error handling rule
    def error(self, p):
        if p:
            if hasattr(p, 'lineno'):
                print("Error at line %d near the symbol %s " % (p.lineno, p.value))
            else:
                print("Error near the symbol %s" % p.value)
        else:
            print("Error at the end of input")

    # <program> ::= <statement_list> EOF
    @_('statement_list')
    def program(self, p):
        return ('program', p.statement_list)  # NÃO desempacote com *

    @_('statement statement_list')
    def statement_list(self, p):
        return [p.statement] + p.statement_list

    @_('statement')
    def statement_list(self, p):
        return [p.statement]



    # <statement> ::= <expression_statement>
    #               | <loop_statement>
    #               | <selection_statement>
    #               | <jump_statement>
    #               | <code_segment>
    @_('expression_statement')
    def statement(self, p):
        return p.expression_statement

    @_('loop_statement')
    def statement(self, p):
        return p.loop_statement

    @_('selection_statement')
    def statement(self, p):
        return p.selection_statement

    @_('jump_statement')
    def statement(self, p):
        return p.jump_statement

    @_('code_segment')
    def statement(self, p):
        return p.code_segment


    # <jump_statement> ::= "break" ";"
    #                    | "continue" ";"
    @_('BREAK SEMI')
    def jump_statement(self, p):
        coord = self._token_coord(p)
        return (f'break @ {coord[0]}:{coord[1]}',)

    @_('CONTINUE SEMI')
    def jump_statement(self, p):
        coord = self._token_coord(p)
        return (f'continue @ {coord[0]}:{coord[1]}',)


    # <selection_statement> ::= "if" "(" <expression> ")" <statement> { "else" <statement> }?
    @_('IF LPAREN expression RPAREN statement ELSE statement')
    def selection_statement(self, p):
        coord = self._token_coord(p)
        return (f'if @ {coord[0]}:{coord[1]}', p.expression, p.statement0, p.statement1)

    @_('IF LPAREN expression RPAREN statement')
    def selection_statement(self, p):
        coord = self._token_coord(p)
        if isinstance(p.statement, tuple) and len(p.statement) == 1 and (
            p.statement[0].startswith('break @') or p.statement[0].startswith('continue @')):
            return (f'if @ {coord[0]}:{coord[1]}', p.expression, p.statement[0], None)
        return (f'if @ {coord[0]}:{coord[1]}', p.expression, p.statement, None)


    # <loop_statement> ::= "while" "(" <expression> ")" <statement>
    @_('WHILE LPAREN expression RPAREN statement')
    def loop_statement(self, p):
        coord = self._token_coord(p)
        return (f'while @ {coord[0]}:{coord[1]}', p.expression, p.statement)


    # <code_segment> ::= "{" { <statement_list> }? "}"
    @_('LBRACE statement_list RBRACE')
    def code_segment(self, p):
        coord = self._token_coord(p)
        stmts = p.statement_list
        while isinstance(stmts, tuple) and stmts[0] == 'stmt_list':
            stmts = list(stmts[1:])
        if not isinstance(stmts, list):
            stmts = [stmts]
        return (f'stmt_list @ {coord[0]}:{coord[1]}', stmts) 

    @_('LBRACE RBRACE')
    def code_segment(self, p):
        coord = self._token_coord(p)
        return (f'stmt_list @ {coord[0]}:{coord[1]}', [])



    # <expression_statement> ::= { <expression> }? ";"
    @_('expression SEMI')
    def expression_statement(self, p):
        return ('expr', p.expression)

    @_('SEMI')
    def expression_statement(self, p):
        return ('expr', None)

    # <expression> ::= <chuck_expression> { "," <chuck_expression> }*

    @_('expression COMMA chuck_expression')
    def expression(self, p):
        return ('comma', p.expression, p.chuck_expression)

    @_('chuck_expression')
    def expression(self, p):
        return p.chuck_expression


    # <chuck_expression> ::= { <chuck_expression> "=>" }? <decl_expression>
    @_('chuck_expression CHUCK decl_expression')
    def chuck_expression(self, p):
        coord = self._token_coord(p)
        return (f'chuck_op @ {coord[0]}:{coord[1]}', p.decl_expression, p.chuck_expression)



    @_('decl_expression')
    def chuck_expression(self, p):
        return p.decl_expression


    # <decl_expression> ::= <binary_expression>
    #                     | <type_decl> <identifier>
    @_('type_decl ID')
    def decl_expression(self, p):
        type_coord = self._token_coord(p)
        id_token = p._slice[1]
        id_coord = self.lexer._make_location(id_token)
        return ('var_decl',
                f'type: {p.type_decl} @ {type_coord[0]}:{type_coord[1]}',
                f'id: {p.ID} @ {id_coord[0]}:{id_coord[1]}')

    @_('binary_expression')
    def decl_expression(self, p):
        return p.binary_expression


    # <type_decl> ::= "int"
    #               | "float"
    #               | <identifier>
    @_('INT')
    def type_decl(self, p):
        return 'int'

    @_('FLOAT')
    def type_decl(self, p):
        return 'float'

    @_('ID')
    def type_decl(self, p):
        return p.ID


    # <binary_expression> ::= <unary_expression>
    #                       | <binary_expression> "+"  <binary_expression>
    #                       | <binary_expression> "-"  <binary_expression>
    #                       | <binary_expression> "*"  <binary_expression>
    #                       | <binary_expression> "/"  <binary_expression>
    #                       | <binary_expression> "%"  <binary_expression>
    #                       | <binary_expression> "<=" <binary_expression>
    #                       | <binary_expression> "<"  <binary_expression>
    #                       | <binary_expression> ">=" <binary_expression>
    #                       | <binary_expression> ">"  <binary_expression>
    #                       | <binary_expression> "==" <binary_expression>
    #                       | <binary_expression> "!=" <binary_expression>
    #                       | <binary_expression> "&&" <binary_expression>
    #                       | <binary_expression> "||" <binary_expression>
    @_('binary_expression PLUS binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: + @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression MINUS binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: - @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression TIMES binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: * @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression DIVIDE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: / @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression PERCENT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: % @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression LE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: <= @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression LT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: < @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression GE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: >= @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression GT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: > @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression EQ binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: == @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression NEQ binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: != @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression AND binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: && @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('binary_expression OR binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return (f'binary_op: || @ {coord[0]}:{coord[1]}', p.binary_expression0, p.binary_expression1)

    @_('unary_expression')
    def binary_expression(self, p):
        return p.unary_expression


    # <unary_expression> ::= <primary_expression>
    #                      | <unary_operator> <unary_expression>
    @_('unary_operator unary_expression')
    def unary_expression(self, p):
        coord = self._token_coord(p)
        return (f'unary_op: {p.unary_operator} @ {coord[0]}:{coord[1]}', p.unary_expression)

    @_('MINUS unary_expression %prec EXCLAMATION')
    def unary_expression(self, p):
        coord = self._token_coord(p)
        return (f'unary_op: - @ {coord[0]}:{coord[1]}', p.unary_expression)

    @_('primary_expression')
    def unary_expression(self, p):
        return p.primary_expression


    # <unary_operator> ::= "+"
    #                    | "-"
    #                    | "!"
    @_('PLUS')
    def unary_operator(self, p):
        return '+'

    @_('MINUS')
    def unary_operator(self, p):
        return '-'

    @_('EXCLAMATION')
    def unary_operator(self, p):
        return '!'


    # <primary_expression> ::= <literal>
    #                        | <location>
    #                        | "<<<" <expression> ">>>"
    #                        | "(" <expression> ")"
    @_('literal')
    def primary_expression(self, p):
        return p.literal

    @_('location')
    def primary_expression(self, p):
        return p.location

    @_('L_HACK expression R_HACK')
    def primary_expression(self, p):
        coord = self._token_coord(p)
        return (f'print @ {coord[0]}:{coord[1]}', p.expression)

    @_('LPAREN expression RPAREN')
    def primary_expression(self, p):
        return p.expression


    # <literal> ::= <integer_value>
    #             | <float_value>
    #             | <string_literal>
    #             | "true"
    #             | "false"
    @_('INT_VAL')
    def literal(self, p):
        coord = self._token_coord(p)
        return f'literal: int, {p.INT_VAL} @ {coord[0]}:{coord[1]}'

    @_('FLOAT_VAL')
    def literal(self, p):
        coord = self._token_coord(p)
        return f'literal: float, {p.FLOAT_VAL} @ {coord[0]}:{coord[1]}'

    @_('STRING_LIT')
    def literal(self, p):
        coord = self._token_coord(p)
        return f'literal: string, {p.STRING_LIT} @ {coord[0]}:{coord[1]}'

    @_('TRUE')
    def literal(self, p):
        coord = self._token_coord(p)
        return f'literal: int, 1 @ {coord[0]}:{coord[1]}'

    @_('FALSE')
    def literal(self, p):
        coord = self._token_coord(p)
        return f'literal: int, 0 @ {coord[0]}:{coord[1]}'


    # <location> ::= <identifier>
    @_('ID')
    def location(self, p):
        coord = self._token_coord(p)
        return f'location: {p.ID} @ {coord[0]}:{coord[1]}'

def build_tree(root):
    return '\n'.join(_build_tree(root))

def _build_tree(node):
    if isinstance(node, list):
        if not node: return
        node = tuple(node)

    if not isinstance(node, tuple):
        yield " "+str(node)
        return

    values = [_build_tree(n) for n in node]
    if len(values) == 1:
        yield from build_lines('──', '  ', values[0])
        return

    start, *mid, end = values
    yield from build_lines('┬─', '│ ', start)
    for value in mid:
        yield from build_lines('├─', '│ ', value)
    yield from build_lines('└─', '  ', end)

def build_lines(first, other, values):
    try:
        yield first + next(values)
        for value in values:
            yield other + value
    except StopIteration:
        return

def print_error(msg, x, y):
    # use stdout to match with the output in the .out test files
    print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stdout)

def main(args):
    parser = UChuckParser(print_error)
    with open(args[0], 'r') if len(args) > 0 else sys.stdin as f:
        st = parser.parse(f.read())
        if st is not None:
            print(build_tree(st))


