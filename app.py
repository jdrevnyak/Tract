from barcode import Code128
from barcode.writer import ImageWriter
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Equipment, MaintenanceTask
from datetime import date, timedelta
from dateutil.parser import parse as parse_date


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with your own secret key
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/equipment')
    def list_equipment():
        equipment = Equipment.query.all()
        return render_template('list_equipment.html', equipment=equipment)

    @app.route('/equipment/new', methods=['GET', 'POST'])
    def new_equipment():
        if request.method == 'POST':
            name = request.form['name']
            barcode = request.form['barcode']

            # Generate the barcode image and save it
            barcode_image = Code128(barcode, writer=ImageWriter())
            barcode_image.save(f'static/barcodes/{barcode}')
            equipment = Equipment(name=name, barcode=barcode)
            db.session.add(equipment)
            db.session.commit()

            return redirect(url_for('list_equipment'))

        return render_template('new_equipment.html')

    @app.route('/equipment/<int:id>/edit', methods=['GET', 'POST'])
    def edit_equipment(id):
        equipment = Equipment.query.get(id)
        if request.method == 'POST':
            equipment.name = request.form['name']
            db.session.commit()
            return redirect(url_for('list_equipment'))
        return render_template('edit_equipment.html', equipment=equipment)

    @app.route('/equipment/<int:id>', methods=['GET', 'POST'])
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
    def delete_maintenance(id):
        task = MaintenanceTask.query.get(id)
        equipment_id = task.equipment_id
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('view_equipment', id=equipment_id))

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
