class SymbolicInfinity:
    def __init__(self, coefficient=1, operation=None, right=None, base=None):
        self.coefficient = coefficient
        self.operation = operation
        self.right = right
        self.base = base  # for nesting like (∞/3) + 5

    def __str__(self):
        base_str = str(self.base) if self.base else f"{'' if self.coefficient == 1 else self.coefficient}∞"

        if self.operation == '*':
            return f"{self.coefficient}∞"
        elif self.operation is None:
            return base_str
        else:
            return f"{base_str}{self.operation}{self.right}"

    def __repr__(self):
        return self.__str__()

    def with_offset(self, offset):
        if offset == 0:
            return self
        return SymbolicInfinity(operation='+', right=offset, base=self)

    def __int__(self):
        if self.base:
            base_val = int(self.base)
        else:
            base_val = int(1e9)

        if self.operation == '+':
            return base_val + int(self.right)
        elif self.operation == '-':
            return base_val - int(self.right)
        elif self.operation == '/':
            return int(1e9 // self.right)
        elif self.operation is None:
            return base_val
        else:
            raise RuntimeError(f"Unsupported operation: {self.operation}")

    def __float__(self):
        return float(self.__int__())

    def __sub__(self, other):
        if isinstance(other, SymbolicInfinity):
            return f"({self})-({other})"
        elif isinstance(other, (int, float)):
            return f"({self})-{other}"
        else:
            raise TypeError(f"Unsupported type for subtraction from SymbolicInfinity: {type(other)}")

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return SymbolicInfinity(self.coefficient, "+", other)
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)
