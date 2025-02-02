# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from watcher import run_user_code 
import os
from dotenv import load_dotenv

load_dotenv()


frontend_url = os.getenv("FRONTEND_URL")

app = Flask(__name__)


CORS(app, origins=frontend_url, supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code = request.json.get("code")  
    # code = clean_code(code)  
    # print("Received Code:")
    # for line in code:
    #     print(line)  

    
    initial_arr, final_arr, manipulations, line_nums = run_user_code(code)
    # print(line_nums)
    return jsonify({
        "message": "Analysis complete",
        "initial_arr": initial_arr,  
        "manipulations": manipulations,  
        "final_arr": final_arr,  
        "line_nums": line_nums,  
    })

# def clean_code(code):
#     return [line for line in code if line.strip()]  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)