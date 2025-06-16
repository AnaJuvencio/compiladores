import sys

def represent_node(obj, indent=0):
    def _repr(obj, indent, printed_set):
        if isinstance(obj, list):
            if not obj:
                return "[]"
            indent += 4
            sep = ",\n" + (" " * indent)
            return (
                "[\n"
                + sep.join(_repr(e, indent, printed_set) for e in obj)
                + "\n" + (" " * (indent - 4)) + "]"
            )
        elif isinstance(obj, Node):
            if obj in printed_set:
                return f"{obj.__class__.__name__}(...)"
            printed_set.add(obj)

            class_name = obj.__class__.__name__
            attrs = []
            indent += 4
            for name in obj.__slots__:
                if name == "attrs":  # ignora campo interno
                    continue
                value = getattr(obj, name, None)
                if value is None:
                    continue
                value_str = _repr(value, indent + len(name) + 1, printed_set)
                attrs.append(f"{name}={value_str}")
            sep = ",\n" + (" " * indent)
            result = f"{class_name}(\n" + (" " * indent) + sep.join(attrs) + "\n" + (" " * (indent - 4)) + ")"
            return result
        elif isinstance(obj, tuple) and len(obj) == 2 and all(isinstance(x, int) for x in obj):
            return f"{obj[0]}:{obj[1]}"
        elif isinstance(obj, str):
            return f"'{obj}'"
        else:
            return str(obj)

    printed_set = set()
    return _repr(obj, indent, printed_set)


class Node:
    """
    Base class for AST nodes.

    Defines `__slots__` to save memory and a `show()` method for printing.
    """
    __slots__ = ("coord", "attrs")

    def __init__(self, coord=None):
        self.coord = coord
        self.attrs = {}

    def children(self):
        return ()

    attr_names = ()

    def __repr__(self):
        result = self.__class__.__name__
        if hasattr(self, 'attr_names') and self.attr_names:
            parts = []
            for attr in self.attr_names:
                value = getattr(self, attr, None)
                parts.append(f"{value}")
            result += ": " + ", ".join(parts)
        return result


    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, showcoord=False, _my_node_name=None):
        lead = " " * offset
        label = self.__repr__()
        if showcoord and self.coord:
            label += f" @ {self.coord.line}:{self.coord.column}"
        print(lead + label, file=buf)
        for (child_name, child) in self.children():
            if child is not None:
                child.show(buf, offset + 4, attrnames, nodenames, showcoord, child_name)
            else:
                print(" " * (offset + 4) + f"{child_name}: None", file=buf)



class NodeVisitor:
    """A base NodeVisitor class for visiting uchuck_ast nodes.
    Subclass it and define your own visit_XXX methods.
    """

    _method_cache = None

    def visit(self, node):
        if self._method_cache is None:
            self._method_cache = {}

        visitor = self._method_cache.get(node.__class__.__name__, None)
        if visitor is None:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            self._method_cache[node.__class__.__name__] = visitor

        return visitor(node)

    def generic_visit(self, node):
        for _, child in node.children():
            if isinstance(child, Node):
                self.visit(child)

class Coord:
    """Coordinates of a syntactic element. Consists of:
    - Line number
    - (optional) column number
    """
    __slots__ = ("line", "column")

    def __init__(self, line, column=None):
        self.line = line
        self.column = column

    def __str__(self):
        if self.line and self.column is not None:
            return "@ %s:%s" % (self.line, self.column)
        elif self.line:
            return "@ %s" % (self.line)
        else:
            return ""


class Program(Node):
    __slots__ = ("stmts",)
    def __init__(self, stmts):
        super().__init__()
        self.stmts = stmts
    def children(self):
        return tuple((None, stmt) for stmt in (self.stmts or []))
    attr_names = ()
    def __repr__(self):
        return "Program:"

class ChuckOp(Node):
    __slots__ = ("source", "target", "coord")

    def __init__(self, source, target, coord=None):
        super().__init__()
        self.source = source
        self.target = target
        self.coord = coord

    def children(self):
        return (None, self.target), (None, self.source)



class IfStatement(Node):
    __slots__ = ("condition", "if_body", "else_body", "coord")
    
    def __init__(self, condition, if_body, else_body=None, coord=None):
        super().__init__()
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
        self.coord = coord

    def children(self):
        children = [(None, self.condition), (None, self.if_body)]
        if self.else_body is not None:
            children.append((None, self.else_body))
        return tuple(children)

    attr_names = ("coord",)

    def __repr__(self):
        return f"IfStatement:"


class WhileStatement(Node):
    __slots__ = ("condition", "body", "coord")
    def __init__(self, condition, body, coord=None):
        super().__init__()
        self.condition = condition
        self.body = body
        self.coord = coord
    def children(self):
        return (None, self.condition), (None, self.body)
    def __repr__(self):
        return f"WhileStatement:"


class PrintStatement(Node):
    __slots__ = ("expr", "coord")
    def __init__(self, expr, coord=None):
        super().__init__()
        self.expr = expr
        self.coord = coord
    def children(self):
        return (None, self.expr),



class BinaryOp(Node):
    __slots__ = ("operator", "left", "right", "coord")

    def __init__(self, operator, left, right, coord=None):
        super().__init__()
        self.operator = operator
        self.left = left
        self.right = right
        self.coord = coord

    def children(self):
        return (None, self.left), (None, self.right)

    attr_names = ("operator", "coord")
    def __repr__(self):
        return f"BinaryOp: {self.operator}"


class UnaryOp(Node):
    __slots__ = ("op", "operand", "coord")
    def __init__(self, op, operand, coord=None):
        super().__init__()
        self.op = op
        self.operand = operand
        self.coord = coord
    def children(self):
        return (None, self.operand),


class Location(Node):
    __slots__ = ("name", "coord")

    def __init__(self, name, coord=None):
        super().__init__(coord)
        self.name = name

    def children(self):
        return ()

    attr_names = ("name",)  
    def __repr__(self):
        return f"Location: {self.name}"



class Literal(Node):
    __slots__ = ("tipo", "valor", "coord")

    def __init__(self, tipo, valor, coord=None):
        super().__init__(coord)
        self.tipo = tipo
        self.valor = valor

    def children(self):
        return ()

    attr_names = ("tipo", "valor") 

    def __repr__(self):
        return f"Literal: {self.tipo}, {self.valor}"



class Type(Node):
    __slots__ = ("typename", "coord")

    def __init__(self, typename, coord=None):
        super().__init__(coord)
        self.typename = typename

    def children(self):
        return ()

    attr_names = ("typename",)  



class VarDecl(Node):
    __slots__ = ("typename", "identifier", "coord")
    def __init__(self, typename, identifier, coord=None):
        super().__init__()
        self.typename = typename
        self.identifier = identifier
        self.coord = coord
    def children(self):
        # Só inclui Type como filho!
        return (
            (None, Type(self.typename, self.coord)),
        )
    attr_names = ()
    def __repr__(self):
        return f"VarDecl: ID(name={self.identifier})"



    
class ExpressionAsStatement(Node):
    __slots__ = ("expression", "coord")

    def __init__(self, expression, coord=None):
        super().__init__()
        self.expression = expression
        self.coord = coord

    def children(self):
        return ((None, self.expression),) if self.expression is not None else ()

    #attr_names = ("coord",)


class StmtList(Node):
    __slots__ = ("stmts", "coord")
    def __init__(self, stmts, coord=None):
        super().__init__()
        self.stmts = stmts
        self.coord = coord
    def children(self):
      return tuple((None, stmt) for stmt in (self.stmts or []))
    attr_names = ("coord",)
    def __repr__(self):
        return f"StmtList:"
      
class BreakStatement (Node):
    __slots__ = ("coord",)

    def __init__(self, coord=None):
        super().__init__()
        self.coord = coord

    def children(self):
        return ()

    attr_names = ("coord",)

    def __repr__(self):
        return f"BreakStatement:"

class ContinueStatement(Node):
    __slots__ = ("coord",)

    def __init__(self, coord=None):
        super().__init__()
        self.coord = coord

    def children(self):
        return ()

    attr_names = ("coord",)

    def __repr__(self):
        return f"ContinueStatement:"
      
class ID(Node):
    __slots__ = ("name", "coord")

    def __init__(self, name, coord=None):
        super().__init__()
        self.name = name
        self.coord = coord

    def children(self):
        return ()

    def __repr__(self):
        return f"ID(name={self.name})"
      
class ExprList(Node):
    __slots__ = ("exprs", "coord")

    def __init__(self, exprs, coord=None):
        super().__init__()
        self.exprs = exprs
        self.coord = coord

    def children(self):
        return tuple((None, expr) for expr in self.exprs)

