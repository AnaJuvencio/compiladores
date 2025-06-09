import sys
from sly import Lexer

class UChuckLexer(Lexer):
    """A lexer for the uChuck language."""

    def __init__(self, error_func):
        """Create a new Lexer.
        An error function. Will be called with an error
        message, line and column as arguments, in case of
        an error during lexing.
        """
        self.error_func = error_func

    # Reserved keywords
    #keywords = {
     #   'while': "WHILE",
      #  'if': "IF",
      #  'else': "ELSE",
    #}
    
   # Reserved keywords
    keywords = {
        'int': "INT",
        'float': "FLOAT",
        'if': "IF",
        'else': "ELSE",
        'while': "WHILE",
        'break': "BREAK",
        'continue': "CONTINUE",
        'true': "TRUE",
        'false': "FALSE",
    }

    # All the tokens recognized by the lexer
    tokens = tuple(keywords.values()) + ( 
        # Identifiers
        "ID",
        # Constants
        "FLOAT_VAL",     
        "INT_VAL",
        "STRING_LIT",
        # Operators
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "PERCENT",
        "LE",             
        "LT",
        "GE",            
        "GT",             
        "EQ",            
        "NEQ",            
        "AND",           
        "OR",             
        "EXCLAMATION",    
        # Assignment
        "CHUCK",
        # Delimiters
        "LPAREN",
        "RPAREN",  # ( )
        "LBRACE",
        "RBRACE",  # { }
        "L_HACK",
        "R_HACK",  # <<< >>>
        "COMMA",
        "SEMI",  # , ;
    )
    

    # Ignorar espaços e tabulações
    ignore = ' \t'

    # Ignorar comentários de linha
    @_(r'//.*')
    def ignore_comment_line(self, t):
        pass

    # Ignorar comentários de bloco
    @_(r'/\*([^*]|\*+[^*/])*\*+/')
    def ignore_comment_block(self, t):
        self.lineno += t.value.count('\n')


    # Comentário de bloco mal formatado 
    #@_(r'/\*([^*]|\*+[^*/])*$')
    @_(r'/\*([^*]|\*+[^*/])*')
    def error_unterminated_comment(self, t):
        self._error("Unterminated comment", t)

    
    # Regras de expressão regular para os tokens
    L_HACK = r'<<<'
    R_HACK = r'>>>'

    # Operadores relacionais 
    LE  = r'<='
    GE  = r'>='
    EQ  = r'=='
    NEQ = r'!='
    LT  = r'<'
    GT  = r'>'

    # Operadores lógicos
    AND = r'&&'
    OR  = r'\|\|'
    EXCLAMATION = r'!'

    # Operadores matemáticos
    PLUS    = r'\+'
    MINUS   = r'-'
    TIMES   = r'\*'
    DIVIDE  = r'/'
    PERCENT = r'%'
    CHUCK   = r'=>'

    # Delimitadores
    SEMI   = r';'
    COMMA  = r','   
    LPAREN = r'\('
    RPAREN = r'\)'
    LBRACE = r'\{'
    RBRACE = r'\}'

    # Literais
    STRING_LIT = r'"([^"\\]|\\.)*"'
    #FLOAT_VAL  = r'\d+\.\d*|\.\d+'
    FLOAT_VAL = r'\d+\.\d+(e[+-]?\d+)?|\d+e[+-]?\d+|\.\d+(e[+-]?\d+)?'
    INT_VAL    = r'\d+'

    # Identificadores
    #ID = r'[a-zA-Z_][a-zA-Z0-9_]*\$?'
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'


    # Special cases
    def ID(self, t):
      t.type = self.keywords.get(t.value, "ID")
      return t

    # Define a rule so we can track line numbers
    @_(r'\n+')
    def ignore_newline(self, t):
        self.lineno += len(t.value)


    def find_column(self, token):
        """Find the column of the token in its line."""
        last_cr = self.text.rfind('\n', 0, token.index)
        return token.index - last_cr

    #@_(r'"(\\["\\nrt]|[^"\\\n])*')
    @_(r'"([^"\\\n]|\\.)*(\\)?$')
    def error_string(self, t):
        self._error("Unterminated string literal", t)

    # Internal auxiliary methods
    def _error(self, msg, token):
        location = self._make_location(token)
        self.error_func(msg, location[0], location[1])
        self.index += 1

    def _make_location(self, token):
        return token.lineno, self.find_column(token)

    # Error handling rule
    def error(self, t):
        msg = "Illegal character %s" % repr(t.value[0])
        self._error(msg, t)

    # Scanner (used only for test)
    def scan(self, text):
        output = ""
        for tok in self.tokenize(text):
            print(tok)
            output += str(tok) + "\n"
        return output
    
def print_error(msg, x, y):
    # use stdout to match with the output in the .out test files
    print("Lexical error: %s at %d:%d" % (msg, x, y), file=sys.stdout)

def main(args):
    lex = UChuckLexer(print_error)
    with open(args[0], 'r') if len(args) > 0 else sys.stdin as f:
        lex.scan(f.read())
