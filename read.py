
example_code = ["arr[0],arr[1] = arr[1],arr[0]","arr.append(1)","for i in range(1,10):" , "*arr.append(10)","*arr[0],arr[1] = arr[1], arr[0]","*arr.append(7)","hello!","for j in range(1,5)", "*arr.append(3)","*arr[1] = arr[4]"]
example_string = "for i in range(1,10):"
example_array = [1,2,3,4,5]

METHODS = {"for":1,"while":2,"append":3,"clear":4,"copy":5,"count":6,"extend":7,"index":8,"insert":9,"pop":10,"remove":11,"reverse":12,"sort":13, "arr":14}

import re
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
            self.perform_operation(operation,idx)
        for manipulation in self.manipulations:
            print(manipulation.toString())


        self.manipulations.clear()
    
    
    def for_loops(self, loop, idx):
        start_idx = int(loop[loop.find("range(") + len("range("):loop.find(",")])
        end_idx = int(loop[loop.find(",") + 1:loop.find(")")])
        pointer = idx + 1  
        if pointer >= len(self.operations):  
            return  
        loop_operations = []
        while pointer < len(self.operations) and self.operations[pointer][0] == "*":
            loop_operations.append(self.operations[pointer])
            pointer += 1 
        for i in range(start_idx, end_idx):
            for operation in loop_operations:
                self.perform_operation
                value = self.perform_operation(operation,i)
                
        return start_idx, end_idx
    
    def perform_append(self,operation):
        value = int(operation[operation.find("(") + 1:operation.find(")")])
        self.array_state.append(value)
        self.manipulations.append(Manipulation(operation,0,self.array_state[:],value))
        return value
    
    def replace(self, operation, i):
        try:
            left_bracket = operation.find("[") + 1
            right_bracket = operation.find("]")
            i_index = int(operation[left_bracket:right_bracket])
            equal_sign = operation.find("=") + 1
            j_start = operation.find("[", equal_sign) + 1
            j_end = operation.find("]", equal_sign)
            j_index = int(operation[j_start:j_end])  
            
            if 0 <= i_index < len(self.array_state) and 0 <= j_index < len(self.array_state):
                self.array_state[i_index] = self.array_state[j_index] 
                self.manipulations.append(Manipulation(operation,0,self.array_state[:],0,(),(i_index,j_index))) 
                return self.array_state[i_index]  
            else:
                return "Index Error"
        except:
            return "Invalid Swap"
        

    def perform_operation(self, operation, i):
        
        if "for" in operation:
            self.for_loops(operation, i)
        elif "append" in operation:
            return self.perform_append(operation)
        elif (operation.count("arr[") == 4 
            and "," in operation 
            and "=" in operation):
                return self.perform_swap_expression(operation)
        elif "=" in operation and "arr[" in operation:
            return self.replace(operation, i)
        return None  
    

    def perform_swap_expression(self, operation):

        left_side, right_side = operation.split("=")
        left_side  = left_side.strip()  
        right_side = right_side.strip()  
        indices = re.findall(r"arr\[(\d+)\]", operation)
        if len(indices) != 4:
            return "Could not parse swap expression (need exactly 4 indices)."
        i_left = int(indices[0])  
        j_left = int(indices[1])  
        i_right = int(indices[2]) 
        j_right = int(indices[3]) 

        if i_left != j_right or j_left != i_right:
            return "Not a symmetrical swap expression."

        
        arr_len = len(self.array_state)
        if not (0 <= i_left < arr_len and 0 <= j_left < arr_len):
            return "Index out of range."

        self.array_state[i_left], self.array_state[j_left] = (
            self.array_state[j_left],
            self.array_state[i_left]
        )
        self.manipulations.append(Manipulation(operation,0,self.array_state[:],0,(i_left,j_left)))
        return f"Swapped arr[{i_left}] and arr[{j_left}]"



class Manipulation():
        
    def __init__(self, operation="", pointer=0, array=[], data=0,swap=(),replaced = ()):
            self.operation = operation
            self.pointer = pointer
            self.array = array
            self.data = data
            self.swap = swap
            self.replaced = replaced
    
    def toString(self):
        return str(self.operation) + " | Pointer: " + "0"+ " | Array: " + str(self.array) + " "+ str(self.data)+ "| Swapped: " +str(self.swap)+"| Replaced: " +str(self.replaced)

obj = CodeToArray([],[])

print(obj.create_list(example_array, example_code))
