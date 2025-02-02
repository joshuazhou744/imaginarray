
import sys
import re

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

        self._last_setitem_call = None

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
    
        old_value = None
        if 0 <= index < len(self):
            old_value = self[index]

       
        if self._last_setitem_call:
            last_index, last_old_value, last_new_value = self._last_setitem_call
 
            if (index != last_index and
                old_value == last_new_value and
                value == last_old_value):
             
                super().__setitem__(index, value)
            
                if self._manipulations and self._manipulations[-1]["type"] == "replace":
                    self._manipulations.pop()
            
                self._manipulations.append({
                    "type": "swap",
                    "indices": [last_index, index],
                    "state": self[:]
                })
                self._last_setitem_call = None
                return

        super().__setitem__(index, value)
        self._manipulations.append({
            "type": "replace",
            "index": index,
            "value": value,
            "state": self[:]
        })

        self._last_setitem_call = (index, old_value, value)

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
            if indent_level < min_indent:
                min_indent = indent_level

    if min_indent == float("inf"):
        return code_lines

    new_lines = []
    for line in code_lines:
        if line.strip():
            new_lines.append(line[min_indent:])
        else:
            new_lines.append(line)
    return new_lines


def extract_initial_array(code_lines):
    """
    Gets the initial values for an array
    Last occurrence of arr init is used
    """
    initial_arr = None
    arr_name = None

    for line in code_lines:
        # whitespace, empty lines, comments
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if '=' in line and '[' in line and ']' in line:
            try:
                left, right = line.split("=", 1)
                left = left.strip()
                
                if '[' not in left and ']' not in left: # ex. we dont want 'arr[i]'
                    candidate = eval(right, SAFE_BUILTINS)
                    if isinstance(candidate, list):
                        initial_arr = candidate
                        arr_name = left
                        
            except Exception:
                continue

    if initial_arr is None:
        initial_arr = []

    return initial_arr, arr_name

class TrackingDict(dict):
    '''
    intercept assignments to 'arr' and make them type TrackedList
    '''
    def __init__(self, manipulations, arr_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manipulations = manipulations
        self.arr_name = arr_name

    def __setitem__(self, key, value):
        if key == self.arr_name and not isinstance(value, TrackedList) and isinstance(value, list):
            value = TrackedList(value, manipulations=self.manipulations)
        super().__setitem__(key, value)

def run_user_code(code_lines):
    manipulations = []

    initial_arr, arr_name = extract_initial_array(code_lines)
    print(f"Initial Array is: {initial_arr}")

    arr = TrackedList(initial_arr, manipulations=manipulations)

    # needed so all arrays are TrackingLists
    exec_env = TrackingDict(manipulations, arr_name, **SAFE_BUILTINS)
    exec_env["arr"] = arr

    normalized = normalize_indentation(code_lines)
    full_code = "\n".join(normalized)


    try:
        exec(full_code, exec_env)
    except Exception as e:
        print(f"Error executing code:\n{full_code}\n{e}")


    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    final_arr = exec_env["arr"]
    return initial_arr, final_arr[:], manipulations


if __name__ == "__main__":
    user_code = [
   
        "arr = [9,8]",
        "arr.append(3)",

        "arr[0], arr[1] = arr[1], arr[0]", 
   
        "arr[1], arr[2] = arr[2], arr[1]",
  
        "arr[0], arr[2] = 999, 777",
   
        "arr = [1,2,3]",
       
        "arr[0], arr[2] = arr[2], arr[0]"
    ]
    init_arr, final, manips = run_user_code(user_code)
    print("Initial Array from code:", init_arr)
    print("Final Array:", final)
    print("All Manipulations:")
    for m in manips:
        print(m)