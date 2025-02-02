from flask import Flask, request, jsonify
from flask_cors import CORS
from watcher import run_user_code  

app = Flask(__name__)


CORS(app, origins="http://localhost:5173", supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code = request.json.get("code")  
    code = clean_code(code)  
    print("Received Code:")
    for line in code:
        print(line)  

    
    final_arr, manipulations = run_user_code(code)


    print("\n--- Array Manipulations ---")
    for m in manipulations:
        print(m)
    print("--- End of Manipulations ---\n")

    return jsonify({
        "message": "Analysis complete",
        "initial_arr": [],  
        "manipulations": manipulations,  
        "final_arr": final_arr,  
    })

def clean_code(code):

    return [line for line in code if line.strip()]  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)