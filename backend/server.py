# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from watcher import run_user_code  

app = Flask(__name__)


CORS(app, origins="http://localhost:5173", supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code = request.json.get("code")  
    try:
        initial_arr, final_arr, manipulations, line_nums = run_user_code(code)
        return jsonify({
            "message": "Analysis complete",
            "initial_arr": initial_arr,
            "manipulations": manipulations,
            "final_arr": final_arr,
            "line_nums": line_nums,
        })
    except SyntaxError as e:
        print('error')
        return jsonify({"error": f"Syntax Error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# def clean_code(code):
#     return [line for line in code if line.strip()]  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)