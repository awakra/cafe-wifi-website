from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.context_processor
def inject_year():
    return {'now': datetime.now().year}

@app.route('/')
def home():
    pass

if __name__ == '__main__':
    app.run(debug=True)