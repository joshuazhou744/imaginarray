from flask import Flask, request, jsonify
from flask_cors import CORS
from watcher import run_user_code
from server_parser import parse_python_code
import io
from contextlib import redirect_stdout
import ast

app = Flask(__name__)


CORS(app, origins="http://localhost:5173", supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code_lines = request.json.get("code")  
    code = "\n".join(code_lines)
    print("Received Code:")
    try:
        initial_arr, manipulations = parse_python_code(code)
    except Exception as e:
        return jsonify({
            "message": "Error during parsing.",
            "error": str(e)
        }), 400
    
    output_buffer = io.StringIO()
    with redirect_stdout(output_buffer):
        try:
            exec(code, {})
        except Exception as e:
            final_output = f"Execution error: {str(e)}"
        else:
            final_output = output_buffer.getvalue().strip()

    try:
        final_arr = ast.literal_eval(final_output)
    except Exception:
        final_arr = final_output 


    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    return jsonify({
        "message": "Analysis complete",
        "initial_arr": initial_arr,
        "manipulations": manipulations,
        "final_arr": final_arr,
    })

def clean_code(code):
    return [line for line in code if line.strip()]  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)