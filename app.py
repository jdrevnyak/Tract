from flask_sqlalchemy import SQLAlchemy
from barcode import Code128
from barcode.writer import ImageWriter
from datetime import date, timedelta
from flask.globals import _app_ctx_stack
import os
from werkzeug.security import check_password_hash
from flask import Flask, render_template_string, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, current_user, login_required, LoginManager
from flask_security import Security, current_user, auth_required, hash_password, SQLAlchemyUserDatastore
from database import db_session, Base, engine, init_db
from flask_migrate import Migrate
from models import Equipment, MaintenanceTask, User, Role
from forms import LoginForm, RegistrationForm, EquipmentForm
from flask_bcrypt import Bcrypt
import uuid
from dotenv import load_dotenv

load_dotenv('flask.env')


def create_app():
    # Create the Flask app
    app = Flask(__name__)

    # Set up your Flask app's secret key and salt
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

    # Initialize SQLAlchemy
    db = SQLAlchemy(app)

    # Initialize extensions inside create_app()
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)

    # Setup Flask-Security-Too
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)

    # Initialize the database schema
    init_db()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)  # No need to convert to int(user_id)

    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)  # No need to convert to int(user_id)


    @app.route('/loginuser', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                # Login and validate the user
                login_user(user)
                flash('Logged in successfully.')

                return redirect(url_for('home'))

        return render_template('login_user.html', form=form)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            # Generate fs_uniquifier using a unique identifier like UUID
            fs_uniquifier = str(uuid.uuid4())

            # Hash the password using bcrypt
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            # Create a new user object with hashed password and save it to the database
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                fs_uniquifier=fs_uniquifier,
                active=True,
                id=fs_uniquifier
            )
            db.session.add(user)
            db.session.commit()

            # Redirect the user to the login page after successful registration
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))

        return render_template('register_user.html', form=form)
        
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def home():
        total_machines = Equipment.query.count()
        total_tasks = MaintenanceTask.query.count()
        total_active_machines = Equipment.query.filter_by(is_active=True).count()
        return render_template('home.html', total_machines=total_machines, total_active_machines=total_active_machines, total_tasks=total_tasks)

    @app.route('/equipment')
    @login_required
    def list_equipment():
        equipment = Equipment.query.all()
        return render_template('list_equipment.html', equipment=equipment)

    @app.route('/equipment/new', methods=['GET', 'POST'])
    @login_required
    def new_equipment():
        form = EquipmentForm(request.form)
        if request.method == 'POST' or form.validate():
            is_active = True
            # Generate the barcode image and save it
            barcode_image = Code128(form.barcode.data, writer=ImageWriter())
            barcode_image.save(f'static/barcodes/{form.barcode.data}')
            equipment = Equipment(name=form.name.data, room=form.room.data, barcode=form.barcode.data, is_active=is_active)
            db.session.add(equipment)
            db.session.commit()

            return redirect(url_for('list_equipment'))

        return render_template('new_equipment.html', form=form)

    @app.route('/equipment/<int:id>/delete', methods=['POST'])
    @login_required
    def delete_equipment(id):
        equipment = Equipment.query.get(id)
        if equipment:
            equipment = db.session.merge(equipment)   # Merge the object into the session
            db.session.delete(equipment)    # Delete the object
            db.session.commit()             # Commit the changes
        return redirect(url_for('list_equipment'))

    @app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_equipment(id):
        equipment = Equipment.query.get(id)
        form = EquipmentForm(obj=equipment)

        if request.method == 'POST' and form.validate():
            form.populate_obj(equipment)  # Update the equipment object with the form data
            db.session.merge(equipment)  # Merge the updated equipment object into the session
            db.session.commit()  # Commit the changes to the database
            flash('Equipment updated successfully.', 'success')
            return redirect(url_for('list_equipment'))

        return render_template('edit_equipment.html', form=form, equipment=equipment)


    @app.route('/equipment/<int:id>', methods=['GET', 'POST'])
    @login_required
    def view_equipment(id):
        equipment = Equipment.query.get(id)
        if equipment is None:
            flash('Equipment not found', 'error')
            return redirect('/equipment')
        if request.method == 'POST':
            description = request.form['description']
            frequency = request.form['frequency']
            today = date.today()
            if frequency != 'one-time':
                occurrence = int(request.form['occurrence'])
                next_date = today + timedelta(days=occurrence)
            else:
                next_date = None
            task = MaintenanceTask(
                equipment_id=equipment.id,
                description=description,
                next_date=next_date,
                frequency=frequency,
                occurrence=occurrence if frequency != 'one-time' else None
            )
            db.session.add(task)
            db.session.commit()
            flash('Maintenance task created successfully', 'success')
            return redirect('/equipment/' + str(id))
        return render_template('view_equipment.html', equipment=equipment)


    @app.route('/equipment/<int:id>/maintenance/new', methods=['GET', 'POST'])
    @login_required
    def new_maintenance(id):
        equipment = Equipment.query.get(id)

        if request.method == 'POST':
            description = request.form['description']
            frequency = request.form['frequency']

            today = date.today()
            if frequency != 'none':
                if frequency == 'daily':
                    occurrence = 1
                elif frequency == 'weekly':
                    occurrence = 7
                elif frequency == 'biweekly':
                    occurrence = 14
                elif frequency == 'monthly':
                    occurrence = 30

                next_date = today + timedelta(days=occurrence)
            else:
                occurrence = None
                next_date = None

            task = MaintenanceTask(equipment_id=id, description=description, next_date=next_date, frequency=frequency, occurrence=occurrence)
            db.session.add(task)
            db.session.commit()

            return redirect(url_for('view_equipment', id=id))

        return render_template('new_maintenance.html', equipment=equipment)


    @app.route('/maintenance/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_maintenance(id):
        task = MaintenanceTask.query.get(id)
        if request.method == 'POST':
            task.description = request.form['description']
            frequency = request.form['frequency']

            today = date.today()
            if frequency != 'none':
                if frequency == 'daily':
                    occurrence = 1
                elif frequency == 'weekly':
                    occurrence = 7
                elif frequency == 'biweekly':
                    occurrence = 14
                elif frequency == 'monthly':
                    occurrence = 30

                next_date = today + timedelta(days=occurrence)
            else:
                occurrence = None
                next_date = None

            task.next_date = next_date
            task.frequency = frequency
            task.occurrence = occurrence

            db.session.commit()
            return redirect(url_for('view_equipment', id=task.equipment_id))

        return render_template('edit_maintenance.html', task=task)


    @app.route('/maintenance/<int:id>/delete', methods=['POST'])
    @login_required
    def delete_maintenance(id):
        task = MaintenanceTask.query.get(id)
        equipment_id = task.equipment_id
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('view_equipment', id=equipment_id))

    return app

    app = create_app()

    if __name__ == '__main__':
        app.run()
