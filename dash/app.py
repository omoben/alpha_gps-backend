from flask import Flask, render_template

app = Flask(__name__, static_folder='static')  # static folder for images, CSS, etc.

@app.route('/')
def splash():
    return render_template('index.html')  # Landing page

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')  # Map interface page

if __name__ == '__main__':
    app.run(debug=True)

