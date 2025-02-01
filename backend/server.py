# server.py

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

#! CHANGE ORIGIN ONCE IN PROD
CORS(app, origins="http://localhost:5173", supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    code = request.json.get("code")
    code = clean_code(code)
    
    for line in code:
        print(line)

    
    initial_arr = [1, 2, 3, 4]
    manipulations = [
        { 'type': 'append', 'value': 2 },
        { 'type': 'append', 'value': 3 },
        { 'type': 'swap', 'indices': [0, 2] },
        { 'type': 'replace', 'index': 0, 'value': 4 },
  ] ;
    final_arr = None
    
    return jsonify({
        "message": "manipulations created", 
        "initial_arr": initial_arr,
        "manipulations": manipulations,
        "final_arr": final_arr,
    })
    
def clean_code(code):
    '''
    adds tab chars
    removes empty lines
    '''
    cleaned_code = [line for line in code if line.strip()] # Remove empty lines
    
    #? Maybe do smth with tabs later (use \t)
    return cleaned_code
        
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
