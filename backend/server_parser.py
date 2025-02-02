import ast
import io
from contextlib import redirect_stdout

class ArrayVisitor(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.initial_array = []
        self.manipulations = []
        self.target_list_name = None
        self.max_iterations = 1000

        # The environment for integer variables (like i, j, swapped, etc.)
        self.env = {}

        # The actual contents of the target array
        self.local_array = []

        # Dictionary for storing function definitions by name
        self.funcs = {}

        # If the function param is the target array, we track it here
        self.array_alias = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """
        Store function definitions so we can simulate them if called.
        """
        self.funcs[node.name] = node
        self.generic_visit(node)

    def simulate_function_call(self, func_node: ast.FunctionDef, arg_values: list):
        """
        Simulate calling a user-defined function by binding arguments and visiting the body.
        We only log variable changes if the new value actually differs from the old one.
        """
        backup_env = self.env.copy()
        backup_target = self.target_list_name
        backup_local = self.local_array[:]
        backup_alias = self.array_alias

        param_names = [arg.arg for arg in func_node.args.args]

        for p_name, val in zip(param_names, arg_values):
            # If the user passed our target array
            if val == '__ARRAY_REFERENCE__':
                self.array_alias = p_name
            else:
                old_val = self.env.get(p_name, None)
                if val != old_val:
                    self.env[p_name] = val
                    self.manipulations.append({
                        'type': 'variable',
                        'name': p_name,
                        'value': val
                    })

        for stmt in func_node.body:
            self.visit(stmt)

        # Restore
        self.env = backup_env
        self.target_list_name = backup_target
        self.local_array = backup_local
        self.array_alias = backup_alias

    def visit_Call(self, node: ast.Call):
        """
        If we see a direct function call (e.g., bubbleSort(my_arr)), we handle it.
        Otherwise we do a normal fallback.
        """
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in self.funcs:
                arg_values = []
                for arg in node.args:
                    # If the user passed the same array variable
                    if (isinstance(arg, ast.Name) and arg.id == self.target_list_name):
                        arg_values.append('__ARRAY_REFERENCE__')
                    else:
                        val = self._extract_value(arg)
                        arg_values.append(val)
                self.simulate_function_call(self.funcs[func_name], arg_values)
                return None
        # fallback if it's not a recognized function
        self.generic_visit(node)
        return None

    def visit_Assign(self, node: ast.Assign):
        """
        Called for statements like i = 5 or my_arr[i] = x
        """
        if len(node.targets) == 1:
            target = node.targets[0]

            # Case 1: variable assignment like i = 5
            if isinstance(target, ast.Name):
                var_name = target.id

                # If it's a list literal, treat it as our target array
                if isinstance(node.value, ast.List):
                    self.target_list_name = var_name
                    self.initial_array = self._extract_list_literal(node.value)
                    self.local_array = self.initial_array[:]
                else:
                    rhs_val = self._extract_value(node.value)
                    if rhs_val is not None:
                        old_val = self.env.get(var_name, None)
                        if rhs_val != old_val:
                            self.env[var_name] = rhs_val
                            self.manipulations.append({
                                'type': 'variable',
                                'name': var_name,
                                'value': rhs_val
                            })

            # Case 2: subscript assignment: my_arr[i] = x
            elif (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)):
                list_name = target.value.id
                if list_name == self.target_list_name or list_name == self.array_alias:
                    index_val = self._extract_value(target.slice)
                    replace_value = self._extract_value(node.value)
                    if (isinstance(index_val, int) and 0 <= index_val < len(self.local_array)):
                        self.local_array[index_val] = replace_value
                        self.manipulations.append({
                            'type': 'replace',
                            'index': index_val,
                            'value': replace_value
                        })

            # Case 3: tuple assignment for swaps
            elif (isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple)):
                self._check_for_swap(target, node.value)

        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        """
        We support range(...) with up to two arguments: range(end) or range(start, end).
        We only log the variable change if the loop var's new value differs from the old.
        """
        if (isinstance(node.target, ast.Name) and
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range'):
            if len(node.iter.args) == 1:
                start = 0
                end = self._extract_value(node.iter.args[0])
            elif len(node.iter.args) == 2:
                start = self._extract_value(node.iter.args[0])
                end = self._extract_value(node.iter.args[1])
            else:
                self.generic_visit(node)
                return
            if isinstance(start, int) and isinstance(end, int):
                loop_var = node.target.id
                for i in range(start, end):
                    old_val = self.env.get(loop_var, None)
                    if i != old_val:
                        self.env[loop_var] = i
                        self.manipulations.append({
                            'type': 'variable',
                            'name': loop_var,
                            'value': i
                        })
                    for stmt in node.body:
                        self.visit(stmt)
                if loop_var in self.env:
                    del self.env[loop_var]
            else:
                self.generic_visit(node)
        else:
            self.generic_visit(node)

    def visit_Expr(self, node: ast.Expr):
        """
        Called for expressions like my_arr.append(...), or direct calls.
        """
        val = node.value
        # If it's an attribute call, e.g. my_arr.append(...)
        if (isinstance(val, ast.Call) and 
            isinstance(val.func, ast.Attribute) and
            isinstance(val.func.value, ast.Name)):
            list_name = val.func.value.id
            method_name = val.func.attr
            if list_name == self.target_list_name or list_name == self.array_alias:
                if method_name == 'append' and len(val.args) == 1:
                    value = self._extract_value(val.args[0])
                    self.local_array.append(value)
                    self.manipulations.append({'type': 'append', 'value': value})
                elif method_name == 'pop':
                    if val.args:
                        idx = self._extract_value(val.args[0])
                        if (isinstance(idx, int) and 0 <= idx < len(self.local_array)):
                            self.local_array.pop(idx)
                            self.manipulations.append({'type': 'pop', 'index': idx})
                    else:
                        if self.local_array:
                            self.local_array.pop()
                        self.manipulations.append({'type': 'pop'})
                elif method_name == 'remove' and len(val.args) == 1:
                    rm_val = self._extract_value(val.args[0])
                    if rm_val in self.local_array:
                        self.local_array.remove(rm_val)
                        self.manipulations.append({'type': 'remove', 'value': rm_val})
                elif method_name == 'clear' and not val.args:
                    self.local_array.clear()
                    self.manipulations.append({'type': 'clear'})
                elif method_name == 'reverse' and not val.args:
                    self.local_array.reverse()
                    self.manipulations.append({'type': 'reverse'})

        # If it's a direct function call like bubbleSort(...)
        elif isinstance(val, ast.Call):
            self.visit_Call(val)

        self.generic_visit(node)

    def visit_While(self, node: ast.While):
        iteration_count = 0
        while self._eval_condition(node.test):
            iteration_count += 1
            if iteration_count > self.max_iterations:
                print("warning: infinite loop detected, stopping.")
                break
            for stmt in node.body:
                self.visit(stmt)
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)

    def visit_Delete(self, node: ast.Delete):
        for target in node.targets:
            if (isinstance(target, ast.Subscript) and
                isinstance(target.value, ast.Name) and
                (target.value.id == self.target_list_name or
                 target.value.id == self.array_alias)):
                idx = self._extract_value(target.slice)
                if (isinstance(idx, int) and 0 <= idx < len(self.local_array)):
                    del self.local_array[idx]
                    self.manipulations.append({'type': 'delete', 'index': idx})
        self.generic_visit(node)

    def visit_Subscript(self, node: ast.Subscript):
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign):
        """
        For i += 1 etc. Only log if new_val != old_val
        """
        if isinstance(node.target, ast.Name):
            var_name = node.target.id
            old_val = self.env.get(var_name, None)
            right_val = self._extract_value(node.value)
            if isinstance(old_val, int) and isinstance(right_val, int):
                if isinstance(node.op, ast.Add):
                    new_val = old_val + right_val
                elif isinstance(node.op, ast.Sub):
                    new_val = old_val - right_val
                elif isinstance(node.op, ast.Mult):
                    new_val = old_val * right_val
                elif isinstance(node.op, ast.Div):
                    new_val = old_val // right_val  # integer division
                elif isinstance(node.op, ast.FloorDiv):
                    new_val = old_val // right_val
                else:
                    new_val = old_val

                if new_val != old_val:
                    self.env[var_name] = new_val
                    self.manipulations.append({
                        'type': 'variable',
                        'name': var_name,
                        'value': new_val
                    })
        self.generic_visit(node)

    def _check_for_swap(self, target_tuple: ast.Tuple, value_tuple: ast.Tuple):
        """
        Detects something like:
        arr[j], arr[j+1] = arr[j+1], arr[j]
        Logs a 'swap' if it matches.
        """
        if len(target_tuple.elts) == 2 and len(value_tuple.elts) == 2:
            left_sub1, left_sub2 = target_tuple.elts
            right_sub1, right_sub2 = value_tuple.elts

            def is_subscript_of_array(node):
                return (isinstance(node, ast.Subscript) and
                        isinstance(node.value, ast.Name) and
                        (node.value.id == self.target_list_name or
                         node.value.id == self.array_alias))

            if (is_subscript_of_array(left_sub1) and
                is_subscript_of_array(left_sub2) and
                is_subscript_of_array(right_sub1) and
                is_subscript_of_array(right_sub2)):

                idx1_left = self._extract_value(left_sub1.slice)
                idx2_left = self._extract_value(left_sub2.slice)
                idx1_right = self._extract_value(right_sub1.slice)
                idx2_right = self._extract_value(right_sub2.slice)

                # We want:  idx1_left == idx2_right and idx2_left == idx1_right
                if idx1_left == idx2_right and idx2_left == idx1_right:
                    if (isinstance(idx1_left, int) and 
                        isinstance(idx2_left, int) and
                        0 <= idx1_left < len(self.local_array) and
                        0 <= idx2_left < len(self.local_array)):

                        # Perform the local array swap
                        self.local_array[idx1_left], self.local_array[idx2_left] = \
                            self.local_array[idx2_left], self.local_array[idx1_left]

                        self.manipulations.append({
                            'type': 'swap',
                            'indices': [idx1_left, idx2_left]
                        })

    def _extract_list_literal(self, list_node: ast.List):
        vals = []
        for elt in list_node.elts:
            val = self._extract_value(elt)
            vals.append(val)
        return vals

    def _extract_value(self, node: ast.AST):
        """
        Evaluate a node: 
         - numeric literals
         - environment variables
         - binOps
         - len(array)
         - subscript references
        Only log variable changes if something is truly changed; 
        but that logic is mostly in assign/augAssign, not here.
        """
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            return self.env.get(node.id, None)

        elif isinstance(node, ast.BinOp):
            left_val = self._extract_value(node.left)
            right_val = self._extract_value(node.right)
            if isinstance(left_val, int) and isinstance(right_val, int):
                if isinstance(node.op, ast.Add):
                    return left_val + right_val
                elif isinstance(node.op, ast.Sub):
                    return left_val - right_val
                elif isinstance(node.op, ast.Mult):
                    return left_val * right_val
                elif isinstance(node.op, ast.Div):
                    return left_val // right_val
                elif isinstance(node.op, ast.FloorDiv):
                    return left_val // right_val
            return None

        elif isinstance(node, ast.Call):
            # e.g., len(arr)
            if isinstance(node.func, ast.Name) and node.func.id == 'len':
                if node.args and isinstance(node.args[0], ast.Name):
                    alias = node.args[0].id
                    if alias == self.target_list_name or alias == self.array_alias:
                        return len(self.local_array)
            return None

        elif isinstance(node, ast.Subscript):
            # e.g. arr[j]
            if (isinstance(node.value, ast.Name) and
               (node.value.id == self.target_list_name or
                node.value.id == self.array_alias)):
                idx = self._extract_value(node.slice)
                if isinstance(idx, int) and 0 <= idx < len(self.local_array):
                    return self.local_array[idx]
            return None

        return None
    
    def _eval_condition(self, test_node: ast.AST):
        """
        Evaluate while conditions for simple comparisons: i < something, i > something, etc.
        """
        if (isinstance(test_node, ast.Compare) and
            len(test_node.ops) == 1 and
            len(test_node.comparators) == 1):
            left_val = self._extract_value(test_node.left)
            right_val = self._extract_value(test_node.comparators[0])
            op = test_node.ops[0]
            if isinstance(left_val, int) and isinstance(right_val, int):
                if isinstance(op, ast.Gt):
                    return left_val > right_val
                elif isinstance(op, ast.Lt):
                    return left_val < right_val
                elif isinstance(op, ast.GtE):
                    return left_val >= right_val
                elif isinstance(op, ast.LtE):
                    return left_val <= right_val
                elif isinstance(op, ast.Eq):
                    return left_val == right_val
                elif isinstance(op, ast.NotEq):
                    return left_val != right_val
        return False

def parse_python_code(python_code: str):
    """
    Parses the user's code, simulates the array usage,
    returns (initial_array, manipulations).
    """
    tree = ast.parse(python_code)
    visitor = ArrayVisitor()
    visitor.visit(tree)
    return visitor.initial_array, visitor.manipulations


if __name__ == "__main__":
    code_example = r'''
def bubbleSort(arr):
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swapped = True
        if swapped == False:
            break

my_arr = [1, 2, 3, 0, 1, 2, 6, 7, 8, 9]
bubbleSort(my_arr)
print(my_arr)
'''

    init_arr, manips = parse_python_code(code_example)
    print("Initial Array:", init_arr)
    print("Manipulations:")
    for m in manips:
        print(m)

    # Execute the code natively to see final array
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        exec(code_example, {})
    result = output_buffer.getvalue().strip()

    import ast as pyast
    try:
        final_arr = pyast.literal_eval(result)
    except Exception:
        final_arr = result

    print("\nFinal Array:", final_arr)
    print("Final Array Type:", type(final_arr))
