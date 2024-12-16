from flask import Flask, render_template

app = Flask(__name__, template_folder="templates")  # Update to use "templates" folder

@app.route('/')
def splash():
    return render_template('index.html')

@app.route('/map')
def map_view():
    return render_template('map.html')  # Make sure map.html is inside the templates folder

if __name__ == '__main__':
    app.run(debug=True)

