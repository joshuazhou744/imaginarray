
example_code = ["for i in range(1,10):" , "*arr.append(10)","*arr.append(7)","hello!", "","arr[i] = arr[j]"]
example_string = "for i in range(1,10):"
example_array = [1,2,3,4,5]

METHODS = {"for":1,"while":2,"append":3,"clear":4,"copy":5,"count":6,"extend":7,"index":8,"insert":9,"pop":10,"remove":11,"reverse":12,"sort":13, "arr":14}
manipulations = []

class Manipulation():
    
    def __init__(self, operation, pointer, array):
        self.operation = operation
        self.pointer = pointer
        self.array = array
    
    def toString(self):
        return(str(self.operation)+str(self.pointer)+str(self.array))


class CodeToArray():

    def __init__(self, operations):
        self.operations = operations
    

    def find_crucial_words(self,array):
        functions = []
        for line in array:
            if any(method in line for method in METHODS):  
                functions.append(line)
        return functions

    
    def create_list(self,initial_array, code):
        self.operations = self.find_crucial_words(code)
        for idx, operation in enumerate(self.operations):
            if("for" in operation):
               self.for_loops(operation,idx)



    def for_loops(self, loop, idx):
        start_idx = loop[loop.find("range(")+ len("range("):loop.find(",")]
        end_idx = loop[loop.find(",")+len(","):loop.find(")")]
        pointer = idx+1
        for i in range(int(start_idx),int(end_idx)):
            if pointer >= len(self.operations):
                return
            if(self.operations[pointer][0]=="*"):
                manipulations.append(Manipulation(self.operations[pointer],1,example_array))
                pointer+=1

            else:
                pointer = idx+1
                i-=1
            
                
        for manipulation in manipulations:
            print(manipulation.toString())
        
        return start_idx,end_idx
        
        

obj = CodeToArray([])
print(obj.create_list(example_array,example_code))
print(obj.find_crucial_words(example_code))
def call_functions():
    pass
