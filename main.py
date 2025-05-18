from flask import Flask, render_template, redirect, url_for, flash
from models import db, Cafe, User
from forms import RegisterForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a strong secret key!
db.init_app(app)

@app.route('/')
def home():
    cafes = Cafe.query.all()
    return render_template('index.html', cafes=cafes)

@app.route('/add', methods=['GET', 'POST'])
def add_cafe():
    return "Add Cafe page coming soon!"

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('signup'))
        # Create new user
        new_user = User(
            email=form.email.data,
            name=form.name.data
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('home'))  # Or redirect to a login page if you have one
    return render_template('signup.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)