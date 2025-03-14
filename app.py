from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from io import StringIO
import contextlib

app = Flask(__name__)
CORS(app) 

@app.route('/api/run', methods=['POST'])
def run_code():
    """Run Python code and return the output or display errors if there are any"""
    data = request.get_json()
    code = data.get('code', '')

    output = StringIO()
    error = None

    #TODO: Implement the code execution
    # with contextlib.redirect_stdout(output):(maybe)
    # try:
    #    exec(code)
    # except Exception as e:
    #     return jsonify({
    #         'status': 'error',
    #         'error': str(e)
    #     })
    
    return jsonify({
        'status': 'success',
        'output': 'test',
        'error': None
    })

# @app.route('/api/analyze', methods=['POST'])
# def analyze_code():
#     """
#     Analyze code without running it.
#     """
#     # Implementation here


# Add code parsing functions here
# def parse_variables(code):
#     """
#     Parse variables from code.
#     """
#     # Implementation here

if __name__ == '__main__':
    app.run(debug=True, port=5000)  