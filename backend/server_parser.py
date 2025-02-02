# server_parser.py

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
        self.env = {}

    def visit_Assign(self, node):
        """
        Handles assignments like:
          i = 5
          my_list = [1, 2, 3]
          my_list[i] = x
        """
        if len(node.targets) == 1:
            target = node.targets[0]

            # Case 1: A variable assignment like i = 5
            if isinstance(target, ast.Name):
                var_name = target.id
                # If the right side is a list, treat it as the initial array
                if isinstance(node.value, ast.List):
                    self.target_list_name = var_name
                    self.initial_array = []
                    for elt in node.value.elts:
                        if isinstance(elt, ast.Constant):
                            self.initial_array.append(elt.value)
                        else:
                            self.initial_array.append(self._extract_value(elt))
                else:
                    # Evaluate the right-hand side
                    rhs_val = self._extract_value(node.value)
                    if rhs_val is not None:
                        # Update our environment
                        self.env[var_name] = rhs_val
                        # Record this as a variable manipulation
                        self.manipulations.append({
                            'type': 'variable',
                            'name': var_name,
                            'value': rhs_val
                        })
            # Case 2: Subscript assignment like: my_list[i] = x
            elif (isinstance(target, ast.Subscript)
                  and isinstance(target.value, ast.Name)):
                list_name = target.value.id
                if list_name == self.target_list_name:
                    index_val = self._extract_index(target.slice)
                    replace_value = self._extract_value(node.value)
                    if index_val is not None:
                        self.manipulations.append({
                            'type': 'replace',
                            'index': index_val,
                            'value': replace_value
                        })
            # Case 3: Tuple assignment for swapping
            elif (isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple)):
                self._check_for_swap(target, node.value)

        self.generic_visit(node)

    def visit_For(self, node):
        if (isinstance(node.target, ast.Name) and
            isinstance(node.iter, ast.Call) and
            isinstance(node.iter.func, ast.Name) and
            node.iter.func.id == 'range' and
            len(node.iter.args) == 1):
            
            # Evaluate the range expression
            iterations = self._extract_value(node.iter.args[0])
            if isinstance(iterations, int):
                loop_var = node.target.id
                for i in range(iterations):
                    self.env[loop_var] = i
                    # Record the variable each iteration
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
                # If we can't evaluate the range expression to an int, fallback
                self.generic_visit(node)
        else:
            # If not a simple recognized for loop, fallback
            self.generic_visit(node)
    
    def visit_Expr(self, node):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute):
            call = node.value
            method_name = call.func.attr
            if isinstance(call.func.value, ast.Name):
                list_name = call.func.value.id
                if list_name == self.target_list_name:
                    if method_name == 'append' and len(call.args) == 1:
                        value = self._extract_value(call.args[0])
                        self.manipulations.append({
                            'type': 'append',
                            'value': value
                        })
                    elif method_name == 'pop':
                        if call.args:
                            index_val = self._extract_value(call.args[0])
                            self.manipulations.append({
                                'type': 'pop',
                                'index': index_val
                            })
                        else:
                            self.manipulations.append({'type': 'pop'})
                    elif method_name == 'remove' and len(call.args) == 1:
                        rm_val = self._extract_value(call.args[0])
                        self.manipulations.append({
                            'type': 'remove',
                            'value': rm_val
                        })
                    elif method_name == 'clear' and not call.args:
                        self.manipulations.append({'type': 'clear'})
                    elif method_name == 'reverse' and not call.args:
                        self.manipulations.append({'type': 'reverse'})
        self.generic_visit(node)


    def visit_While(self, node):
        iteration_count = 0
        while self._eval_condition(node.test):
            iteration_count += 1
            if iteration_count > self.max_iterations:
                print("Warning: possible infinite loop detected, stopping.")
                break
            for stmt in node.body:
                self.visit(stmt)
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)


    def visit_Delete(self, node):
        for target in node.targets:
            if (isinstance(target, ast.Subscript) and
                isinstance(target.value, ast.Name) and
                target.value.id == self.target_list_name):
                index_val = self._extract_index(target.slice)
                if index_val is not None:
                    self.manipulations.append({
                        'type': 'delete',
                        'index': index_val
                    })
        self.generic_visit(node)

    def visit_Subscript(self, node):
        self.generic_visit(node)

    def visit_AugAssign(self, node):
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
                    new_val = old_val / right_val
                elif isinstance(node.op, ast.FloorDiv):
                    new_val = old_val // right_val
                else:
                    new_val = old_val  # Default fallback

                self.env[var_name] = new_val
                self.manipulations.append({
                    'type': 'variable',
                    'name': var_name,
                    'value': new_val
                })
        self.generic_visit(node)

    def _check_for_swap(self, target_tuple, value_tuple):
        if len(target_tuple.elts) == 2 and len(value_tuple.elts) == 2:
            left_sub1, left_sub2 = target_tuple.elts
            right_sub1, right_sub2 = value_tuple.elts
            if (isinstance(left_sub1, ast.Subscript) and 
                isinstance(left_sub1.value, ast.Name) and 
                left_sub1.value.id == self.target_list_name and
                isinstance(left_sub2, ast.Subscript) and 
                isinstance(left_sub2.value, ast.Name) and 
                left_sub2.value.id == self.target_list_name and
                isinstance(right_sub1, ast.Subscript) and 
                isinstance(right_sub1.value, ast.Name) and 
                right_sub1.value.id == self.target_list_name and
                isinstance(right_sub2, ast.Subscript) and 
                isinstance(right_sub2.value, ast.Name) and 
                right_sub2.value.id == self.target_list_name
            ):
                idx1_left = self._extract_index(left_sub1.slice)
                idx2_left = self._extract_index(left_sub2.slice)
                idx1_right = self._extract_index(right_sub1.slice)
                idx2_right = self._extract_index(right_sub2.slice)
                # For a swap: left[0] = right[1], left[1] = right[0]
                if idx1_left == idx2_right and idx2_left == idx1_right:
                    if idx1_left is not None and idx2_left is not None:
                        self.manipulations.append({
                            'type': 'swap',
                            'indices': [idx1_left, idx2_left]
                        })


    def _extract_index(self, node):
        return self._extract_value(node)

    def _extract_value(self, node):
        if isinstance(node, ast.Constant):
            # e.g. a numeric literal
            return node.value

        elif isinstance(node, ast.Name):
            # e.g. i
            if node.id in self.env:
                return self.env[node.id]
            return node.id  # fallback

        elif isinstance(node, ast.BinOp):
            # e.g. i + j, i + 2, ...
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
                    return left_val / right_val
                elif isinstance(node.op, ast.FloorDiv):
                    return left_val // right_val
            return None

        # For more complex expressions (e.g. function calls, etc.), fallback
        return None
    
    def _eval_condition(self, test_node):
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
    tree = ast.parse(python_code)
    visitor = ArrayVisitor()
    visitor.visit(tree)
    return visitor.initial_array, visitor.manipulations


if __name__ == "__main__":
    code_example = """
my_arr = [1, 2, 3]
n = 2

# Outer for loop
for i in range(n):
    my_arr.append(i)
    for j in range(i + 2):
        my_arr.append(i + j)
        n += 1

# Another loop that modifies the list using subscript assignment
for x in range(3):
    my_arr[x] = my_arr[x] * 2

# A tuple assignment swap
my_arr[1], my_arr[2] = my_arr[2], my_arr[1]

# Print final list
print(my_arr)
"""


    init_arr, manips = parse_python_code(code_example)
    print(init_arr)
    print(manips)

    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        exec(code_example, {})
    output = output_buffer.getvalue().strip()

    try:
        final_arr = ast.literal_eval(output)
    except Exception as e:
        final_arr = output

    print(final_arr)
    print(type(final_arr))
