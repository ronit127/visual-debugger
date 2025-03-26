from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/api/run', methods=['POST'])
def run_code():
    try:
        data = request.get_json()
        code = data.get('code', '')

        
        if code.strip() == "":
            return jsonify({'status': 'error', 'error': 'No code provided'})

        output = f"Processed: {code}"
        return jsonify({'status': 'success', 'output': output})

    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})