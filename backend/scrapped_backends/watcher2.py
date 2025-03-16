
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

    def pop(self, index=-1):
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
            
            if (index != last_index
                and old_value == last_new_value
                and value == last_old_value):
               
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


class ArrDict(dict):
    
    def __init__(self, arr):
        super().__init__()
        self._arr = arr
        self._manipulations = arr._manipulations

        self.update({
            "arr": arr,
            "range": range,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list
        })

    def __setitem__(self, key, value):
        if key == "arr":
            if isinstance(value, list):
                new_tracked = TrackedList(value, manipulations=self._manipulations)
                super().__setitem__(key, new_tracked)
            else:
                super().__setitem__(key, value)
        else:
            super().__setitem__(key, value)


def run_user_code(code_lines):
    manipulations = []
    arr = TrackedList([1,2,3,4], manipulations=manipulations)
    exec_env = ArrDict(arr)
    full_code = "\n".join(code_lines)

    try:
        exec(full_code, {}, exec_env)
    except Exception as e:
        print(f"Error executing code:\n{full_code}\n{e}")

    final_arr = None
    if isinstance(exec_env["arr"], TrackedList):
        final_arr = exec_env["arr"][:]

    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    return final_arr, manipulations


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
    final, manips = run_user_code(user_code)
    print("Final Array:", final)
    print("Manipulations:")
    for m in manips:
        print(m)