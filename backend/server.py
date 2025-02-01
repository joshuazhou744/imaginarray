from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

#! CHANGE ORIGIN ONCE IN PROD
CORS(app, origins="http://localhost:5173", supports_credentials=True)

@app.route("/submit_code", methods=["POST"])
def submit_code():
    print(request.json)
    code = request.json.get("code")
    code = clean_code(code)
    
    # for line in code:
    #     print(line)

    
    initial_arr = None
    manipulations = None
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
