import sys
import ast
import io
from contextlib import redirect_stdout

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

    def _record_manipulation(self, manipulation_type, **kwargs):
        # Get the caller's frame (2 levels up)
        frame = sys._getframe(2)
        line_no = frame.f_lineno
        kwargs.update({
            "type": manipulation_type,
            "line": line_no,
            "state": list(self)
        })
        self._manipulations.append(kwargs)

    def append(self, value):
        super().append(value)
        self._record_manipulation("append", value=value)

    def pop(self, index=None):
        if index is None:
            index = len(self) - 1
        popped = super().pop(index)
        self._record_manipulation("pop", index=index, popped=popped)
        return popped

    def __setitem__(self, index, value):
        old_value = self[index] if 0 <= index < len(self) else None

        if self._last_setitem_call:
            last_index, last_old_value, last_new_value = self._last_setitem_call
            # Detect a swap pattern: arr[i], arr[j] = arr[j], arr[i]
            if (index != last_index and old_value == last_new_value and value == last_old_value):
                super().__setitem__(index, value)
                if self._manipulations and self._manipulations[-1]["type"] == "replace":
                    self._manipulations.pop()
                self._record_manipulation("swap", indices=[last_index, index])
                self._last_setitem_call = None
                return

        super().__setitem__(index, value)
        self._record_manipulation("replace", index=index, value=value)
        self._last_setitem_call = (index, old_value, value)

    def insert(self, index, value):
        super().insert(index, value)
        self._record_manipulation("insert", index=index, value=value)

    def remove(self, value):
        super().remove(value)
        self._record_manipulation("remove", value=value)

    def extend(self, iterable):
        super().extend(iterable)
        self._record_manipulation("extend", value=list(iterable))

    def reverse(self):
        super().reverse()
        self._record_manipulation("reverse")

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        flattened_args = [repr(a) for a in args]
        flattened_kwargs = {k: repr(v) for k, v in kwargs.items()}
        self._record_manipulation("sort", args=flattened_args, kwargs=flattened_kwargs)

class TrackedVariable:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.manipulations = []

    def update(self, new_value, line_no):
        self.value = new_value
        self.manipulations.append({
            "type": "variable_update",
            "name": self.name,
            "value": new_value,
            "line": line_no
        })

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "manipulations": self.manipulations
        }

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
    initial_arr = None
    arr_name = None
    for line in code_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line and "[" in line and "]" in line:
            try:
                left, right = line.split("=", 1)
                left = left.strip()
                # We avoid subscript assignments (like arr[i])
                if "[" not in left and "]" not in left:
                    candidate = eval(right, SAFE_BUILTINS)
                    if isinstance(candidate, list):
                        initial_arr = candidate
                        arr_name = left
            except Exception:
                continue
    if initial_arr is None:
        initial_arr = []
    return initial_arr, arr_name

def scrub_for_json(obj):
    if isinstance(obj, dict):
        return {k: scrub_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [scrub_for_json(x) for x in obj]
    elif callable(obj):
        return f"<function {obj.__name__}>" if hasattr(obj, "__name__") else str(obj)
    else:
        return obj

class TrackingDict(dict):
    """
    Intercepts assignments. If the key equals the target array name, the value is wrapped as a TrackedList.
    Otherwise, we track variable updates using TrackedVariable objects.
    """
    def __init__(self, manipulations, arr_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.manipulations = manipulations
        self.arr_name = arr_name
        self.tracked_vars = {}  # key: variable name, value: TrackedVariable

    def __setitem__(self, key, value):
        if key == self.arr_name and isinstance(value, list) and not isinstance(value, TrackedList):
            value = TrackedList(value, manipulations=self.manipulations)
            super().__setitem__(key, value)
            return

        old_val = self.get(key, None)
        if old_val != value:
            frame = sys._getframe(1)
            line_no = frame.f_lineno
            if key in self.tracked_vars:
                self.tracked_vars[key].update(value, line_no)
            else:
                tv = TrackedVariable(key, value)
                tv.manipulations.append({
                    "type": "variable",
                    "name": key,
                    "value": value,
                    "line": line_no
                })
                self.tracked_vars[key] = tv
            self.manipulations.append({
                "type": "variable",
                "name": key,
                "value": value,
                "line": line_no
            })
        super().__setitem__(key, value)

def run_user_code(code_lines):
    manipulations = []

    initial_arr, arr_name = extract_initial_array(code_lines)
    print(f"Initial Array is: {initial_arr}")

    arr = TrackedList(initial_arr, manipulations=manipulations)

    exec_env = TrackingDict(manipulations, arr_name, **SAFE_BUILTINS)
    exec_env[arr_name] = arr

    normalized = normalize_indentation(code_lines)
    full_code = "\n".join(normalized)

    try:
        exec(full_code, exec_env)
    except Exception as e:
        print(f"Error executing code:\n{full_code}\n{e}")

    line_nums = [m["line"] for m in manipulations if "line" in m]
    line_nums = scrub_for_json(line_nums)

    variable_manips = [m for m in manipulations if m["type"] == "variable"]
    arr.tracked_vars = {k: v.to_dict() for k, v in exec_env.tracked_vars.items()}

    final_arr = exec_env[arr_name]
    final_arr = list(final_arr)
    sanitized_manipulations = scrub_for_json(manipulations)

    return initial_arr, final_arr, sanitized_manipulations, line_nums

if __name__ == "__main__":
    # Test code using bubble sort with nested loops.
    user_code = [
        "def bubble_sort(arr):",
        "    n = len(arr)",
        "    for i in range(n):",
        "        swapped = False",
        "        for j in range(0, n-i-1):",
        "            if arr[j] > arr[j+1]:",
        "                arr[j], arr[j+1] = arr[j+1], arr[j]",
        "                swapped = True",
        "        if not swapped:",
        "            break",
        "",
        "arr = [64, 34, 25, 12, 22, 11, 90]",
        "bubble_sort(arr)",
        "print(arr)"
    ]
    init_arr, final, manips, line_nums = run_user_code(user_code)
    print("Initial Array from code:", init_arr)
    print("Final Array:", final)
    print("Tracked Variables:", getattr(final, "tracked_vars", {}))
    print("All Manipulations:")
    for m in manips:
        print(m)
