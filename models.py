from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    barcode = db.Column(db.String(120), unique=True, nullable=False)
    manual_id = db.Column(db.Integer, db.ForeignKey('manual.id'), nullable=True)

    def __repr__(self):
        return '<Equipment %r>' % self.name

class MaintenanceTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    next_date = db.Column(db.DateTime, nullable=False)
    equipment = db.relationship('Equipment', backref=db.backref('maintenance_tasks', lazy=True))
    frequency = db.Column(db.String(20))
    occurrence = db.Column(db.Integer)
    
    def __repr__(self):
        return '<MaintenanceTask %r>' % self.description

class Manual(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)

    equipment = db.relationship('Equipment', backref=db.backref('manual', uselist=False))

    def __repr__(self):
        return '<Manual %r>' % self.url
