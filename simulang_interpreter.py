function_table = {}  # Global function table

class Environment:
    def __init__(self):
        self.vars = {}

    def set(self, name, value, is_const=False):
        if name in self.vars:
            current_value, is_already_const = self.vars[name]
            if is_already_const and value != current_value:
                raise RuntimeError(f"Cannot reassign constant {name}")
            if is_already_const and value == current_value:
                return  # silently allow re-declaration with same value
        self.vars[name] = (value, is_const)

    def get(self, name):
        if name not in self.vars:
            raise RuntimeError(f"Undefined variable {name}")
        return self.vars[name][0]

def execute(node, env, should_continue=lambda: True):
    if node.type == "Program":
        entry = None
        for child in node.children:
            if child.type == "Function":
                fname = child.value
                function_table[fname] = child
            elif child.type == "Assignment":
                execute(child, env, should_continue)
            elif child.type == "Call":
                execute(child, env, should_continue)

        if "ds2" in function_table:
            execute(function_table["ds2"], env, should_continue)

    elif node.type == "Function":
        loop_count = 0
        max_loops = 100
        while should_continue():
            for child in node.children:
                result = execute(child, env, should_continue)
                if isinstance(result, tuple) and result[0] == "RECUR":
                    if result[1] is not None:
                        max_loops = int(result[1])
                    break
                elif result == "RECUR":
                    break
            else:
                break
            loop_count += 1
            if loop_count >= max_loops:
                print(f"Bounded at {max_loops}∞")
                break

    elif node.type == "Assignment":
        name, value_expr, is_const = node.value
        value = evaluate_expr(value_expr, env)
        env.set(name, value, is_const)

    elif node.type == "Print":
        val = evaluate_expr(node.value, env)
        print(val)

    elif node.type == "Recur":
        if node.value is not None:
            return ("RECUR", node.value)
        return "RECUR"

    elif node.type == "Call":
        fname = node.value
        if fname not in function_table:
            raise RuntimeError(f"Undefined function: {fname}")
        execute(function_table[fname], env, should_continue)

def evaluate_expr(expr, env):
    type_ = expr[0]
    if type_ == "Number":
        return expr[1]
    elif type_ == "String":
        return expr[1]
    elif type_ == "Ident":
        return env.get(expr[1])
    elif type_ == "Binary":
        op, left, right = expr[1], expr[2], expr[3]
        lval = evaluate_expr(left, env)
        rval = evaluate_expr(right, env)
        if op == "+":
            if isinstance(lval, str) or isinstance(rval, str):
                return str(lval) + str(rval)
            return lval + rval
        else:
            raise RuntimeError(f"Unsupported operator: {op}")
