from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/python', methods=['GET'])
def python_api():
    return jsonify({"message": "Hello from Python!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
