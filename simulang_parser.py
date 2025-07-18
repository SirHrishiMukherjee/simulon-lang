class Node:
    def __init__(self, type_, value=None, children=None):
        self.type = type_
        self.value = value
        self.children = children or []

    def __repr__(self):
        return f"Node(type={self.type}, value={self.value}, children={self.children})"

def parse(tokens):
    i = 0

    def consume(expected_type=None, expected_value=None):
        nonlocal i
        if i >= len(tokens):
            raise SyntaxError("Unexpected end of input")
        type_, value = tokens[i]
        if expected_type and type_ != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {type_}")
        if expected_value and value != expected_value:
            raise SyntaxError(f"Expected {expected_value} but got {value}")
        i += 1
        return value

    def parse_program():
        nodes = []
        while i < len(tokens):
            if tokens[i][1] == "posit":
                nodes.append(parse_function())
            elif tokens[i][1] in ("coeternal", "octyl"):
                nodes.append(parse_statement())
            else:
                raise SyntaxError(f"Unexpected token: {tokens[i][1]}")
        return Node("Program", children=nodes)


    def parse_statement():
        if tokens[i][1] == "posit":
            return parse_function()
        elif tokens[i][1] == "print":
            return parse_print()
        elif tokens[i][1] == "recur":
            return parse_recur()
        elif tokens[i][1] in ("coeternal", "octyl"):
            return parse_assignment(tokens[i][1] == "coeternal")
        elif tokens[i][0] == "IDENT" and i + 1 < len(tokens) and tokens[i + 1][1] == "(":
            return parse_function_call()
        elif tokens[i][0] == "IDENT":
            return parse_reassignment()
        else:
            raise SyntaxError(f"Unknown statement: {tokens[i][1]}")


    def parse_function():
        consume("KEYWORD", "posit")

        # Check if this is the symbolic entry: posit varnothing nabla infty ds2()
        if tokens[i][1] == "varnothing":
            consume("KEYWORD", "varnothing")
            consume("KEYWORD", "nabla")
            consume("KEYWORD", "infty")
            consume("KEYWORD", "ds2")
            fname = "ds2"
        else:
            fname = consume("IDENT")

        consume("SYMBOL", "(")
        consume("SYMBOL", ")")
        consume("SYMBOL", ":")
        consume("SYMBOL", "{")
        body = []
        while tokens[i][1] != "}":
            body.append(parse_statement())
        consume("SYMBOL", "}")
        return Node("Function", value=fname, children=body)

    def parse_assignment(is_const):
        consume("KEYWORD")           # coeternal or octyl
        name = consume("IDENT")
        consume("ASSIGN")            # :=
        value = parse_expression()
        consume("SYMBOL", ";")
        return Node("Assignment", value=(name, value, is_const))

    def parse_reassignment():
        name = consume("IDENT")
        consume("ASSIGN")  # :=
        value = parse_expression()
        consume("SYMBOL", ";")
        return Node("Assignment", value=(name, value, False))  # not const

    def parse_print():
        consume("KEYWORD", "print")
        consume("SYMBOL", "(")
        value = parse_expression()
        consume("SYMBOL", ")")
        consume("SYMBOL", ";")
        return Node("Print", value=value)

    def parse_recur():
        consume("KEYWORD", "recur")
        consume("KEYWORD", "ds2")
        consume("SYMBOL", "(")

        # Check if parameter is present (e.g. 10∞)
        param = None
        if tokens[i][0] == "NUMBER":
            param = float(consume("NUMBER"))
            if tokens[i][1] == "∞":
                consume("SYMBOL", "∞")

        consume("SYMBOL", ")")
        consume("SYMBOL", ";")
        return Node("Recur", value=param)

    def parse_function_call():
        name = consume("IDENT")
        consume("SYMBOL", "(")
        consume("SYMBOL", ")")
        consume("SYMBOL", ";")
        return Node("Call", value=name)

    def parse_expression():
        def parse_primary():
            nonlocal i
            token_type, token_value = tokens[i]
            if token_type == "NUMBER":
                consume("NUMBER")
                return ("Number", float(token_value))
            elif token_type == "STRING":
                consume("STRING")
                return ("String", token_value.strip('"'))
            elif token_type == "IDENT":
                consume("IDENT")
                return ("Ident", token_value)
            elif token_type == "SYMBOL" and token_value == "(":
                consume("SYMBOL", "(")
                expr = parse_expression()
                consume("SYMBOL", ")")
                return expr
            else:
                raise SyntaxError(f"Invalid expression near: {token_value}")

        def parse_binary(lhs):
            nonlocal i
            while i < len(tokens) and tokens[i][1] in ("+"):
                op = consume("SYMBOL")
                rhs = parse_primary()
                lhs = ("Binary", op, lhs, rhs)
            return lhs

        lhs = parse_primary()
        return parse_binary(lhs)

    return parse_program()
