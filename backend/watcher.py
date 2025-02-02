import sys

# allow for input code
SAFE_BUILTINS = {
    "range": range,
    "len": len,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list
}

class TrackedList(list):
    def __init__(self, *args, manipulations=None):
        super().__init__(*args)
        self._manipulations = manipulations if manipulations is not None else []

    def append(self, value):
        super().append(value)
        self._manipulations.append({
            "type": "append",
            "value": value,
            "state": self[:]
        })

    def pop(self, index=None):
        if index is None:
            index = len(self) - 1
        popped = super().pop(index)
        self._manipulations.append({
            "type": "pop",
            "index": index,
            "popped": popped,
            "state": self[:]
        })
        return popped

    def __setitem__(self, index, value):
        super().__setitem__(index, value)
        self._manipulations.append({
            "type": "replace",
            "index": index,
            "value": value,
            "state": self[:]
        })

    def insert(self, index, value):
        super().insert(index, value)
        self._manipulations.append({
            "type": "insert",
            "index": index,
            "value": value,
            "state": self[:]
        })

    def remove(self, value):
        super().remove(value)
        self._manipulations.append({
            "type": "remove",
            "value": value,
            "state": self[:]
        })

    def extend(self, iterable):
        super().extend(iterable)
        self._manipulations.append({
            "type": "extend",
            "value": list(iterable),
            "state": self[:]
        })

    def reverse(self):
        super().reverse()
        self._manipulations.append({
            "type": "reverse",
            "state": self[:]
        })

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        self._manipulations.append({
            "type": "sort",
            "args": args,
            "kwargs": kwargs,
            "state": self[:]
        })

class TrackedVariable:
    def __init__(self, name, value, manipulations):
        self.name = name
        self.value = value
        self.manipulations = manipulations

    def __repr__(self):
        return str(self.value)

    def update(self, new_value):
        self.value = new_value
        self.manipulations.append({
            "type": "variable_update",
            "variable": self.name,
            "value": new_value
        })

def normalize_indentation(code_lines):
    if not code_lines:
        return code_lines

    min_indent = float("inf")
    for line in code_lines:
        stripped = line.lstrip()
        if stripped:
            indent_level = len(line) - len(stripped)
            min_indent = min(min_indent, indent_level)

    return [line[min_indent:] if line.strip() else line for line in code_lines]

def extract_initial_array(code_lines):
    initial_arr = []
    arr_name = None

    for line in code_lines:
        if '=' in line and '[' in line and ']' in line:
            try:
                arr_name, arr = line.split("=", 1)
                arr_name = arr_name.strip()
                arr = arr.strip()
                initial_arr = eval(arr)
                if isinstance(initial_arr, list):
                    break  # Stop when list found
            except Exception:
                pass 

    return initial_arr, arr_name

class TrackingDict(dict):
    '''
    intercept assignments to 'arr' and make them type TrackedList
    '''
    def __init__(self, manipulations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manipulations = manipulations

    def __setitem__(self, key, value):
        if key == 'arr' and not isinstance(value, TrackedList) and isinstance(value, list):
            value = TrackedList(value, manipulations=self.manipulations)
        super().__setitem__(key, value)

def run_user_code(code_lines):
    manipulations = []

    initial_arr, arr_name = extract_initial_array(code_lines)
    print(f"Initial Array is: {initial_arr}")

    arr = TrackedList(initial_arr, manipulations=manipulations)

    # needed so all arrays are TrackingLists
    exec_env = TrackingDict(manipulations, **SAFE_BUILTINS)
    exec_env['arr'] = arr

    normalized_code = normalize_indentation(code_lines)
    full_code = "\n".join(normalized_code)

    try:
        exec(full_code, exec_env)
    except Exception as e:
        print(f"Error executing code:\n{full_code}\n{e}")

    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    # Return the original initial array, the final state of 'arr', and the manipulations
    final_arr = exec_env['arr']
    return initial_arr, final_arr[:], manipulations

# TEST
if __name__ == "__main__":
    user_code = [
        "x = 0",
        "while x < 3:",
        "    arr.append(x)",
        "    x += 1",
        "    for i in range(2):",
        "        arr.append(i)",
    ]
    final_arr, manipulations = run_user_code(user_code)
    print("Final Array:", final_arr)
    print("Manipulations:")
    for m in manipulations:
        print(m)