from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from database import db_session, Base
from flask_security import UserMixin, RoleMixin
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey, UnicodeText


class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    room = Column(String(80), nullable=False)
    barcode = Column(String(120), unique=True, nullable=False)
    manual_id = Column(Integer, ForeignKey('manual.id'), nullable=True)
    is_active = Column(Boolean, default=True, nullable=True)

    def __repr__(self):
        return '<Equipment %r>' % self.name

class MaintenanceTask(Base):
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

class Manual(Base):
    __tablename__ = 'manual'
    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False)

    equipment = relationship('Equipment', backref=backref('manual', uselist=False))

    def __repr__(self):
        return '<Manual %r>' % self.url


class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(UnicodeText)

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(String(36), primary_key=True) 
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    active = Column(Boolean())
    fs_uniquifier = Column(String(255), unique=True, nullable=False)
    fs_uniquifier = Column(String(255), nullable=True)
    roles = relationship('Role', secondary='roles_users', backref=backref('users', lazy='dynamic'))

class MaintenanceHistory(Base):
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
