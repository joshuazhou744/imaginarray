import re

def parse_data(s, arr):
    s = s.strip()
    if not s:
        return None
    try:
        return eval(s, {"__builtins__": {}}, {"arr": arr, "len": len})
    except:
        return s

def parse_range_expr(expr, arr):
    expr = expr.strip()
    try:
        val = eval(expr, {"__builtins__": {}}, {"arr": arr, "len": len})
        if isinstance(val, int):
            return (0, val, 1)  
        if isinstance(val, tuple):
            if len(val) == 1:
                return (0, val[0], 1)
            elif len(val) == 2:
                return (val[0], val[1], 1)
            elif len(val) == 3:
                return val
        return None
    except:
        return None

class Manipulation:
    def __init__(self, operation="", pointer=0, array=None, data=None, swap=(), replaced=()):
        self.operation = operation
        self.pointer = pointer
        self.array = array if array is not None else []
        self.data = data
        self.swap = swap
        self.replaced = replaced
    def toString(self):
        return (
            str(self.operation)
            + " | Pointer: " + str(self.pointer)
            + " | Array: " + str(self.array)
            + " " + str(self.data)
            + "| Swapped: " + str(self.swap)
            + "| Replaced: " + str(self.replaced)
        )

class CodeToArray:
    def __init__(self, operations, manipulations):
        self.operations = operations
        self.manipulations = manipulations

    def find_crucial_words(self, array):
        functions = []
        for line in array:
            if any(method in line for method in METHODS):
                functions.append(line)
        return functions

    def create_list(self, initial_array, code):
        self.operations = self.find_crucial_words(code)
        self.array_state = initial_array[:]
        for idx, operation in enumerate(self.operations):
            self.perform_operation(operation, idx)
        for manipulation in self.manipulations:
            print(manipulation.toString())
        self.manipulations.clear()

    def for_loops(self, loop, idx):
        content = loop[loop.find("range(") + 6 : loop.rfind(")")]
        rng = parse_range_expr(content, self.array_state)
        if not rng:
            return
        start_idx, end_idx, step = rng
        pointer = idx + 1
        if pointer >= len(self.operations):
            return
        loop_operations = []
        while pointer < len(self.operations) and self.operations[pointer].startswith("*"):
            loop_operations.append(self.operations[pointer])
            pointer += 1

        for i in range(start_idx, end_idx, step):
            for op in loop_operations:
                self.perform_operation(op, i)
        return start_idx, end_idx

    def perform_operation(self, operation, i):
        if "for" in operation and "range(" in operation:
            self.for_loops(operation, i)
        elif "append" in operation and "arr.append" in operation:
            return self.perform_append(operation)
        elif "arr.pop" in operation:
            return self.perform_pop(operation)
        elif "arr.remove" in operation:
            return self.perform_remove(operation)
        elif "arr.insert" in operation:
            return self.perform_insert(operation)
        elif "arr.extend" in operation:
            return self.perform_extend(operation)
        elif "arr.clear" in operation:
            return self.perform_clear(operation)
        elif "arr.reverse" in operation:
            return self.perform_reverse(operation)
        elif "arr.sort" in operation:
            return self.perform_sort(operation)
        elif "arr.copy" in operation:
            return self.perform_copy(operation)
        elif "arr.index" in operation:
            return self.perform_index(operation)
        elif "arr.count" in operation:
            return self.perform_count(operation)
        elif "len(arr" in operation:
            return self.perform_len(operation)
        elif operation.count("arr[") == 4 and "," in operation and "=" in operation:
            return self.perform_swap_expression(operation)
        elif "=" in operation and "arr[" in operation:
            return self.replace(operation, i)
        return None

    def perform_append(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        self.array_state.append(val)
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], val))
        return val

    def perform_pop(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        if content.strip() == "":
            if not self.array_state:
                return "Pop from empty list"
            popped = self.array_state.pop()
            self.manipulations.append(Manipulation(operation, 0, self.array_state[:], popped))
            return popped
        if isinstance(val, int) and 0 <= val < len(self.array_state):
            popped = self.array_state.pop(val)
            self.manipulations.append(Manipulation(operation, 0, self.array_state[:], popped))
            return popped
        return "Index Error"

    def perform_remove(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        if val in self.array_state:
            self.array_state.remove(val)
            self.manipulations.append(Manipulation(operation, 0, self.array_state[:], val))
            return val
        return "Value not found"

    def perform_insert(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        parts = content.split(",", 1)
        if len(parts) < 2:
            return "Invalid insert"
        idx = parse_data(parts[0], self.array_state)
        val = parse_data(parts[1], self.array_state)
        if not isinstance(idx, int):
            return "Index Error"
        if idx < 0:
            idx = 0
        if idx > len(self.array_state):
            idx = len(self.array_state)
        self.array_state.insert(idx, val)
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], val))
        return val

    def perform_extend(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        if isinstance(val, list):
            self.array_state.extend(val)
            self.manipulations.append(Manipulation(operation, 0, self.array_state[:], val))
            return val
        return "Extend requires a list"

    def perform_clear(self, operation):
        self.array_state.clear()
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], None))
        return None

    def perform_reverse(self, operation):
        self.array_state.reverse()
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], None))
        return None

    def perform_sort(self, operation):
        args = operation[operation.find("(")+1 : operation.rfind(")")]
        kw = {}
        if args.strip():
            parts = args.split("=")
            if len(parts) == 2 and parts[0].strip() == "reverse":
                val = parse_data(parts[1], self.array_state)
                if isinstance(val, bool):
                    kw["reverse"] = val
        try:
            self.array_state.sort(**kw)
        except TypeError:
            return "Cannot sort array with incompatible item types"
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], None))
        return None

    def perform_copy(self, operation):
        new_copy = self.array_state[:]
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], new_copy))
        return new_copy

    def perform_index(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        if val in self.array_state:
            idx = self.array_state.index(val)
            self.manipulations.append(Manipulation(operation, 0, self.array_state[:], idx))
            return idx
        return "Value not found"

    def perform_count(self, operation):
        content = operation[operation.find("(")+1 : operation.rfind(")")]
        val = parse_data(content, self.array_state)
        c = self.array_state.count(val)
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], c))
        return c

    def perform_len(self, operation):
        l = len(self.array_state)
        self.manipulations.append(Manipulation(operation, 0, self.array_state[:], l))
        return l

    def replace(self, operation, i):
        left_bracket = operation.find("[") + 1
        right_bracket = operation.find("]")
        left_content = operation[left_bracket:right_bracket]
        left_idx = parse_data(left_content, self.array_state)
        eq = operation.find("=") + 1
        j_start = operation.find("[", eq) + 1
        j_end = operation.find("]", eq)
        right_content = operation[j_start:j_end]
        right_idx = parse_data(right_content, self.array_state)
        if not isinstance(left_idx, int) or not isinstance(right_idx, int):
            return "Index Error"
        if 0 <= left_idx < len(self.array_state) and 0 <= right_idx < len(self.array_state):
            self.array_state[left_idx] = self.array_state[right_idx]
            self.manipulations.append(
                Manipulation(operation, 0, self.array_state[:], None, (), (left_idx, right_idx))
            )
            return self.array_state[left_idx]
        return "Index Error"

    def perform_swap_expression(self, operation):
        left_side, right_side = operation.split("=")
        left_side = left_side.strip()
        right_side = right_side.strip()
        indices = re.findall(r"arr\[(.*?)\]", operation)
        if len(indices) != 4:
            return "Could not parse swap expression (need exactly 4 indices)."
        i_left = parse_data(indices[0], self.array_state)
        j_left = parse_data(indices[1], self.array_state)
        i_right = parse_data(indices[2], self.array_state)
        j_right = parse_data(indices[3], self.array_state)
        if not all(isinstance(x, int) for x in [i_left, j_left, i_right, j_right]):
            return "Index Error"
        if i_left != j_right or j_left != i_right:
            return "Not a symmetrical swap expression."
        if not (0 <= i_left < len(self.array_state) and 0 <= j_left < len(self.array_state)):
            return "Index out of range."
        self.array_state[i_left], self.array_state[j_left] = (
            self.array_state[j_left],
            self.array_state[i_left]
        )
        self.manipulations.append(
            Manipulation(operation, 0, self.array_state[:], None, (i_left, j_left))
        )
        return "Swapped arr["+str(i_left)+"] and arr["+str(j_left)+"]"

METHODS = {
    "for":1,"while":2,"append":3,"clear":4,"copy":5,"count":6,
    "extend":7,"index":8,"insert":9,"pop":10,"remove":11,"reverse":12,
    "sort":13,"arr":14,"len(":15
}

example_code = [
    "arr.append(arr[0]+arr[1]*2+2)",
    "arr[0],arr[1] = arr[1],arr[0]",
    "arr.append('yes')",
    "arr.remove('yes')",
    "arr.insert(0, 'start')",
    "arr.pop(2)",
    "len(arr)",
    "arr.extend([99,100])",
    "arr.reverse()",
    "arr.sort(reverse=True)",
    "arr.count(99)",
    "arr.index(100)",
    "for i in range(2, len(arr), 2):",
    "*arr.append(10)",
    "*arr[0],arr[1] = arr[1], arr[0]",
    "*arr.append(7)",
    "hello!",
    "for j in range(len(arr)-2):",
    "*arr.append(arr[0]%3)",
    "*arr[1] = arr[4]",
    "arr.copy()",
    "arr.clear()"
]

example_array = [1,2,3,4,5]
obj = CodeToArray([], [])
obj.create_list(example_array, example_code)