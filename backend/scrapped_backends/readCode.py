import re
import autopep8


def get_indentation(line):
    """Returns the indentation of a line as a string (spaces or tabs)."""
    match = re.match(r"^(\s*)", line)
    return match.group(1) if match else ""

def edit_code(code_lines):
    """Processes code lines and adds logging statements while preserving indentation."""
    KEYWORDS = ["append", "clear", "extend", "insert", "pop", "remove", "reverse", "sort"]
    modified_lines = []
    
    for i, line in enumerate(code_lines):
        for keyword in KEYWORDS:
            if keyword in line:
                indent = get_indentation(line)
                arr_name = line.split('.')[0].strip()  # ex. arr.append(2)
                statement = f'output.append(f"{i+1}_{keyword}_{{{arr_name}}}")' # i+1 is line_num
                
                modified_lines.append(f'{indent}{statement}')
                modified_lines.append(f'{indent}{line.strip()}')  # Original line
                modified_lines.append(f'{indent}{statement}')
                break
        else:
            modified_lines.append(line)
    
    # Add four spaces of indentation to every non-empty line
    # This ensures proper indentation when the code is placed inside execute_code()
    indented_lines = []
    for line in modified_lines:
        if line.strip():  # If line is not empty
            indented_lines.append('    ' + line)
        else:
            indented_lines.append(line)
            
    return '\n'.join(indented_lines), arr_name

def handle_append(start_arr, end_arr):
    """Handle 'append' operation."""
    if len(end_arr) > len(start_arr):
        return {"type": "append", "value": end_arr[-1]}  # The last appended element
    return None

def handle_insert(start_arr, end_arr):
    """Handle 'insert' operation."""
    for i in range(len(start_arr)):
        if start_arr[i] != end_arr[i]:
            return {"type": "replace", "index": i, "value": end_arr[i]}  # Return replaced value and its index
    return None

def handle_clear(start_arr, end_arr):
    """Handle 'clear' operation."""
    if not end_arr:
        return {"type": "clear"}  # Array is cleared
    return None

def handle_extend(start_arr, end_arr):
    """Handle 'extend' operation."""
    for element in end_arr:
        if element not in start_arr:
            return {"type": "append", "value": element}  # The element added during extension
    return None

def handle_pop(start_arr, end_arr):
    """Handle 'pop' operation."""
    if len(start_arr) > len(end_arr):
        return {"type": "pop"}  # Pop operation
    return None

def handle_remove(start_arr, end_arr):
    """Handle 'remove' operation."""
    for element in start_arr:
        if element not in end_arr:
            return {"type": "remove", "index": start_arr.index(element)}  # The removed element and its index
    return None

def handle_reverse(start_arr, end_arr):
    """Handle 'reverse' operation."""
    if start_arr[::-1] == end_arr:
        return {"type": "reverse"}  # If the array is reversed
    return None

def handle_sort(start_arr, end_arr):
    """Handle 'sort' operation."""
    if sorted(start_arr) == end_arr:
        return {"type": "sort"}  # If the array is sorted
    return None

def create_manipulation(call_list):
    result = []
    line_nums = []
    initial_arr = None
    for i in range(0, len(call_list), 2):
        func_statement = call_list[i]  # ex: "3_append_[1, 0, 2, 3, 0, 3]"
        line_num = func_statement.split('_')[0]
        line_nums.append(line_num)
        
        func_name = func_statement.split('_')[1]  # e.g., 'append', 'insert', etc.
        start_arr = eval(func_statement.split('_')[2])  # Convert the string to an actual list
        
        if i == 0:
            initial_arr = start_arr
            
        # Handle next element in the list if available
        if i + 1 < len(call_list):
            next_func_statement = call_list[i + 1]
            end_arr = eval(next_func_statement.split('_')[2])  # Convert the string to an actual list
        else:
            end_arr = start_arr  # No next element, keep it the same for the last one
        
        # Process based on function name and return the appropriate dictionary
        
        if func_name == 'append':
            value = handle_append(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'insert':
            value = handle_insert(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'clear':
            value = handle_clear(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'extend':
            value = handle_extend(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'pop':
            value = handle_pop(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'remove':
            value = handle_remove(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'reverse':
            value = handle_reverse(start_arr, end_arr)
            if value:
                result.append(value)
        elif func_name == 'sort':
            value = handle_sort(start_arr, end_arr)
            if value:
                result.append(value)
    
    return result, line_nums, initial_arr

def get_final_arr(code_lines,arr_name):
    code = '\n'.join(code_lines) 
    local_scope = {}
    exec(code, {}, local_scope)
    final_arr = local_scope.get(arr_name, [])

    return final_arr

def main(code_lines):
    """Main function that executes the code transformation and runs it."""
    edited_code, arr_name = edit_code(code_lines)
    
    # Create the executable code string
    # Note that edited_code is already properly indented
    code_to_run = f"""
def execute_code():
    output = []
{edited_code}
    return output
"""
    code_to_run = autopep8.fix_code(code_to_run)

    print(code_to_run)
    # Execute the code in a clean namespace
    local_scope = {}
    exec(code_to_run, {}, local_scope)
    out = local_scope.get("execute_code", lambda: [])()

    manipulations, line_nums, initial_arr = create_manipulation(out)
    
    final_arr = get_final_arr(code_lines, arr_name)
    
    return manipulations, line_nums, initial_arr, final_arr