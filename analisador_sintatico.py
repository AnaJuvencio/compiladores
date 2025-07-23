import sys
from sly import Parser
from analisador_lexico import UChuckLexer
from analisador_semantico import Visitor 
from ast_alguma import Program, BinaryOp, UnaryOp, Literal, Location, PrintStatement, IfStatement, WhileStatement, ChuckOp, VarDecl, ExpressionAsStatement, StmtList, BreakStatement, ContinueStatement, ExprList, Coord, Type, ID

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
        #('right', 'UMINUS'),
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
        line, column = self.lexer._make_location(p)
        return Coord(line, column)

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
        return Program(p.statement_list)
  
    
    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

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
        return BreakStatement(coord=coord)

    @_('CONTINUE SEMI')
    def jump_statement(self, p):
        coord = self._token_coord(p)
        return ContinueStatement(coord=coord)
 


    # <selection_statement> ::= "if" "(" <expression> ")" <statement> { "else" <statement> }?
    @_('IF LPAREN expression RPAREN statement ELSE statement')
    def selection_statement(self, p):
        coord = self._token_coord(p)
        return IfStatement(p.expression, p.statement0, p.statement1, coord=coord)

    @_('IF LPAREN expression RPAREN statement')
    def selection_statement(self, p):
        coord = self._token_coord(p)
        return IfStatement(p.expression, p.statement, None, coord=coord)



    # <loop_statement> ::= "while" "(" <expression> ")" <statement>
    @_('WHILE LPAREN expression RPAREN statement')
    def loop_statement(self, p):
        coord = self._token_coord(p)
        return WhileStatement(p.expression, p.statement, coord=coord)



    # <code_segment> ::= "{" { <statement_list> }? "}"
    @_('LBRACE statement_list RBRACE')
    def code_segment(self, p):
        coord = self._token_coord(p)
        return StmtList(p.statement_list, coord=coord)

    @_('LBRACE RBRACE')
    def code_segment(self, p):
        coord = self._token_coord(p)
        return StmtList([], coord=coord)




    # <expression_statement> ::= { <expression> }? ";"
    @_('expression SEMI')
    def expression_statement(self, p):
        coord = self._token_coord(p)
        return ExpressionAsStatement(p.expression, coord=coord)

    @_('SEMI')
    def expression_statement(self, p):
        coord = self._token_coord(p)
        return ExpressionAsStatement(None, coord=coord)


    # <expression> ::= <chuck_expression> { "," <chuck_expression> }*

    @_('expression COMMA expression')
    def expression(self, p):
        if isinstance(p.expression0, ExprList):
            expressions = p.expression0.exprs + [p.expression1]
            coord = p.expression0.coord  
        else:
            expressions = [p.expression0, p.expression1]
            coord = p.expression0.coord  

        return ExprList(expressions, coord=coord)



    @_('chuck_expression')
    def expression(self, p):
        return p.chuck_expression


    # <chuck_expression> ::= { <chuck_expression> "=>" }? <decl_expression>
    @_('chuck_expression CHUCK decl_expression')
    def chuck_expression(self, p):
        coord = self._token_coord(p)
        return ChuckOp(p.chuck_expression, p.decl_expression, coord=coord)





    @_('decl_expression')
    def chuck_expression(self, p):
        return p.decl_expression


    # <decl_expression> ::= <binary_expression>
    #                     | <type_decl> <identifier>
    @_('type_decl ID')
    def decl_expression(self, p):
        coord = self._token_coord(p)
        # Se p.type_decl já for Type, só usa ele!
        if isinstance(p.type_decl, Type):
            dtype = p.type_decl
        else:
            dtype = Type(p.type_decl, coord=coord)
        return VarDecl(dtype, ID(p.ID, coord=coord), coord=coord)







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
        if isinstance(p.binary_expression0, UnaryOp):
            coord.column += 1
        return BinaryOp('+', p.binary_expression0, p.binary_expression1, coord=coord)


    @_('binary_expression MINUS binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('-', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression TIMES binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('*', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression DIVIDE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('/', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression PERCENT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('%', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression LE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('<=', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression LT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('<', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression GE binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('>=', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression GT binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('>', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression EQ binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        return BinaryOp('==', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression NEQ binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p) 
        return BinaryOp('!=', p.binary_expression0, p.binary_expression1, coord)

    @_('binary_expression AND binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)

        
        left_coord = getattr(p.binary_expression0, "coord", None)

        
        if left_coord and coord.column != left_coord.column:
            coord.column += 1  

        return BinaryOp('&&', p.binary_expression0, p.binary_expression1, coord)


    @_('binary_expression OR binary_expression')
    def binary_expression(self, p):
        coord = self._token_coord(p)
        coord.column += 1  
        return BinaryOp('||', p.binary_expression0, p.binary_expression1, coord)


    @_('unary_expression')
    def binary_expression(self, p):
        return p.unary_expression


    # <unary_expression> ::= <primary_expression>
    #                      | <unary_operator> <unary_expression>
    @_('MINUS expression')
    def expression(self, p):
        coord = self._token_coord(p.MINUS)  
        return UnaryOp('-', p.expression, coord=coord)


    @_('unary_operator unary_expression')
    def unary_expression(self, p):
        return UnaryOp(p.unary_operator, p.unary_expression, coord=p.unary_expression.coord)


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
        return PrintStatement(p.expression, coord=coord)



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
        return Literal('int', p.INT_VAL, coord=coord)

    @_('FLOAT_VAL')
    def literal(self, p):
        coord = self._token_coord(p)
        return Literal('float', p.FLOAT_VAL, coord=coord)

    @_('STRING_LIT')
    def literal(self, p):
        coord = self._token_coord(p)
        return Literal('string', p.STRING_LIT, coord=coord)

    @_('TRUE')
    def literal(self, p):
        coord = self._token_coord(p)
        return Literal('int', 1, coord=coord)

    @_('FALSE')
    def literal(self, p):
        coord = self._token_coord(p)
        return Literal('int', 0, coord=coord)

    

    # <location> ::= <identifier>
    @_('ID')
    def location(self, p):
        coord = self._token_coord(p)
        return Location(p.ID, coord=coord)

    

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

'''def main(args):
    parser = UChuckParser(print_error)
    with open(args[0], 'r') if len(args) > 0 else sys.stdin as f:
        ast = parser.parse(f.read())
        if ast is not None:
            ast.show(showcoord=True)'''
def main(args):
    parser = UChuckParser(print_error)
    with open(args[0], 'r') if len(args) > 0 else sys.stdin as f:
        ast = parser.parse(f.read())
        if ast is not None:
            sema = Visitor()
            sema.visit(ast)  # ⬅️ aqui executa a análise semântica
            ast.show(showcoord=True)
