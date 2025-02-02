import sys
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

def run_user_code(code_lines):
    manipulations = []
    arr = TrackedList([1, 2, 3, 4], manipulations=manipulations)

    SAFE_BUILTINS = {
        "range": range,
        "len": len,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list
    }

    exec_env = {
        "arr": arr,
        **SAFE_BUILTINS
    }

    normalized_code = normalize_indentation(code_lines)
    full_code = "\n".join(normalized_code)

    try:
        exec(full_code, {}, exec_env)  
    except Exception as e:
        print(f"Error executing code:\n{full_code}\n{e}")

    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    return arr[:], manipulations
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