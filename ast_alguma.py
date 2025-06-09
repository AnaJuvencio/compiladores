import sys

def represent_node(obj, indent): 
  def _repr(obj, indent, printed_set):
    if isinstance(obj, list):
      indent += 1
      sep = ",\n" + (" " * indent)
      final_sep = ",\n" + (" " * (indent - 1))
      return (
        "["
        + (sep.join((_repr(e, indent, printed_set) for e in obj)))
        + final_sep
        + "]"
      )
    elif isinstance(obj, Node):
      if obj in printed_set:
        return ""
      printed_set.add(obj)
      result = obj.__class__.__name__ + "("
      indent += len(obj.__class__.__name__) + 1
      attrs = []
      for name in obj.__slots__:
        if name == "attrs":
          continue
        value = getattr(obj, name)
        value_str = _repr(value, indent + len(name) + 1, printed_set) if value is not None else "None"
        attrs.append(name + "=" + value_str)
      sep = ",\n" + (" " * indent)
      final_sep = ",\n" + (" " * (indent - 1))
      result += sep.join(attrs) + final_sep + ")"
      return result
    elif isinstance(obj, str):
      return obj
    else:
      return str(obj)

  return _repr(obj, indent, set())


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
    if nodenames and _my_node_name is not None:
      buf.write(lead + self.__class__.__name__ + " <" + _my_node_name + ">: ")
      inner_offset = len(self.__class__.__name__ + " <" + _my_node_name + ">: ")
    else:
      buf.write(lead + self.__class__.__name__ + ":")
      inner_offset = len(self.__class__.__name__ + ":")

    if self.attr_names:
      if attrnames:
        nvlist = [
          (n, represent_node(getattr(self, n), offset + inner_offset + 1 + len(n) + 1))
          for n in self.attr_names if getattr(self, n) is not None
        ]
        attrstr = ", ".join("%s=%s" % nv for nv in nvlist)
      else:
        vlist = [getattr(self, n) for n in self.attr_names]
        attrstr = ", ".join(
          represent_node(v, offset + inner_offset + 1) for v in vlist if v is not None
        )
      buf.write(" " + attrstr)

    buf.write("\n")

    for (child_name, child) in self.children():
      child.show(buf, offset + 4, attrnames, nodenames, child_name)



class ChuckOp(Node):
    __slots__ = ("source", "target", "coord")

    def __init__(self, source, target, coord=None):
        super().__init__()
        self.source = source  # Literal (valor)
        self.target = target  # VarDecl
        self.coord = coord

    def children(self):
        return (None, self.source), (None, self.target)

    attr_names = ("coord",)

    def __repr__(self):
        return f"ChuckOp: @ {self.coord[0]}:{self.coord[1]}"




class IfStatement(Node):
  __slots__ = ("condition", "then_branch", "else_branch", "coord")
  def __init__(self, condition, then_branch, else_branch=None, coord=None):
    super().__init__()
    self.condition = condition
    self.then_branch = then_branch
    self.else_branch = else_branch
    self.coord = coord
  def children(self):
    lst = [("condition", self.condition), ("then_branch", self.then_branch)]
    if self.else_branch is not None:
      lst.append(("else_branch", self.else_branch))
    return tuple(lst)
  attr_names = ("coord",)

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

class Print(Node):
    __slots__ = ("expression", "coord")

    def __init__(self, expression, coord=None):
        super().__init__()
        self.expression = expression
        self.coord = coord

    def children(self):
        return ((None, self.expression),)

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


class Program(Node):
  __slots__ = ("statements",)
  def __init__(self, statements):
    super().__init__()
    self.statements = statements
  def children(self):
    return [(f"statements[{i}]", stmt) for i, stmt in enumerate(self.statements or [])]

class VarDecl(Node):
    __slots__ = ("type", "identifier", "coord")
    def __init__(self, type, identifier, coord=None):
        super().__init__()
        self.type = type
        self.identifier = identifier
        self.coord = coord
    def children(self):
        return [
            ("Location", Location(self.identifier, self.coord)),
            ("type", Literal("Type", self.type, self.coord))
        ]
    attr_names = ()

    
class ExpressionAsStatement(Node):
    __slots__ = ("expression",)

    def __init__(self, expression):
        super().__init__()
        self.expression = expression

    def children(self):
        return (("expression", self.expression),)



class StmtList(Node):
    __slots__ = ("statements", "coord")
    def __init__(self, statements, coord=None):
        super().__init__()
        self.statements = statements
        self.coord = coord
    def children(self):
        return [(f"statements[{i}]", stmt) for i, stmt in enumerate(self.statements or [])]
    attr_names = ("coord",)


