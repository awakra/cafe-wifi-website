from flask import Flask, render_template, redirect, url_for, flash, session
from flask_migrate import Migrate
from models import db, Cafe, User, CafeSuggestion 
from forms import RegisterForm, LoginForm, SuggestCafeForm 
from datetime import datetime, timezone
from functools import wraps # For the admin decorator
import click # For the CLI command
from flask.cli import with_appcontext # For the CLI command

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key' # IMPORTANT: Change this in production
db.init_app(app)
migrate = Migrate(app, db)

@app.context_processor
def inject_current_year():
    """Injects the current year into all templates."""
    return {'now': datetime.now(timezone.utc).year}

# --- Admin Logic ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to access this page.', 'warning')
            return redirect(url_for('login'))
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

@app.cli.command("create-admin")
@with_appcontext
def create_admin_command():
    """Creates a new admin user."""
    email = click.prompt("Admin email")
    name = click.prompt("Admin name")
    password = click.prompt("Admin password", hide_input=True, confirmation_prompt=True)

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        click.echo(f"User with email {email} already exists.")
        if not existing_user.is_admin:
            if click.confirm(f"User {email} exists but is not an admin. Promote to admin?"):
                existing_user.is_admin = True
                db.session.commit()
                click.echo(f"User {email} promoted to admin.")
            else:
                click.echo("Admin creation aborted.")
        else:
            click.echo(f"User {email} is already an admin.")
        return

    new_admin = User(email=email, name=name, is_admin=True)
    # Assumes set_password method is available in User model
    new_admin.set_password(password)
    db.session.add(new_admin)
    db.session.commit()
    click.echo(f"Admin user {name} ({email}) created successfully.")

# --- Routes ---
@app.route('/')
def home():
    cafes = Cafe.query.all()
    return render_template('index.html', cafes=cafes)

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard to view and manage cafes and suggestions."""
    cafes = Cafe.query.all()
    # Fetch all suggestions for the dashboard tabs
    pending_suggestions = CafeSuggestion.query.filter_by(status='pending').all()
    approved_suggestions = CafeSuggestion.query.filter_by(status='approved').all()
    rejected_suggestions = CafeSuggestion.query.filter_by(status='rejected').all()

    return render_template('admin_dashboard.html',
                           cafes=cafes,
                           pending_suggestions=pending_suggestions,
                           approved_suggestions=approved_suggestions,
                           rejected_suggestions=rejected_suggestions)

@app.route('/suggest-cafe', methods=['GET', 'POST'])
def suggest_cafe():
    """Allows logged-in users to suggest a new cafe."""
    if not session.get('user_id'):
        flash('You must be logged in to suggest a cafe.', 'warning')
        return redirect(url_for('login'))

    form = SuggestCafeForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        new_suggestion = CafeSuggestion(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data,
            suggested_by_id=user_id, # Link the suggestion to the user
            status='pending' # Default status
        )
        db.session.add(new_suggestion)
        db.session.commit()
        flash('Your suggestion has been submitted for review!', 'success')
        return redirect(url_for('home')) # Redirect after submission

    return render_template('suggest_cafe.html', form=form)

@app.route('/approve-suggestion/<int:suggestion_id>')
@admin_required
def approve_suggestion(suggestion_id):
    """Admin route to approve a pending cafe suggestion."""
    suggestion = CafeSuggestion.query.get_or_404(suggestion_id)

    if suggestion.status == 'pending':
        # Create a new Cafe entry from the suggestion data
        new_cafe = Cafe(
            name=suggestion.name,
            map_url=suggestion.map_url,
            img_url=suggestion.img_url,
            location=suggestion.location,
            has_sockets=suggestion.has_sockets,
            has_toilet=suggestion.has_toilet,
            has_wifi=suggestion.has_wifi,
            can_take_calls=suggestion.can_take_calls,
            seats=suggestion.seats,
            coffee_price=suggestion.coffee_price
        )
        db.session.add(new_cafe)

        # Update the suggestion status
        suggestion.status = 'approved'
        db.session.commit()

        flash(f'Suggestion "{suggestion.name}" approved and added to cafes!', 'success')
    else:
        flash(f'Suggestion "{suggestion.name}" is not pending.', 'warning')

    return redirect(url_for('admin_dashboard'))

@app.route('/reject-suggestion/<int:suggestion_id>')
@admin_required
def reject_suggestion(suggestion_id):
    """Admin route to reject a pending cafe suggestion."""
    suggestion = CafeSuggestion.query.get_or_404(suggestion_id)

    if suggestion.status == 'pending':
        # Update the suggestion status
        suggestion.status = 'rejected'
        db.session.commit()
        flash(f'Suggestion "{suggestion.name}" rejected.', 'info')
    else:
        flash(f'Suggestion "{suggestion.name}" is not pending.', 'warning')

    return redirect(url_for('admin_dashboard'))

@app.route('/view-suggestion/<int:suggestion_id>')
def view_suggestion(suggestion_id):
    """
    Displays the details of a specific suggestion.
    Accessible by admins or the user who made the suggestion.
    """
    suggestion = CafeSuggestion.query.get_or_404(suggestion_id)
    user_id = session.get('user_id')

    if not user_id:
        flash('You must be logged in to view this page.', 'warning')
        return redirect(url_for('login'))

    current_user = User.query.get(user_id)
    if not current_user: # Should not happen if user_id is valid
        session.clear()
        flash('Invalid session. Please log in again.', 'danger')
        return redirect(url_for('login'))

    # Check if the current user is an admin OR the author of the suggestion
    if not current_user.is_admin and suggestion.suggested_by_id != user_id:
        flash('You do not have permission to view this suggestion.', 'danger')
        return redirect(url_for('home')) # Or 'user_dashboard'

    # Determine which template to render based on admin status
    return render_template('view_suggestion.html', suggestion=suggestion)

@app.route('/add-cafe', methods=['GET', 'POST'])
@admin_required
def add_cafe():
    """Admin route to add a new cafe."""
    form = SuggestCafeForm() # Reusing the suggestion form for adding
    if form.validate_on_submit():
        new_cafe = Cafe(
            name=form.name.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            has_sockets=form.has_sockets.data,
            has_toilet=form.has_toilet.data,
            has_wifi=form.has_wifi.data,
            can_take_calls=form.can_take_calls.data,
            seats=form.seats.data,
            coffee_price=form.coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        flash('Cafe added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_edit_cafe.html', form=form, is_editing=False)

@app.route('/edit-cafe/<int:cafe_id>', methods=['GET', 'POST'])
@admin_required
def edit_cafe(cafe_id):
    """Admin route to edit an existing cafe."""
    cafe = Cafe.query.get_or_404(cafe_id)
    form = SuggestCafeForm(obj=cafe) # Populate form with existing cafe data

    if form.validate_on_submit():
        form.populate_obj(cafe) # Update cafe object with form data
        db.session.commit()
        flash(f'Cafe "{cafe.name}" updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('add_edit_cafe.html', form=form, is_editing=True, cafe_id=cafe.id) # Reuse add_edit_cafe.html

@app.route('/delete-cafe/<int:cafe_id>')
@admin_required
def delete_cafe(cafe_id):
    """Admin route to delete a cafe."""
    cafe_to_delete = Cafe.query.get_or_404(cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    flash(f'Cafe "{cafe_to_delete.name}" deleted successfully!', 'info')
    return redirect(url_for('admin_dashboard'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered. Please log in.", "warning")
            return redirect(url_for('login')) # Redirect to login if email exists

        # By default, new users are not admins
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            is_admin=False # Explicitly set new users as non-admin
        )
        # Assumes set_password method is available in User model
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('login')) # Redirect to login after successful signup
    return render_template('signup.html', form=form)

@app.route('/user-dashboard')
def user_dashboard():
    """Allows logged-in users to view their suggestions and their status."""
    user_id = session.get('user_id')
    if not user_id:
        flash('You must be logged in to view your dashboard.', 'warning')
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    if not user:
        # This case should ideally not happen if user_id is in session
        session.pop('user_id', None)
        session.pop('is_admin', None)
        flash('Your session is invalid. Please log in again.', 'danger')
        return redirect(url_for('login'))

    # Fetch suggestions made by the current user
    user_suggestions = CafeSuggestion.query.filter_by(suggested_by_id=user_id).all()

    pending_suggestions = [s for s in user_suggestions if s.status == 'pending']
    approved_suggestions = [s for s in user_suggestions if s.status == 'approved']
    rejected_suggestions = [s for s in user_suggestions if s.status == 'rejected']

    return render_template('user_dashboard.html',
                           user=user,
                           pending_suggestions=pending_suggestions,
                           approved_suggestions=approved_suggestions,
                           rejected_suggestions=rejected_suggestions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['is_admin'] = user.is_admin # Store admin status in session
            flash('Logged in successfully!', 'success')

            if user.is_admin:
                return redirect(url_for('admin_dashboard')) # Redirect admin to dashboard
            else:
                return redirect(url_for('suggest_cafe')) # Redirect regular user to suggest page
            
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)