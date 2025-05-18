from flask import Flask, render_template
from models import db, Cafe

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def home():
    cafes = Cafe.query.all()
    return render_template('index.html', cafes=cafes)

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    return "Add Cafe page coming soon!"

if __name__ == '__main__':
    app.run(debug=True)