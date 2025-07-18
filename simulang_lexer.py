import re

TOKEN_TYPES = [
    ('KEYWORD', r'\b(posit|varnothing|nabla|infty|ds2|coeternal|octyl|equiangular|intertillage|delineator|recur|print)\b'),
    ('IDENT',   r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('NUMBER',  r'\b\d+(\.\d+)?\b'),
    ('STRING',  r'"[^"]*"'),
    ('ASSIGN',  r'\:='),
    ('SYMBOL',  r'[{}();=+\-\[\]<>:∞]'),  # Note: keep ':' here but after ':=' is matched
    ('WHITESPACE', r'\s+'),
    ('COMMENT', r'//.*'),
]

def tokenize(code):
    tokens = []
    i = 0
    while i < len(code):
        match = None
        for type_, pattern in TOKEN_TYPES:
            regex = re.compile(pattern)
            match = regex.match(code, i)
            if match:
                if type_ != 'WHITESPACE' and type_ != 'COMMENT':
                    tokens.append((type_, match.group(0)))
                i = match.end()
                break
        if not match:
            raise SyntaxError(f"Unexpected character: {code[i]}")
    return tokens
