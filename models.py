from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from database import db
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey, UnicodeText


class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    room = Column(String(80), nullable=False)
    barcode = Column(String(120), unique=True, nullable=False)
    manual_id = Column(Integer, ForeignKey('manual.id'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)

    def __repr__(self):
        return '<Equipment %r>' % self.name

class MaintenanceTask(db.Model):
    __tablename__ = 'maintenance_task'
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    description = Column(String(200), nullable=False)
    next_date = Column(DateTime, nullable=True)
    equipment = relationship('Equipment', backref=backref('maintenance_tasks', lazy=True))
    frequency = Column(String(20))
    occurrence = Column(Integer)
    
    def __repr__(self):
        return '<MaintenanceTask %r>' % self.description

class Manual(db.Model):
    __tablename__ = 'manual'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)

    equipment = relationship('Equipment', backref=backref('manual', uselist=False))

    def __repr__(self):
        return '<Manual %r>' % self.url


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    # Permission Flags use powers of 2
    CAN_ADD_EQUIPMENT = 0x01
    CAN_EDIT_EQUIPMENT = 0x02
    CAN_ADD_MAINTENANCE = 0x04

    # Use an integer to store the combination of permissions
    permissions = Column(Integer)

    @property
    def permission_names(self):
        """Convert permission flags to a list of permission names."""
        perm_flags = [self.CAN_ADD_EQUIPMENT, self.CAN_EDIT_EQUIPMENT, self.CAN_ADD_MAINTENANCE]
        perm_names = ['can_add_equipment', 'can_edit_equipment', 'can.add.maintenance']
        return [name for flag, name in zip(perm_flags, perm_names) if self.permissions & flag]

    def get_permissions(self):
        """Override the get_permissions method."""
        return self.permission_names


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = Column(String(36), primary_key=True) 
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    fs_uniquifier = Column(String(255), nullable=True)
    roles = db.relationship('Role', secondary='roles_users', backref=db.backref('users', lazy='dynamic'))
    
    def has_permission(self, permission):
        if self.roles is None:
            return False
        for role in self.roles:
            if (role.permissions & permission) == permission:
                return True
        return False




class MaintenanceHistory(db.Model):
    __tablename__ = 'maintenance_history'
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    description = Column(String(200), nullable=False)
    completed_date = Column(DateTime, nullable=False)
    equipment = relationship('Equipment', backref=backref('maintenance_history', lazy=True))
    frequency = Column(String(20))
    occurrence = Column(Integer)
    
    def __repr__(self):
        return '<MaintenanceHistory %r>' % self.description
