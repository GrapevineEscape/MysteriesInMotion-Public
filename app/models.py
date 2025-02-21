from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # New fields
    address = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    headshot_path = db.Column(db.String(200))


    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)


class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    kid_friendly = db.Column(db.Boolean, default=False)
    script_path = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    roles = db.relationship('Role', backref='show', cascade="all, delete-orphan")


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)  # M, F, Any
    age = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=False)


class RoleApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    performer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Status: Pending, Approved, Rejected
    applied_at = db.Column(db.DateTime, server_default=db.func.now())

    performer = db.relationship('User', backref='applications')
    show = db.relationship('Show', backref='applications')
    role = db.relationship('Role', backref='applications')


class ShowDate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Draft')  # Draft, Open, Fully Cast, Closed, Canceled
    location = db.Column(db.String(100))
    customer = db.Column(db.String(100))
    attendees = db.Column(db.Integer)
    notes = db.Column(db.Text)
    rehearsals = db.relationship('Rehearsal', backref='show_date', lazy=True, cascade='all, delete-orphan')
    show = relationship('Show', backref='show_dates')


class Rehearsal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_date_id = db.Column(db.Integer, db.ForeignKey('show_date.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text)
    availability = db.relationship('RehearsalAvailability', backref='rehearsal', lazy=True)

    def __repr__(self):
        return f"<Rehearsal {self.date} - {self.location}>"


class RehearsalAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rehearsal_id = db.Column(db.Integer, db.ForeignKey('rehearsal.id'), nullable=False)
    performer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20))  # Available, Unavailable, Partial
    note = db.Column(db.Text)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
