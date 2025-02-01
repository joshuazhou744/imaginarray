from flask import Flask
import json

app = Flask(__name__)


@app.route('/submit-code')
def process_code(code):
    '''
    input: [String] <- each item is a line of code
    return: [] <- all the animations needed
    '''
    print(code)
    return 

# def clean_string(line):
    
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)