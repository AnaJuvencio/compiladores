import sys

def represent_node(obj, indent):
    if isinstance(obj, Node):
        return obj.__repr__()
    elif isinstance(obj, list):
        return "[" + ", ".join(represent_node(e, indent) for e in obj) + "]"
    elif isinstance(obj, str):
        return obj
    else:
        return str(obj)

class Node:
    __slots__ = ("attrs",)

    def __init__(self):
        self.attrs = {}

    def children(self):
        return ()

    attr_names = ()

    def __repr__(self):
        return represent_node(self, 0)

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, _my_node_name=None):
        lead = " " * offset
        print(lead + self.__repr__(), file=buf)
        for (child_name, child) in self.children():
            if child is not None:
                child.show(buf, offset + 4, attrnames, nodenames, child_name)

class Program(Node):
    __slots__ = ("statements",)
    def __init__(self, statements):
        super().__init__()
        self.statements = statements
    def children(self):
        return [(f"statements[{i}]", stmt) for i, stmt in enumerate(self.statements or [])]
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
    
    attr_names = ("coord",)

    def __repr__(self):
      return f"ChuckOp: @ {self.coord[0]}:{self.coord[1]}"



class IfStatement(Node):
    __slots__ = ("condition", "if_body", "else_body", "coord")
    
    def __init__(self, condition, if_body, else_body=None, coord=None):
        super().__init__()
        self.condition = condition
        self.if_body = if_body
        self.else_body = else_body
        self.coord = coord

    def children(self):
        children = [("condition", self.condition), ("if_body", self.if_body)]
        if self.else_body is not None:
            children.append(("else_body", self.else_body))
        return tuple(children)

    attr_names = ("coord",)

    def __repr__(self):
        return f"IfStatement: @ {self.coord[0]}:{self.coord[1]}"


class WhileStatement(Node):
  __slots__ = ("condition", "body", "coord")
  def __init__(self, condition, body, coord=None):
    super().__init__()
    self.condition = condition
    self.body = body
    self.coord = coord
  def children(self):
    return (("condition", self.condition), ("body", self.body))
  attr_names = ("coord",)
  def __repr__(self):
    return f"WhileStatement: @ {self.coord[0]}:{self.coord[1]}"


class PrintStatement(Node):
    __slots__ = ("exprs", "coord")
    def __init__(self, exprs, coord=None):
        self.exprs = exprs if isinstance(exprs, list) else [exprs]
        self.coord = coord

    def children(self):
        return [(f"expr[{i}]", e) for i, e in enumerate(self.exprs)]

    attr_names = ("coord",)

    def __repr__(self):
        return f"PrintStatement: @ {self.coord[0]}:{self.coord[1]}"



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
      return f"BinaryOp: {self.operator} @ {self.coord[0]}:{self.coord[1]}"

class UnaryOp(Node):
  __slots__ = ("operator", "operand", "coord")
  def __init__(self, operator, operand, coord=None):
    super().__init__()
    self.operator = operator
    self.operand = operand
    self.coord = coord
  def children(self):
    return (("operand", self.operand),)
  attr_names = ("operator", "coord")


class Location(Node):
    __slots__ = ("name", "coord")
    def __init__(self, name, coord=None):
        super().__init__()
        self.name = name
        self.coord = coord
    attr_names = ("name", "coord")
    def __repr__(self):
        if self.coord is not None:
            return f"Location: {self.name} @ {self.coord[0]}:{self.coord[1]}"
        else:
            return f"Location: {self.name}"

class Literal(Node):
    __slots__ = ("tipo", "valor", "coord")

    def __init__(self, tipo, valor, coord=None):
        super().__init__()
        self.tipo = tipo
        self.valor = valor
        self.coord = coord

    def children(self):
        return ()

    def show(self, buf=sys.stdout, offset=0, attrnames=False, nodenames=False, _my_node_name=None):
        label = f"{_my_node_name or 'Literal'}: {self.tipo}, {self.valor}"
        if self.coord:
            label += f" @ {self.coord[0]}:{self.coord[1]}"
        print(" " * offset + label, file=buf)

    def __repr__(self):
        return f"Literal: {self.tipo}, {self.valor} @ {self.coord[0]}:{self.coord[1]}"

class Type(Node):
    __slots__ = ("typename", "coord")
    def __init__(self, typename, coord=None):
        super().__init__()
        self.typename = typename
        self.coord = coord
    def children(self):
        return ()
    attr_names = ("typename", "coord")
    def __repr__(self):
        return f"Type: {self.typename} @ {self.coord[0]}:{self.coord[1]}"

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
        return (("expression", self.expression),) if self.expression is not None else ()

    #attr_names = ("coord",)
    def __repr__(self):
        return "ExpressionAsStatement:"


class StmtList(Node):
    __slots__ = ("statements", "coord")
    def __init__(self, statements, coord=None):
        super().__init__()
        self.statements = statements
        self.coord = coord
    def children(self):
        return [(f"statements[{i}]", stmt) for i, stmt in enumerate(self.statements or [])]
    attr_names = ("coord",)
    def __repr__(self):
        return f"StmtList: @ {self.coord[0]}:{self.coord[1]}"
      
class Break(Node):
    __slots__ = ("coord",)

    def __init__(self, coord=None):
        super().__init__()
        self.coord = coord

    def children(self):
        return ()

    attr_names = ("coord",)

    def __repr__(self):
        return f"break @ {self.coord[0]}:{self.coord[1]}"

class Continue(Node):
    __slots__ = ("coord",)

    def __init__(self, coord=None):
        super().__init__()
        self.coord = coord

    def children(self):
        return ()

    attr_names = ("coord",)

    def __repr__(self):
        return f"continue @ {self.coord[0]}:{self.coord[1]}"