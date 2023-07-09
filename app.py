from flask_sqlalchemy import SQLAlchemy
from barcode import Code128
from barcode.writer import ImageWriter
from datetime import date, timedelta, datetime
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
from sqlalchemy.exc import SQLAlchemyError
from flask_bcrypt import Bcrypt
import uuid
import secrets
from dotenv import load_dotenv

load_dotenv('flask.env')

def create_app():
    # Create the Flask app
    app = Flask(__name__)

    # Set up your Flask app's secret key and salt
    app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
    app.config['SECURITY_PASSWORD_SALT'] = os.environ.get("SECURITY_PASSWORD_SALT")
    app.config['SQLALCHEMY_POOL_SIZE'] = 20
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 30

    # Compute the database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'tract.db')
    DATABASE_URL = 'sqlite:///{}'.format(db_path)

    # Configure the database
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

    # Initialize SQLAlchemy
    db = SQLAlchemy(app)


    # Initialize extensions inside create_app()
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)


    # Setup Flask-Security-Too
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security = Security(app, user_datastore)
    
    # # Rehash passwords function
    # def rehash_passwords():
    #     users = User.query.all()
    #     for user in users:
    #         hashed_password = bcrypt.generate_password_hash(user.password).decode('utf-8')
    #         user.password = hashed_password
    #     db.session.commit()
    
    # Initialize the database schema
    init_db()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)  


    @app.route('/loginuser', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Logged in successfully.')

                return redirect(url_for('home'))

        return render_template('login_user.html', form=form)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            fs_uniquifier = str(uuid.uuid4())

            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

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
        
        today = datetime.now().date()
        one_week_from_now = today + timedelta(days=7)

        # Fetch upcoming tasks and order them by next_date
        upcoming_tasks = MaintenanceTask.query.filter(
            MaintenanceTask.next_date >= today,
            MaintenanceTask.next_date <= one_week_from_now
        ).order_by(MaintenanceTask.next_date.asc()).limit(10).all()
        
        return render_template('home.html', total_machines=total_machines, total_active_machines=total_active_machines, total_tasks=total_tasks, upcoming_tasks=upcoming_tasks)
    
    @app.route('/equipment')
    @login_required
    def list_equipment():
        equipment = Equipment.query.all()
        return render_template('list_equipment.html', equipment=equipment)
    
    @app.route('/maintenance')
    @login_required
    def list_maintenance():
        upcoming_tasks = MaintenanceTask.query.order_by(MaintenanceTask.next_date.asc()).all()
        
        return render_template('list_maintenance.html', upcoming_tasks=upcoming_tasks)



    @app.route('/equipment/new', methods=['GET', 'POST'])
    @login_required
    def new_equipment():
        form = EquipmentForm(request.form)
        if request.method == 'POST' or form.validate():
            is_active = True
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
        if not equipment:
            abort(404)
        #Check if there are any maintenance tasks associated with the equipment. Delete them first.
        try:
            maintenance_tasks = MaintenanceTask.query.filter_by(equipment_id=id).all()

            for task in maintenance_tasks:
                merged_task = db.session.merge(task)  
                db.session.delete(merged_task) 

            # Delete the equipment
            merged_equipment = db.session.merge(equipment)  
            db.session.delete(merged_equipment) 
            db.session.commit()

            return redirect(url_for('list_equipment'))
        except SQLAlchemyError as e:
            db.session.rollback()
            return redirect(url_for('list_equipment'))


    @app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_equipment(id):
        equipment = Equipment.query.get(id)
        form = EquipmentForm(obj=equipment)

        if request.method == 'POST' and form.validate():
            form.populate_obj(equipment) 
            db.session.merge(equipment)
            db.session.commit()
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

            frequency_mapping = {'daily': 1, 'weekly': 7, 'biweekly': 14, 'monthly': 30}

            if frequency == 'once':
                once_date = request.form['onceDate']
                task = MaintenanceTask(equipment_id=id, description=description, next_date=once_date, frequency=frequency)
                db.session.add(task)
            elif frequency in frequency_mapping:
                today = date.today()
                for i in range(12):  
                    next_date = today + timedelta(days=frequency_mapping[frequency]*i)
                    task = MaintenanceTask(equipment_id=id, description=description, next_date=next_date, frequency=frequency)
                    db.session.add(task)
            elif frequency == 'none':
                task = MaintenanceTask(equipment_id=id, description=description, next_date=None, frequency=frequency)
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


    @app.route('/maintenance/<int:id>/delete/<string:redirect_route>', methods=['POST'])
    @login_required
    def delete_maintenance(id, redirect_route):
        task = db.session.query(MaintenanceTask).get(id)
        if task:
            equipment_id = task.equipment_id
            db.session.delete(task)
            db.session.commit()
            if redirect_route not in ['home', 'view_equipment']:
                flash('Invalid redirect route, redirecting to home.', 'error')
                return redirect(url_for('home'))
            return redirect(url_for(redirect_route, id=equipment_id) if redirect_route == 'view_equipment' else url_for(redirect_route))
        else:
            flash('Maintenance task not found.', 'error')
            return redirect(url_for('equipment'))


    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        rehash_passwords()
    app.run(host='0.0.0.0')
